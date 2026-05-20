from flask import Flask, request, jsonify
import mysql.connector
import os
import requests
from datetime import date
import pika
import json

app = Flask(__name__)


# CONFIGURACION DE BASE DE DATOS


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("CITA_DB_HOST"),
        user=os.getenv("CITA_DB_USER"),
        password=os.getenv("CITA_DB_PASSWORD"),
        database=os.getenv("CITA_DB_NAME"),
    )


# LOGICA DE RABBITMQ


def publicar_evento(id_usuario, id_cita, accion, detalles=""):
    try:
        rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
        conexion = pika.BlockingConnection(
            pika.ConnectionParameters(host=rabbitmq_host)
        )
        canal = conexion.channel()

        # Declaramos ambas colas para asegurar que existan en RabbitMQ
        canal.queue_declare(queue="eventos_citas", durable=True)
        canal.queue_declare(queue="eventos_notificaciones", durable=True)

        evento = {
            "id_usuario": id_usuario,
            "id_cita": id_cita,
            "accion": accion,
            "detalles": detalles,
        }
        mensaje_json = json.dumps(evento)

        # Envio a la cola de Historial
        canal.basic_publish(
            exchange="",
            routing_key="eventos_citas",
            body=mensaje_json,
            properties=pika.BasicProperties(
                delivery_mode=2,
            ),
        )

        # Envio a la cola de Notificaciones
        canal.basic_publish(
            exchange="",
            routing_key="eventos_notificaciones",
            body=mensaje_json,
            properties=pika.BasicProperties(
                delivery_mode=2,
            ),
        )

        print(
            f"[SERVICIO-CITAS] [RABBITMQ] Evento  disparado disparado tambien a: {accion} para la cita {id_cita}",
            flush=True,
        )
        conexion.close()
    except Exception as e:
        print(
            f"[SERVICIO-CITAS] [RABBITMQ-ERROR] Error al publicar evento en RabbitMQ: {str(e)}",
            flush=True,
        )


# ENDPOINTS ----------------------------------------------------------------------------


@app.route("/")
def Inicio():
    print("[SERVICIO-CITAS] Solicitud recibida en endpoint raíz (/)", flush=True)
    return "Servicio de citas funcionando correctamente"


@app.route("/test-db")
def test_db():
    print(
        "[SERVICIO-CITAS] Solicitud recibida para prueba de base de datos (/test-db)",
        flush=True,
    )
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        print("[SERVICIO-CITAS] Prueba de BD exitosa", flush=True)
        return f"Conexión exitosa bd de citas: {result}"
    except Exception as e:
        print(f"[SERVICIO-CITAS] Error en prueba de BD: {str(e)}", flush=True)
        return f"Error de conexión: {str(e)}"


@app.route("/agendar", methods=["POST"])
def crear_cita():
    print(
        "[SERVICIO-CITAS] Solicitud recibida para crear una cita (/agendar)", flush=True
    )
    data = request.get_json()

    if not data.get("id_paciente_citas") or not data.get("id_doctor_citas"):
        print("[SERVICIO-CITAS] Error: Datos obligatorios faltantes (IDs)", flush=True)
        return jsonify({"Error": "Los IDs del paciente y doctor son obligatorios"}), 400

    paciente = data.get("id_paciente_citas")
    doctor = data.get("id_doctor_citas")
    estado = data.get("estado_citas", "Agendado")
    fecha_cita = data.get("fecha_programacion_citas")
    hora_cita = data.get("hora_programacion_citas")

    if not fecha_cita or not hora_cita:
        print("[SERVICIO-CITAS] Error: Fecha u hora no enviadas", flush=True)
        return jsonify({"Error": "La fecha y hora de la cita son obligatorias"}), 400

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
            (doctor, fecha_cita, hora_cita),
        )

        cita_existente = cursor.fetchone()

        if cita_existente:
            print("[SERVICIO-CITAS] Horario no disponible para el doctor", flush=True)
            return (
                jsonify(
                    {"Error": "El doctor ya tiene una cita agendada en ese horario"}
                ),
                409,
            )

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
        id_nueva_cita = cursor.lastrowid

        print(
            f"[SERVICIO-CITAS] Cita {id_nueva_cita} creada correctamente en BD",
            flush=True,
        )

        # DISPARAMOS EL EVENTO
        publicar_evento(
            id_usuario=paciente,
            id_cita=id_nueva_cita,
            accion="CITA AGENDADA",
            detalles=f"Cita programada para el {fecha_cita} a las {hora_cita}",
        )

        return (
            jsonify({"mensaje": "Cita creada correctamente", "id_cita": id_nueva_cita}),
            201,
        )

    except Exception as e:
        print(f"[SERVICIO-CITAS] Error al crear la cita: {str(e)}", flush=True)
        return jsonify({"Error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route("/citas_paciente", methods=["GET"])
def consultar_citas_paciente():
    print(
        "[SERVICIO-CITAS] Solicitud recibida para consultar citas de paciente (/citas_paciente)",
        flush=True,
    )
    id_paciente = request.args.get("id_paciente")

    if not id_paciente:
        print("[SERVICIO-CITAS] Error: id_paciente no fue enviado", flush=True)
        return jsonify({"Error": "El id_paciente es obligatorio"}), 400

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
            f"[SERVICIO-CITAS] Consulta de citas realizada correctamente. Total: {len(lista_citas)}",
            flush=True,
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
        print(f"[SERVICIO-CITAS] Error al consultar citas: {str(e)}", flush=True)
        return jsonify({"Error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route("/disponibilidad", methods=["GET"])
def consultar_disponibilidad():
    print(
        "[SERVICIO-CITAS] Solicitud recibida para consultar disponibilidad médica (/disponibilidad)",
        flush=True,
    )
    doctor_id = request.args.get("id_doctor")
    fecha = request.args.get("fecha")

    if not doctor_id:
        print("[SERVICIO-CITAS] Error: id_doctor no fue enviado", flush=True)
        return jsonify({"Error": "El parámetro 'id_doctor' es obligatorio"}), 400

    try:
        print(
            f"[SERVICIO-CITAS] Validando doctor con ID: {doctor_id} en servicio Auth",
            flush=True,
        )
        url_auth = f"http://autenticacion:5000/usuarios/{doctor_id}"
        auth_response = requests.get(url_auth, timeout=2)

        if auth_response.status_code == 404:
            print(
                f"[SERVICIO-CITAS] Doctor ID {doctor_id} no encontrado en el sistema Auth",
                flush=True,
            )
            return jsonify({"Error": "El doctor no existe en el sistema"}), 404

        datos_medico = auth_response.json()
        if datos_medico.get("rol_usuario") != "Doctor":
            print(
                f"[SERVICIO-CITAS] El usuario ID {doctor_id} no tiene rol Doctor",
                flush=True,
            )
            return jsonify({"Error": "El usuario seleccionado no es un Doctor"}), 403

    except requests.exceptions.RequestException as e:
        print(
            f"[SERVICIO-CITAS] Error al conectar con servicio Auth: {str(e)}",
            flush=True,
        )
        return (
            jsonify(
                {
                    "Error": "No se pudo validar la identidad del doctor (Servicio Auth caído)"
                }
            ),
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

        disponibles = [h for h in horarios_posibles if h not in ocupadas]
        print(
            f"[SERVICIO-CITAS] Disponibilidad consultada correctamente para el doctor {doctor_id} en fecha {fecha}",
            flush=True,
        )

        return (
            jsonify(
                {
                    "id_doctor": int(doctor_id),
                    "fecha": fecha,
                    "total_disponibles": len(disponibles),
                    "disponibles": disponibles,
                    "ocupadas_detectadas": ocupadas,
                }
            ),
            200,
        )

    except Exception as e:
        print(
            f"[SERVICIO-CITAS] Error al consultar disponibilidad: {str(e)}", flush=True
        )
        return jsonify({"Error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route("/cancelar/<int:id_citas>", methods=["PUT"])
def cancelar_cita(id_citas):
    print(
        f"[SERVICIO-CITAS] Solicitud recibida para cancelar la cita ID {id_citas} (/cancelar)",
        flush=True,
    )
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT estado_citas, id_paciente_citas
            FROM citas
            WHERE id_citas = %s
            """,
            (id_citas,),
        )
        cita = cursor.fetchone()

        if not cita:
            print(
                f"[SERVICIO-CITAS] Error: La cita ID {id_citas} no existe", flush=True
            )
            return jsonify({"Error": "La cita no existe"}), 404

        estado_actual = cita[0]
        id_paciente = cita[1]

        if estado_actual == "Cancelado":
            print(
                f"[SERVICIO-CITAS] La cita ID {id_citas} ya estaba cancelada",
                flush=True,
            )
            return jsonify({"mensaje": "La cita ya estaba cancelada"}), 400

        cursor.execute(
            """
            UPDATE citas
            SET estado_citas = 'Cancelado'
            WHERE id_citas = %s
            """,
            (id_citas,),
        )
        conn.commit()

        print(
            f"[SERVICIO-CITAS] Cita ID {id_citas} cancelada correctamente en BD",
            flush=True,
        )

        # DISPARAMOS EL EVENTO
        publicar_evento(
            id_usuario=id_paciente,
            id_cita=id_citas,
            accion="CITA CANCELADA",
            detalles="La cita ha sido cancelada por el usuario.",
        )

        return jsonify({"mensaje": "Cita cancelada correctamente"}), 200

    except Exception as e:
        print(f"[SERVICIO-CITAS] Error al cancelar cita: {str(e)}", flush=True)
        return jsonify({"Error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route("/reprogramar/<int:id_citas>", methods=["PUT"])
def reprogramar_cita(id_citas):
    print(
        f"[SERVICIO-CITAS] Solicitud recibida para reprogramar la cita ID {id_citas} (/reprogramar)",
        flush=True,
    )
    data = request.get_json()

    nueva_fecha = data.get("fecha_programacion_citas")
    nueva_hora = data.get("hora_programacion_citas")

    if not nueva_fecha or not nueva_hora:
        print("[SERVICIO-CITAS] Error: Nueva fecha u hora no enviadas", flush=True)
        return jsonify({"Error": "La nueva fecha y hora son obligatorias"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT id_doctor_citas, estado_citas, id_paciente_citas
            FROM citas
            WHERE id_citas = %s
            """,
            (id_citas,),
        )
        cita = cursor.fetchone()

        if not cita:
            print(
                f"[SERVICIO-CITAS] Error: La cita ID {id_citas} no existe", flush=True
            )
            return jsonify({"Error": "La cita no existe"}), 404

        doctor_id = cita[0]
        estado_actual = cita[1]
        id_paciente = cita[2]

        if estado_actual == "Cancelado":
            print(
                f"[SERVICIO-CITAS] Error: Intento de reprogramar una cita cancelada (ID {id_citas})",
                flush=True,
            )
            return jsonify({"Error": "No se puede reprogramar una cita cancelada"}), 400

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
            (doctor_id, nueva_fecha, nueva_hora, id_citas),
        )

        conflicto = cursor.fetchone()
        if conflicto:
            print(
                f"[SERVICIO-CITAS] Horario no disponible para reprogramación (Doctor ID {doctor_id})",
                flush=True,
            )
            return jsonify({"Error": "El horario ya está ocupado"}), 409

        # Reprogramar cita
        cursor.execute(
            """
            UPDATE citas
            SET fecha_programacion_citas = %s,
                hora_programacion_citas = %s,
                estado_citas = 'Reprogramado'
            WHERE id_citas = %s
            """,
            (nueva_fecha, nueva_hora, id_citas),
        )
        conn.commit()

        print(
            f"[SERVICIO-CITAS] Cita ID {id_citas} reprogramada correctamente en BD",
            flush=True,
        )

        # DISPARAMOS EL EVENTO
        publicar_evento(
            id_usuario=id_paciente,
            id_cita=id_citas,
            accion="CITA REPROGRAMADA",
            detalles=f"Cita movida para el {nueva_fecha} a las {nueva_hora}",
        )

        return jsonify({"mensaje": "Cita reprogramada correctamente"}), 200

    except Exception as e:
        print(f"[SERVICIO-CITAS] Error al reprogramar cita: {str(e)}", flush=True)
        return jsonify({"Error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route("/health")
def health():
    print("[SERVICIO-CITAS] Health check solicitado", flush=True)
    return jsonify({"status": "ok", "servicio": "Citas"}), 200


# INICIO DE LA APLICACIÓN

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
