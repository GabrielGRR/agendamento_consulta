from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DB = "pacientes.db"

def init_db():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    # Adiciona as colunas 'genero' e 'url' e uma restrição para 'genero'
    cursor.execute('''CREATE TABLE IF NOT EXISTS pacientes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL,
                        cpf TEXT NOT NULL,
                        data_nascimento TEXT NOT NULL,
                        telefone TEXT NOT NULL,
                        genero TEXT NOT NULL)''')
    conn.commit()
    conn.close()

@app.route("/pacientes", methods=["GET"])
def listar_pacientes():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pacientes")
    pacientes = cursor.fetchall()
    conn.close()
    # Inclui os novos campos na resposta
    return jsonify([{"id": m[0], "nome": m[1], "cpf": m[2], "data_nascimento": m[3], "telefone": m[4], "genero": m[5]} for m in pacientes])

@app.route("/pacientes/<int:id>", methods=["GET"])
def consultar_paciente(id):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pacientes WHERE id=?", (id,))
    m = cursor.fetchone()
    conn.close()
    if m:
        # Inclui os novos campos na resposta
        # genero = data.get("genero")
        return jsonify({"id": m[0], "nome": m[1], "cpf": m[2], "data_nascimento": m[3], "telefone": m[4], "genero": m[5]})
    return jsonify({"erro": "Paciente não encontrado"}), 404

@app.route("/pacientes", methods=["POST"])
def adicionar_paciente():
    data = request.get_json()
    
    # Valida e define valores padrão
    nome = data.get("nome")
    cpf = data.get("cpf")
    data_nascimento = data.get("data_nascimento")
    telefone = data.get("telefone")
    genero = data.get("genero")
    # url = data.get("url") or PLACEHOLDER_URL_UNKNOWN

    if not all([nome, cpf, data_nascimento, telefone, genero]):
        return jsonify({"erro": "Campos 'nome', 'cpf', 'data_nascimento', 'telefone' e 'genero' são obrigatórios"}), 400

    if genero and genero not in ['M', 'F']:
        return jsonify({"erro": "Campo 'genero' deve ser 'M' ou 'F'"}), 400

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO pacientes (nome, cpf, data_nascimento, telefone, genero) VALUES (?, ?, ?, ?, ?)",
                   (nome, cpf, data_nascimento, telefone, genero))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({"mensagem": "Paciente adicionado com sucesso!", "id": new_id}), 201

@app.route("/pacientes/<int:id>", methods=["PUT"])
def atualizar_paciente(id):
    data = request.get_json()
    if not data:
        return jsonify({"erro": "Requisição sem dados"}), 400

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    # Verifica se o médico existe antes de tentar atualizar
    cursor.execute("SELECT id FROM pacientes WHERE id=?", (id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"erro": "Paciente não encontrado"}), 404

    # Monta a query dinamicamente para permitir atualização parcial
    campos_para_atualizar = []
    valores = []
    campos_permitidos = ["nome", "cpf", "data_nascimento", "telefone", "genero"]

    for campo in campos_permitidos:
        if campo in data:
            if campo == "genero" and data[campo] not in ['M', 'F', None]:
                 conn.close()
                 return jsonify({"erro": "Campo 'genero' deve ser 'M', 'F' ou nulo"}), 400
            campos_para_atualizar.append(f"{campo} = ?")
            valores.append(data[campo])

    if not campos_para_atualizar:
        conn.close()
        return jsonify({"erro": "Nenhum campo válido para atualizar fornecido"}), 400

    valores.append(id)
    query = f"UPDATE pacientes SET {', '.join(campos_para_atualizar)} WHERE id = ?"
    
    cursor.execute(query, tuple(valores))
    conn.commit()
    conn.close()

    return jsonify({"mensagem": "Paciente atualizado com sucesso!"})

@app.route("/pacientes/<int:id>", methods=["DELETE"])
def remover_paciente(id):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    # Verifica se o médico existe antes de tentar remover
    cursor.execute("SELECT id FROM pacientes WHERE id=?", (id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"erro": "Paciente não encontrado"}), 404

    cursor.execute("DELETE FROM pacientes WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return jsonify({"mensagem": "Paciente removido com sucesso!"})


if __name__ == "__main__":
    init_db()
    app.run(port=5000, debug=True)
