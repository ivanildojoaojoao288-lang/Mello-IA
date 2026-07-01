import os
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
import requests
from dotenv import load_dotenv

# 1. CONFIGURAÇÕES
load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'uma_chave_secreta_super_segura'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mello.db' # Use PostgreSQL no Render
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# 2. MODELOS DE DADOS
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_msg = db.Column(db.String(500))
    bot_msg = db.Column(db.String(500))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 3. LÓGICA DE IA (OPENROUTER)
def chamar_ia(pergunta):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}"}
    payload = {
        "model": "meta-llama/llama-3.1-8b-instruct",
        "messages": [{"role": "user", "content": pergunta}]
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        return response.json()['choices'][0]['message']['content']
    except:
        return "Erro de conexão com o sistema neural."

# 4. ROTAS (API)
@app.route('/chat', methods=['POST'])
@login_required
def chat():
    user_message = request.form.get('message')
    bot_reply = chamar_ia(user_message)
    
    # Salva no banco de dados usando o current_user importado
    nova_msg = Message(user_id=current_user.id, user_msg=user_message, bot_msg=bot_reply)
    db.session.add(nova_msg)
    db.session.commit()
    
    return {"resposta": bot_reply}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
