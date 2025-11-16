from flask import Flask, request, jsonify
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash # Importa funções para lidar com senhas de forma segura
#from flasgger import Swagger
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#SWAGGER_YML = os.path.join(BASE_DIR, "swagger.yml")
#swagger = Swagger(app, template_file=SWAGGER_YML)
DB_DIR = "../db"
DB = os.path.join(DB_DIR, "usuarios.db")


def init_db():
    """Inicializa o banco de dados e cria a tabela 'usuarios'."""
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    # Criamos a tabela de usuários com 'username' sendo ÚNICO
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        password_hash TEXT NOT NULL
                    )''')
    conn.commit()
    conn.close()


@app.route("/ping", methods=["GET"])
def ping():
    print("Ping recebido")
    return jsonify({"status": "OK"})

@app.route("/usuarios", methods=["GET"])
def listar_usuarios():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM usuarios")
    usuarios = cursor.fetchall()
    conn.close()
    # Converte para lista de dicionários com apenas id e username
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

    # Gera o hash da senha para armazenamento seguro
    password_hash = generate_password_hash(password)

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    try:
        # Tenta inserir o novo usuário
        cursor.execute("INSERT INTO usuarios (username, password_hash) VALUES (?, ?)",
                       (username, password_hash))
        conn.commit()
        new_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        # Erro caso o 'username' já exista (devido à restrição UNIQUE)
        conn.close()
        return jsonify({"erro": "Este nome de usuário já existe"}), 409  # 409 Conflict
    finally:
        conn.close()

    return jsonify({"mensagem": "Usuário registrado com sucesso!", "id": new_id}), 201


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

    # Busca o usuário pelo username
    cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    # Verifica se o usuário existe E se a senha está correta
    # user[2] é a coluna 'password_hash'
    if user and check_password_hash(user[2], password):
        # Em uma API real, você geraria um token JWT aqui
        return jsonify({"mensagem": "Login bem-sucedido!", "user_id": user[0]})
    else:
        # Resposta genérica para não informar se foi o usuário ou a senha que errou
        return jsonify({"erro": "Credenciais invalidas."}), 401  # 401 Unauthorized


if __name__ == "__main__":
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    init_db()
    app.run(host="0.0.0.0", port=5002, debug=True)