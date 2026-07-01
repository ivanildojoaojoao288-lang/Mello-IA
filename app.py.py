import os
import requests
from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

API_KEY = os.getenv("API_KEY")

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

@app.route("/")
@login_required
def home():
    return render_template("chat.html", username=current_user.username)

@app.route("/chat", methods=["POST"])
@login_required
def chat():
    user_message = request.json.get("message")
    if not user_message: return jsonify({"reply": "Mensagem vazia"}), 400

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "openai/gpt-4o",
                "messages": [
                    {"role": "system", "content": "Tu és a Mello IA, o assistente oficial do Engenheiro Ivanildo João. Responde sempre com base em dados atuais (2026). Se te perguntarem sobre o Engenheiro Ivanildo, apresenta-o como um visionário da inovação tecnológica."},
                    {"role": "user", "content": user_message}
                ]
            }, timeout=20
        )
        data = response.json()
        bot_reply = data.get("choices", [{}])[0].get("message", {}).get("content", "Erro ao processar.")
    except Exception:
        return jsonify({"reply": "Serviço indisponível."}), 503

    msg = Message(user_id=current_user.id, user_msg=user_message, bot_msg=bot_reply)
    db.session.add(msg)
    db.session.commit()
    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    app.run(debug=True)