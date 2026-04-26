from flask import Flask, request, jsonify
import mysql.connector
import os
import requests
from datetime import date
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
    fecha = request.args.get("fecha")

    if not doctor_id:
        return jsonify({"Error": "El parámetro 'id_doctor' es obligatorio"}), 400

    try:
        # Consultamos al servicio de autenticación
        # Usamos el nombre del contenedor y el puerto interno
        url_auth = f"http://autenticacion:5000/usuarios/{doctor_id}"
        auth_response = requests.get(url_auth, timeout=2)

        if auth_response.status_code == 404:
            return jsonify({"Error": "El doctor no existe en el sistema"}), 404

        datos_medico = auth_response.json()
        if datos_medico.get("rol_usuario") != "Doctor":
            return jsonify({"Error": "El usuario seleccionado no es un Doctor"}), 403

    except requests.exceptions.RequestException:
        # Si el servicio de auth está caído, decidimos si dejar pasar o bloquear
        return (
            jsonify(
                {
                    "Error": "No se pudo validar la identidad del doctor (Servicio Auth caído)"
                }
            ),
            503,
        )
    # -------------------------------------------------

    if not fecha:
        fecha = str(date.today())

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 2. Definir los bloques de tiempo (puedes ajustarlos a tus necesidades)
        # Asegúrate de que el formato sea HH:MM:00 para coincidir con el TIME de MySQL
        horarios_posibles = [
            "08:00:00",
            "08:30:00",
            "09:00:00",
            "09:30:00",
            "10:00:00",
            "10:30:00",
            "11:00:00",
            "11:30:00",
            "14:00:00",
            "14:30:00",
            "15:00:00",
            "15:30:00",
        ]

        # 3. Consultar solo las citas que bloquean la agenda
        # Filtramos por fecha y doctor, ignorando las 'Cancelado'
        sql = """
            SELECT hora_programacion_citas 
            FROM citas 
            WHERE id_doctor_citas = %s 
              AND fecha_programacion_citas = %s 
              AND estado_citas IN ('Agendado', 'Reprogramado')
        """
        cursor.execute(sql, (doctor_id, fecha))

        # Convertimos los objetos timedelta/time a strings tipo '08:30:00'
        resultados = cursor.fetchall()
        ocupadas = []
        for r in resultados:
            # r[0] es el objeto de tiempo; lo convertimos a string limpio
            hora_str = str(r[0])
            # A veces Python devuelve '0:30:00' en lugar de '00:30:00', esto lo corrige:
            if len(hora_str) == 7:
                hora_str = "0" + hora_str
            ocupadas.append(hora_str)

        # 4. Restamos las ocupadas de las posibles
        disponibles = [h for h in horarios_posibles if h not in ocupadas]

        return (
            jsonify(
                {
                    "id_doctor": int(doctor_id),
                    "fecha": fecha,
                    "total_disponibles": len(disponibles),
                    "disponibles": disponibles,
                    "ocupadas_detectadas": ocupadas,  # Útil para debug
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
