from ast import If

from flask import Flask, request, jsonify
import mysql.connector
import os

app = Flask(__name__)


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("CITA_DB_HOST"),
        user=os.getenv("CITA_DB_USER"),
        password=os.getenv("CITA_DB_PASSWORD"),
        database=os.getenv("CITA_DB_NAME"),
    )


@app.route("/")
def Inicio():
    return "Servicio de citas funcionando correctamente"


@app.route("/test-db")
def test_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return f"Conexión exitosa bd de citas: {result}"
    except Exception as e:
        return f"Error de conexión: {str(e)}"


@app.route("/agendar", methods=["POST"])
def crear_cita():
    data = request.get_json()

    if not data.get("id_paciente_citas") or not data.get("id_doctor_citas"):
        return jsonify({"Error": "Los IDs del paciente y doctor son obligatorios"}), 400

    paciente = data.get("id_paciente_citas")
    doctor = data.get("id_doctor_citas")
    estado = data.get("estado_citas", "Agendado")
    fecha_cita = data.get("fecha_programacion_citas")
    hora_cita = data.get("hora_programacion_citas")
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO citas (id_paciente_citas, id_doctor_citas, estado_citas, fecha_programacion_citas, hora_programacion_citas) VALUES (%s, %s, %s, %s, %s)",
            (paciente, doctor, estado, fecha_cita, hora_cita),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"mensaje": "Cita creada correctamente"}), 201

    except Exception as e:
        return jsonify({"Error": str(e)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
