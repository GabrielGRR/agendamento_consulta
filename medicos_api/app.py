from flask import Flask, request, jsonify
import sqlite3
import os
import logging
import watchtower
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)
DB_DIR = "../db"
DB = os.path.join(DB_DIR, "medicos.db")

def init_db():
    # Garante que o diretório existe
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    # Adiciona as colunas 'genero' e 'url' e uma restrição para 'genero'
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS medicos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL,
                        crm TEXT NOT NULL,
                        especialidade TEXT NOT NULL,
                        horario TEXT NOT NULL,
                        genero TEXT NOT NULL)"""
    )
    conn.commit()
    conn.close()


@app.route("/ping", methods=["GET"])
def ping():
    logger.info("Ping recebido")
    return jsonify({"status": "OK"})


@app.route("/medicos", methods=["GET"])
def listar_medicos():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medicos")
    medicos = cursor.fetchall()
    conn.close()
    # Inclui os novos campos na resposta
    return jsonify(
        [
            {
                "id": m[0],
                "nome": m[1],
                "crm": m[2],
                "especialidade": m[3],
                "horario": m[4],
                "genero": m[5],
            }
            for m in medicos
        ]
    )


@app.route("/medicos/<int:id>", methods=["GET"])
def consultar_medico(id):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medicos WHERE id=?", (id,))
    m = cursor.fetchone()
    conn.close()
    if m:
        # Inclui os novos campos na resposta
        # genero = data.get("genero")
        return jsonify(
            {
                "id": m[0],
                "nome": m[1],
                "crm": m[2],
                "especialidade": m[3],
                "horario": m[4],
            }
        )
    return jsonify({"erro": "Médico não encontrado"}), 404


@app.route("/medicos", methods=["POST"])
def adicionar_medico():
    data = request.get_json()

    # Valida e define valores padrão
    nome = data.get("nome")
    especialidade = data.get("especialidade")
    horario = data.get("horario")
    genero = data.get("genero")
    crm = data.get("CRM")
    # url = data.get("url") or PLACEHOLDER_URL_UNKNOWN

    if not all([nome, especialidade, horario]):
        return (
            jsonify(
                {"erro": "Campos 'nome', 'especialidade' e 'horario' são obrigatórios"}
            ),
            400,
        )

    if genero and genero not in ["M", "F"]:
        return jsonify({"erro": "Campo 'genero' deve ser 'M' ou 'F'"}), 400

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO medicos (nome, crm, especialidade, horario, genero) VALUES (?, ?, ?, ?, ?)",
        (nome, crm, especialidade, horario, genero),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({"mensagem": "Médico adicionado com sucesso!", "id": new_id}), 201


@app.route("/medicos/<int:id>", methods=["PUT"])
def atualizar_medico(id):
    data = request.get_json()
    if not data:
        return jsonify({"erro": "Requisição sem dados"}), 400

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    # Verifica se o médico existe antes de tentar atualizar
    cursor.execute("SELECT id FROM medicos WHERE id=?", (id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"erro": "Médico não encontrado"}), 404

    # Monta a query dinamicamente para permitir atualização parcial
    campos_para_atualizar = []
    valores = []
    campos_permitidos = ["nome", "crm", "especialidade", "horario", "genero"]

    for campo in campos_permitidos:
        if campo in data:
            if campo == "genero" and data[campo] not in ["M", "F", None]:
                conn.close()
                return (
                    jsonify({"erro": "Campo 'genero' deve ser 'M', 'F' ou nulo"}),
                    400,
                )
            campos_para_atualizar.append(f"{campo} = ?")
            valores.append(data[campo])

    if not campos_para_atualizar:
        conn.close()
        return jsonify({"erro": "Nenhum campo válido para atualizar fornecido"}), 400

    valores.append(id)
    query = f"UPDATE medicos SET {', '.join(campos_para_atualizar)} WHERE id = ?"

    cursor.execute(query, tuple(valores))
    conn.commit()
    conn.close()

    return jsonify({"mensagem": "Médico atualizado com sucesso!"})


@app.route("/medicos/<int:id>", methods=["DELETE"])
def remover_medico(id):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    # Verifica se o médico existe antes de tentar remover
    cursor.execute("SELECT id FROM medicos WHERE id=?", (id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"erro": "Médico não encontrado"}), 404

    cursor.execute("DELETE FROM medicos WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return jsonify({"mensagem": "Médico removido com sucesso!"})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)

# Configura o logger para CloudWatch
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(watchtower.CloudWatchLogHandler(log_group='medicos-api-logs'))

# Exemplo de uso:
logger.info("Aplicação iniciada e log integrado ao CloudWatch")
