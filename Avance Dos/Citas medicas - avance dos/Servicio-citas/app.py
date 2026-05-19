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


# Aqui con este endpoint agendamos citas, se valida que el doctor no tenga otra cita en el mismo horario y se crea la cita si todo es correcto
# Aqui con este endpoint agendamos citas
@app.route("/agendar", methods=["POST"])
def crear_cita():

    print(
        "[SERVICIO-CITAS] Solicitud recibida para crear una cita",
        flush=True
    )

    data = request.get_json()

    # Validar campos obligatorios
    if not data.get("id_paciente_citas") or not data.get("id_doctor_citas"):

        print(
            "[SERVICIO-CITAS] Error: Datos obligatorios faltantes",
            flush=True
        )

        return jsonify({
            "Error": "Los IDs del paciente y doctor son obligatorios"
        }), 400

    paciente = data.get("id_paciente_citas")
    doctor = data.get("id_doctor_citas")
    estado = data.get("estado_citas", "Agendado")
    fecha_cita = data.get("fecha_programacion_citas")
    hora_cita = data.get("hora_programacion_citas")

    # Validar fecha y hora
    if not fecha_cita or not hora_cita:

        print(
            "[SERVICIO-CITAS]Error: Fecha u hora no enviadas",
            flush=True
        )

        return jsonify({
            "Error": "La fecha y hora de la cita son obligatorias"
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        # Validar conflicto de horario
        cursor.execute(
            """
            SELECT id_citas
            FROM citas
            WHERE id_doctor_citas = %s
            AND fecha_programacion_citas = %s
            AND hora_programacion_citas = %s
            AND estado_citas IN ('Agendado', 'Reprogramado')
            """,
            (doctor, fecha_cita, hora_cita)
        )

        cita_existente = cursor.fetchone()

        if cita_existente:

            print(
                "[SERVICIO-CITAS] Horario no disponible para el doctor",
                flush=True
            )

            return jsonify({
                "Error": "El doctor ya tiene una cita agendada en ese horario"
            }), 409

        # Crear cita
        cursor.execute(
            """
            INSERT INTO citas (
                id_paciente_citas,
                id_doctor_citas,
                estado_citas,
                fecha_programacion_citas,
                hora_programacion_citas
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (paciente, doctor, estado, fecha_cita, hora_cita),
        )

        conn.commit()

        print(
            "[SERVICIO-CITAS] Cita creada correctamente",
            flush=True
        )

        return jsonify({
            "mensaje": "Cita creada correctamente"
        }), 201

    except Exception as e:

        print(
            f"[SERVICIO-CITAS] Error al crear la cita: {str(e)}",
            flush=True
        )

        return jsonify({
            "Error": str(e)
        }), 500

    finally:

        print(
            "[SERVICIO-CITAS] Conexión con base de datos cerrada",
            flush=True
        )

        cursor.close()
        conn.close()


# Este es para ver las citas agendadas por usuario osea el paciente xd
@app.route("/citas_paciente", methods=["GET"])
def consultar_citas_paciente():

    print(
        "[SERVICIO-CITAS] Solicitud recibida para consultar citas",
        flush=True
    )

    id_paciente = request.args.get("id_paciente")

    # Validar parámetro obligatorio
    if not id_paciente:

        print(
            "[SERVICIO-CITAS] Error: id_paciente no fue enviado",
            flush=True
        )

        return jsonify({
            "Error": "El id_paciente es obligatorio"
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT 
                id_citas,
                id_paciente_citas,
                id_doctor_citas,
                fecha_programacion_citas,
                hora_programacion_citas,
                estado_citas
            FROM citas
            WHERE id_paciente_citas = %s
            """,
            (id_paciente,),
        )

        citas = cursor.fetchall()

        lista_citas = [
            {
                "id_citas": cita[0],
                "id_paciente": cita[1],
                "id_doctor": cita[2],
                "fecha": str(cita[3]),
                "hora": str(cita[4]),
                "estado": cita[5],
            }
            for cita in citas
        ]

        print(
            "[SERVICIO-CITAS] Consulta de citas realizada correctamente",
            flush=True
        )

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

        print(
            f"[SERVICIO-CITAS] Error al consultar citas: {str(e)}",
            flush=True
        )

        return jsonify({
            "Error": str(e)
        }), 500

    finally:

        print(
            "[SERVICIO-CITAS] Conexión con base de datos cerrada",
            flush=True
        )

        cursor.close()
        conn.close()


# Este endpoint sera el que se conecte con citas para ver disponibilidad.
@app.route("/disponibilidad", methods=["GET"])
def consultar_disponibilidad():

    print(
        "[SERVICIO-CITAS] Solicitud recibida para consultar disponibilidad médica",
        flush=True
    )

    doctor_id = request.args.get("id_doctor")
    fecha = request.args.get("fecha")

    if not doctor_id:

        print(
            "[SERVICIO-CITAS] Error: id_doctor no fue enviado",
            flush=True
        )

        return jsonify({
            "Error": "El parámetro 'id_doctor' es obligatorio"
        }), 400

    try:

        print(
            f"[SERVICIO-CITAS] Validando doctor con ID: {doctor_id}",
            flush=True
        )

        url_auth = f"http://autenticacion:5000/usuarios/{doctor_id}"

        auth_response = requests.get(
            url_auth,
            timeout=2
        )

        if auth_response.status_code == 404:

            print(
                "[SERVICIO-CITAS] Doctor no encontrado en el sistema",
                flush=True
            )

            return jsonify({
                "Error": "El doctor no existe en el sistema"
            }), 404

        datos_medico = auth_response.json()

        if datos_medico.get("rol_usuario") != "Doctor":

            print(
                "[SERVICIO-CITAS] El usuario no tiene rol Doctor",
                flush=True
            )

            return jsonify({
                "Error": "El usuario seleccionado no es un Doctor"
            }), 403

    except requests.exceptions.RequestException as e:

        print(
            f"[SERVICIO-CITAS] Error al conectar con auth: {str(e)}",
            flush=True
        )

        return (
            jsonify({
                "Error": "No se pudo validar la identidad del doctor (Servicio Auth caído)"
            }),
            503,
        )

    if not fecha:
        fecha = str(date.today())

    conn = get_db_connection()
    cursor = conn.cursor()

    try:

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

        sql = """
            SELECT hora_programacion_citas 
            FROM citas 
            WHERE id_doctor_citas = %s 
              AND fecha_programacion_citas = %s 
              AND estado_citas IN ('Agendado', 'Reprogramado')
        """

        cursor.execute(sql, (doctor_id, fecha))

        resultados = cursor.fetchall()

        ocupadas = []

        for r in resultados:

            hora_str = str(r[0])

            if len(hora_str) == 7:
                hora_str = "0" + hora_str

            ocupadas.append(hora_str)

        disponibles = [
            h for h in horarios_posibles
            if h not in ocupadas
        ]

        print(
            f"[SERVICIO-CITAS] Disponibilidad consultada correctamente para el doctor {doctor_id}",
            flush=True
        )

        return (
            jsonify({
                "id_doctor": int(doctor_id),
                "fecha": fecha,
                "total_disponibles": len(disponibles),
                "disponibles": disponibles,
                "ocupadas_detectadas": ocupadas,
            }),
            200,
        )

    except Exception as e:

        print(
            f"[SERVICIO-CITAS] Error al consultar disponibilidad: {str(e)}",
            flush=True
        )

        return jsonify({
            "Error": str(e)
        }), 500

    finally:

        print(
            "[SERVICIO-CITAS] Conexión con base de datos cerrada",
            flush=True
        )

        cursor.close()
        conn.close()

#en este endpoint se cancelan las citas, se actualiza el estado a "Cancelado" y se mantiene el registro para historial
@app.route("/cancelar/<int:id_citas>", methods=["PUT"])
def cancelar_cita(id_citas):

    print(
        "[SERVICIO-CITAS] Solicitud recibida para cancelar una cita",
        flush=True
    )

    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT estado_citas
            FROM citas
            WHERE id_citas = %s
            """,
            (id_citas,)
        )

        cita = cursor.fetchone()

        if not cita:

            print(
                "[SERVICIO-CITAS] Error: La cita no existe",
                flush=True
            )

            return jsonify({
                "Error": "La cita no existe"
            }), 404

        if cita[0] == "Cancelado":

            print(
                "[SERVICIO-CITAS] La cita ya estaba cancelada",
                flush=True
            )

            return jsonify({
                "mensaje": "La cita ya estaba cancelada"
            }), 400

        cursor.execute(
            """
            UPDATE citas
            SET estado_citas = 'Cancelado'
            WHERE id_citas = %s
            """,
            (id_citas,)
        )

        conn.commit()

        print(
            "[SERVICIO-CITAS] Cita cancelada correctamente",
            flush=True
        )

        return jsonify({
            "mensaje": "Cita cancelada correctamente"
        }), 200

    except Exception as e:

        print(
            f"[SERVICIO-CITAS] Error al cancelar cita: {str(e)}",
            flush=True
        )

        return jsonify({
            "Error": str(e)
        }), 500

    finally:

        print(
            "[SERVICIO-CITAS] Conexión con base de datos cerrada",
            flush=True
        )

        cursor.close()
        conn.close()

#en este endpoint se reprograman las citas, se actualiza la fecha, hora y estado a "Reprogramado"
@app.route("/reprogramar/<int:id_citas>", methods=["PUT"])
def reprogramar_cita(id_citas):

    print(
        " [SERVICIO-CITAS] Solicitud recibida para reprogramar una cita",
        flush=True
    )

    data = request.get_json()

    nueva_fecha = data.get("fecha_programacion_citas")
    nueva_hora = data.get("hora_programacion_citas")

    if not nueva_fecha or not nueva_hora:

        print(
            "[SERVICIO-CITAS] Error: Nueva fecha u hora no enviadas",
            flush=True
        )

        return jsonify({
            "Error": "La nueva fecha y hora son obligatorias"
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT id_doctor_citas, estado_citas
            FROM citas
            WHERE id_citas = %s
            """,
            (id_citas,)
        )

        cita = cursor.fetchone()

        if not cita:

            print(
                "[SERVICIO-CITAS] Error: La cita no existe",
                flush=True
            )

            return jsonify({
                "Error": "La cita no existe"
            }), 404

        doctor_id = cita[0]
        estado_actual = cita[1]

        if estado_actual == "Cancelado":

            print(
                "[SERVICIO-CITAS] No se puede reprogramar una cita cancelada",
                flush=True
            )

            return jsonify({
                "Error": "No se puede reprogramar una cita cancelada"
            }), 400

        # Validar conflicto horario
        cursor.execute(
            """
            SELECT id_citas
            FROM citas
            WHERE id_doctor_citas = %s
            AND fecha_programacion_citas = %s
            AND hora_programacion_citas = %s
            AND estado_citas IN ('Agendado', 'Reprogramado')
            AND id_citas != %s
            """,
            (doctor_id, nueva_fecha, nueva_hora, id_citas)
        )

        conflicto = cursor.fetchone()

        if conflicto:

            print(
                "[SERVICIO-CITAS] Horario no disponible para reprogramación",
                flush=True
            )

            return jsonify({
                "Error": "El horario ya está ocupado"
            }), 409

        # Reprogramar cita
        cursor.execute(
            """
            UPDATE citas
            SET fecha_programacion_citas = %s,
                hora_programacion_citas = %s,
                estado_citas = 'Reprogramado'
            WHERE id_citas = %s
            """,
            (nueva_fecha, nueva_hora, id_citas)
        )

        conn.commit()

        print(
            "[SERVICIO-CITAS] Cita reprogramada correctamente",
            flush=True
        )

        return jsonify({
            "mensaje": "Cita reprogramada correctamente"
        }), 200

    except Exception as e:

        print(
            f"[SERVICIO-CITAS] Error al reprogramar cita: {str(e)}",
            flush=True
        )

        return jsonify({
            "Error": str(e)
        }), 500

    finally:

        print(
            "[SERVICIO-CITAS] Conexión con base de datos cerrada",
            flush=True
        )

        cursor.close()
        conn.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
