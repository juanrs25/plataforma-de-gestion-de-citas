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


# Aqui con este endpoint agendamos citas
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


# Este es para ver las citas agendadas por usuario osea el paciente xd


@app.route("/citas_paciente", methods=["GET"])
def consultar_citas_paciente():
    id_paciente = request.args.get("id_paciente")

    if not id_paciente:
        return jsonify({"Error": "El id_paciente es obligatorio"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT id_paciente_citas, id_doctor_citas, fecha_programacion_citas, hora_programacion_citas, estado_citas FROM citas WHERE id_paciente_citas = %s",
            (id_paciente,),
        )
        citas = cursor.fetchall()

        lista_citas = [
            {
                "id_paciente": cita[0],
                "id_doctor": cita[1],
                "fecha": str(cita[2]),
                "hora": str(cita[3]),
                "estado": cita[4],
            }
            for cita in citas
        ]

        return (
            jsonify(
                {
                    "mensaje": "Consulta de citas del paciente exitosa",
                    "total_citas": len(lista_citas),
                    "citas": lista_citas,
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"Error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# Este endpoint sera el que se conecte con citas para ver disponibilidad.


@app.route("/disponibilidad", methods=["GET"])
def consultar_disponibilidad():

    doctor_id = request.args.get("id_doctor")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if doctor_id:
            cursor.execute(
                "SELECT id_doctor_citas, fecha_programacion_citas, hora_programacion_citas, estado_citas FROM citas WHERE id_doctor_citas = %s",
                (doctor_id,),
            )
        else:
            cursor.execute(
                "SELECT id_doctor_citas, fecha_programacion_citas, hora_programacion_citas, estado_citas FROM citas"
            )

        citas = cursor.fetchall()

        # aqui formamos el json
        lista_ocupados = [
            {
                "id_doctor": cita[0],
                "fecha": str(cita[1]),
                "hora": str(cita[2]),
                "estado": cita[3],
            }
            for cita in citas
        ]

        return (
            jsonify(
                {
                    "mensaje": "Consulta de disponibilidad exitosa",
                    "horarios_ocupados": lista_ocupados,
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"Error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
