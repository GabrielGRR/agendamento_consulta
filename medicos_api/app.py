from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DB = "medicos.db"

def init_db():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS medicos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL,
                        especialidade TEXT NOT NULL,
                        horario TEXT NOT NULL)''')
    conn.commit()
    conn.close()

@app.route("/medicos", methods=["GET"])
def listar_medicos():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medicos")
    medicos = cursor.fetchall()
    conn.close()
    return jsonify([{"id": m[0], "nome": m[1], "especialidade": m[2], "horario": m[3]} for m in medicos])

@app.route("/medicos", methods=["POST"])
def adicionar_medico():
    data = request.get_json()
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO medicos (nome, especialidade, horario) VALUES (?, ?, ?)",
                   (data["nome"], data["especialidade"], data["horario"]))
    conn.commit()
    conn.close()
    return jsonify({"mensagem": "Médico adicionado com sucesso!"})

@app.route("/medicos/<int:id>", methods=["GET"])
def consultar_medico(id):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medicos WHERE id=?", (id,))
    m = cursor.fetchone()
    conn.close()
    if m:
        return jsonify({"id": m[0], "nome": m[1], "especialidade": m[2], "horario": m[3]})
    return jsonify({"erro": "Médico não encontrado"}), 404
print("Iniciando servidor Flask...")

if __name__ == "__main__":
    init_db()
    app.run(port=5001, debug=True)
