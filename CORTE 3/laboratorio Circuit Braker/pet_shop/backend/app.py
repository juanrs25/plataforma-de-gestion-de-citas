from flask import Flask, request, jsonify
import mysql.connector
import os
import requests

app = Flask(__name__)

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


@app.route("/")
def home():
    return "API FUNCIONANDO"

@app.route("/mascotas", methods=["POST"])
def crear_mascota():
    data = request.json
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO mascotas (nombre, tipo) VALUES (%s, %s)",
        (data["nombre"], data["tipo"])
    )
    connection.commit()
    connection.close()
    return {"mensaje": "mascota creada"}

@app.route("/mascotas/<int:id_mascota>", methods=["GET"])
def obtener_mascota(id_mascota):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT id, nombre, tipo FROM mascotas WHERE id = %s",
        (id_mascota,)
    )
    mascota = cursor.fetchone()
    connection.close()

    if not mascota:
        return {"error": "Mascota no encontrada"}, 404

    id_m, nombre, tipo = mascota
    return jsonify({"id": id_m, "nombre": nombre, "tipo": tipo})

@app.route("/mascotas", methods=["GET"])
def listar_mascotas():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM mascotas")
    mascotas = cursor.fetchall()
    connection.close()
    return jsonify(mascotas)

@app.route("/usuarios", methods=["GET"])
def obtener_usuarios():
    try:
        response = requests.get("http://usuarios:5000/usuarios")
        return jsonify(response.json())
    except:
        return {"error": "No se pudo conectar con el servicio de usuarios"}, 500


@app.route("/usuarios/<int:id_usuario>", methods=["GET"])
def obtener_usuario(id_usuario):
    try:
        response = requests.get(f"http://usuarios:5000/usuarios/{id_usuario}")
        
        if response.status_code != 200:
            return {"error": "Usuario no encontrado"}, 404

        return jsonify(response.json())
    except:
        return {"error": "Error de conexión"}, 500

@app.route("/relacion/<int:id_mascota>", methods=["GET"])
def relacion(id_mascota):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, nombre, tipo, usuario_id FROM mascotas WHERE id=%s",
        (id_mascota,)
    )
    mascota = cursor.fetchone()

    connection.close()

    if not mascota:
        return {"error": "Mascota no encontrada"}, 404

    id_m, nombre, tipo, usuario_id = mascota

    # consultar usuario en otro microservicio
    usuario = requests.get(f"http://usuarios:5000/usuarios/{usuario_id}")

    if usuario.status_code != 200:
        return {"error": "Usuario no encontrado"}, 404

    return {
        "mascota": {
            "id": id_m,
            "nombre": nombre,
            "tipo": tipo
        },
        "usuario": usuario.json()
    }



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)