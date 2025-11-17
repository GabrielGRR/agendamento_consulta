from flask import Flask, request, jsonify
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from functools import wraps
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Chave secreta para assinar os tokens JWT
# IMPORTANTE: Em produção, use uma variável de ambiente e uma chave forte
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sua-chave-secreta-super-segura-aqui')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = "../db"
DB = os.path.join(DB_DIR, "usuarios.db")


def init_db():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        password_hash TEXT NOT NULL
                    )''')
    conn.commit()
    conn.close()


def criar_token(user_id, username):
    """Cria um token JWT para o usuário."""
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=1),  # Token expira em 1 hora
        'iat': datetime.utcnow()  # Timestamp de emissão
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token


def verificar_token(f):
    """Decorator para proteger rotas que precisam de autenticação."""

    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Procura o token no header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                # Formato esperado: "Bearer <token>"
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({"erro": "Formato de token inválido"}), 401

        if not token:
            return jsonify({"erro": "Token não fornecido"}), 401

        try:
            # Decodifica e verifica o token
            dados = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            request.user_id = dados['user_id']
            request.username = dados['username']
        except jwt.ExpiredSignatureError:
            return jsonify({"erro": "Token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"erro": "Token inválido"}), 401

        return f(*args, **kwargs)

    return decorated


@app.route("/ping", methods=["GET"])
def ping():
    print("Ping recebido")
    return jsonify({"status": "OK"})


@app.route("/usuarios", methods=["GET"])
@verificar_token  # Agora essa rota é protegida
def listar_usuarios():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM usuarios")
    usuarios = cursor.fetchall()
    conn.close()

    usuarios_list = [{"id": usuario[0], "username": usuario[1]} for usuario in usuarios]
    return jsonify(usuarios_list)


@app.route("/register", methods=["POST"])
def register_user():
    """Rota para registrar um novo usuário."""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"erro": "Usuário e senha são obrigatórios"}), 400

    # Validação básica de senha
    if len(password) < 6:
        return jsonify({"erro": "A senha deve ter no mínimo 6 caracteres"}), 400

    password_hash = generate_password_hash(password)

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO usuarios (username, password_hash) VALUES (?, ?)",
                       (username, password_hash))
        conn.commit()
        new_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"erro": "Este nome de usuário já existe"}), 409
    finally:
        conn.close()

    # Cria um token automaticamente após o registro
    token = criar_token(new_id, username)

    return jsonify({
        "mensagem": "Usuário registrado com sucesso!",
        "id": new_id,
        "token": token
    }), 201


@app.route("/login", methods=["POST"])
def login_user():
    """Rota para autenticar (fazer login) um usuário."""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"erro": "Usuário e senha são obrigatórios"}), 400

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[2], password):
        # Cria o token JWT
        token = criar_token(user[0], user[1])

        return jsonify({
            "mensagem": "Login bem-sucedido!",
            "user_id": user[0],
            "username": user[1],
            "token": token
        }), 200
    else:
        return jsonify({"erro": "Credenciais inválidas"}), 401


@app.route("/perfil", methods=["GET"])
@verificar_token  # Rota protegida - requer token
def get_perfil():
    """Retorna informações do usuário autenticado."""
    return jsonify({
        "user_id": request.user_id,
        "username": request.username,
        "mensagem": "Você está autenticado!"
    })


@app.route("/verificar-token", methods=["GET"])
@verificar_token
def verificar_token_valido():
    """Verifica se o token é válido."""
    return jsonify({
        "valido": True,
        "user_id": request.user_id,
        "username": request.username
    })


if __name__ == "__main__":
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    init_db()
    app.run(host="0.0.0.0", port=5002, debug=True)