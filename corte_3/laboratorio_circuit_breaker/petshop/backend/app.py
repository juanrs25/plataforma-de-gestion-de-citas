from flask import Flask, request, jsonify
import mysql.connector
import os
import requests
import time  # esto para poner tiempo

app = Flask(__name__)


# Funcion para conectarse a una bd
def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )


@app.route("/relacion")
def relacion():
    usuarios = requests.get("http://usuarios:5000/usuarios").json()

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT nombre FROM mascotas")
    mascota = cursor.fetchone()
    connection.close()
    nombre_usuario = usuarios[0]["nombre"] if usuarios else "Sin usuario"
    nombre_mascota = mascota[0] if mascota else "sin mascota"
    return {"usuarios": nombre_usuario, "mascota": nombre_mascota}


@app.route("/")
def home():
    return "api funcionando"


@app.route("/mascotas", methods=["POST"])
def crear_mascotas():
    data = request.json
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO mascotas (nombre, tipo) VALUES (%s,%s)",
        (data["nombre"], data["tipo"]),
    )
    connection.commit()
    connection.close()
    return {"mensaje": "mascota creada"}


@app.route("/mascotas", methods=["GET"])
def listar_mascotas():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM mascotas")
    mascotas = cursor.fetchall()
    connection.close()
    return jsonify(mascotas)
    

# --------
#  RETO GATEWAY
# ---------
@app.route("/mascotas/<int:id>", methods=["GET"])
def obtener_mascota(id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM mascotas WHERE id = %s", (id,))
    mascota = cursor.fetchone()
    connection.close()

    if mascota:
        return jsonify({"id": mascota[0], "nombre": mascota[1], "tipo": mascota[2]})
    else:
        return {"error": "Mascota no encontrada"}, 404


# ---------------------------
# RETO
# ---------------------------


@app.route("/consultaUsuario/<int:id_usuario>")
def consulta_usuario(id_usuario):
    response = requests.get(f"http://usuarios:5000/usuarios/{id_usuario}")
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return {"error": "Usuario no encontrado"}, 404


@app.route("/relacion/<int:id_mascota>")
def consultar_relacion(id_mascota):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT nombre FROM mascotas WHERE id = %s", (id_mascota,))
    mascota = cursor.fetchone()
    connection.close()

    if not mascota:
        return {"error": "Mascota no encontrada"}, 404

    id_dueño = id_mascota
    respuesta = requests.get(f"http://usuarios:5000/usuarios/{id_dueño}")

    if respuesta.status_code == 200:
        dueño = respuesta.json()
        nombre_dueño = dueño["nombre"]
    else:
        nombre_dueño = "Dueño no asignado (ID de usuario no existe)"

    return {
        "mascota": mascota[0],
        "dueño": nombre_dueño,
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
