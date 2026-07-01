from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import logging

# Configuração de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instância da aplicação (O Gunicorn procura exatamente esta variável 'app')
app = Flask(__name__)

# Configuração do Banco de Dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de Utilizador
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Inicialização do Banco (com contexto para evitar erros de deploy)
with app.app_context():
    db.create_all()
    logger.info("Banco de dados pronto.")

# Rota de teste simples para verificar se o Gunicorn sobe
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Online", "criador": "Engenheiro Ivanildo"})

# Rota de login básica para teste
@app.route("/login", methods=["POST"])
def login():
    return jsonify({"message": "Endpoint de login ativo"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
