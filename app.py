import os
import requests
from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
# Importações para segurança de senha
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# 🔐 SECRET
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")

# 🗄️ DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 🔑 LOGIN
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

API_KEY = os.getenv("API_KEY")


# 👤 USER
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)  # Aumentado para suportar o hash


# 💬 MESSAGE
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Definido explicitamente como ForeignKey
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_msg = db.Column(db.Text, nullable=False)
    bot_msg = db.Column(db.Text, nullable=False)


@login_manager.user_loader
def load_user(user_id):
    # db.session.get() é a sintaxe moderna recomendada pelo SQLAlchemy
    return db.session.get(User, int(user_id))


@app.route("/")
@login_required
def home():
    return render_template("chat.html", username=current_user.username)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Verifica se o usuário já existe
        if User.query.filter_by(username=username).first():
            return "Usuário já existe!", 400

        # Gera o hash seguro da senha
        hashed_password = generate_password_hash(password)

        user = User(
            username=username,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()

        # Compara o hash da senha enviada com o hash salvo no banco
        if user and check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect("/")
            
        return "Login inválido", 401

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")


# 🤖 CHAT IA
@app.route("/chat", methods=["POST"])
@login_required
def chat():
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"reply": "Mensagem vazia"}), 400

    if not API_KEY:
        return jsonify({"reply": "API Key não configurada no servidor"}), 500

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {"role": "user", "content": user_message}
                ]
            },
            timeout=10 # Evita que sua aplicação trave se a API demorar a responder
        )

        # Trata erros de requisição externa
        if response.status_code != 200:
            return jsonify({"reply": f"Erro na API externa (Status {response.status_code})"}), 502

        data = response.json()
        bot_reply = data.get("choices", [{}])[0].get("message", {}).get("content", "Sem resposta da IA")

    except requests.exceptions.RequestException:
        return jsonify({"reply": "Falha na comunicação com o provedor de IA."}), 503

    # Salva no banco de dados após sucesso
    msg = Message(
        user_id=current_user.id,
        user_msg=user_message,
        bot_msg=bot_reply
    )
    db.session.add(msg)
    db.session.commit()

    return jsonify({"reply": bot_reply})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)