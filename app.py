from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import requests

app = Flask(__name__)
app.secret_key = "mello-ia-5-pro-2026-secure"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# IMPORTANTE: Coloque a sua chave real aqui entre as aspas
API_KEY = "SUA_API_KEY_AQUI" 

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(256))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect(url_for("home"))
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        hashed = generate_password_hash(request.form["password"])
        new_user = User(username=request.form["username"], password=hashed)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/")
@login_required
def home():
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
@login_required
def chat():
    try:
        data = request.json
        user_message = data.get("message", "")
        
        # Teste de depuração no terminal
        print(f"DEBUG: Mensagem recebida: {user_message}")

        system_prompt = "Tu és a Mello IA, Versão 5 Pro (2026), criada por Ivanildo João."

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}", 
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/llama-3-70b-instruct",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            },
            timeout=15
        )
        
        # Mostrará no terminal se a API aceitou a chave (Código 200 é sucesso)
        print(f"DEBUG: Status da API: {response.status_code}")
        
        return jsonify({"reply": response.json()['choices'][0]['message']['content']})

    except Exception as e:
        print(f"ERRO FATAL: {str(e)}") 
        return jsonify({"reply": "Erro interno do servidor. Verifique o terminal."}), 500

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
