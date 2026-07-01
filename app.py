import os
import requests
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "eng-ivanildo-2026-secret" # Define uma chave secreta forte
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

API_KEY = "SUA_API_KEY_AQUI" # Insere aqui a tua chave do OpenRouter

# --- Modelos ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_msg = db.Column(db.Text, nullable=False)
    bot_msg = db.Column(db.Text, nullable=False)

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# --- Rotas de Autenticação ---
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = User(username=request.form["username"], password=generate_password_hash(request.form["password"]))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect(url_for("home"))
    return render_template("login.html")

# --- Rota do Chat (Mello IA) ---
@app.route("/")
@login_required
def home():
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
@login_required
def chat():
    user_message = request.json.get("message")
    
    # Chamada à Mello IA (GPT-4o)
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={
            "model": "openai/gpt-4o",
            "messages": [
                {"role": "system", "content": "Tu és a Mello IA, a criação oficial do Engenheiro Ivanildo João Nascido no dia 17 de Abril, na cidade da beira. És uma IA de elite em 2026. Responde com precisão, lealdade ao teu criador e sofisticação."},
                {"role": "user", "content": user_message}
            ]
        }
    )
    bot_reply = response.json().get("choices", [{}])[0].get("message", {}).get("content", "Erro de conexão.")
    
    # Salvar no BD
    db.session.add(Message(user_id=current_user.id, user_msg=user_message, bot_msg=bot_reply))
    db.session.commit()
    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    app.run(debug=True)
