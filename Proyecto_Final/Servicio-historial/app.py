from flask import Flask, jsonify, request
import mysql.connector
import pika
import json
import threading
import os
import time

app = Flask(__name__)


# CONFIGURACION DE BASE DE DATOS


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("HISTORIAL_DB_HOST", "db_historial"),
        user=os.getenv("HISTORIAL_DB_USER", "root"),
        password=os.getenv("HISTORIAL_DB_PASSWORD", "root"),
        database=os.getenv("HISTORIAL_DB_NAME", "historial_db"),
    )


# GUARDAR EN BD HISTORIAL


def guardar_evento_en_bd(datos_evento):
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO RegistroHistorial (id_usuario, id_cita, accion, detalles) VALUES (%s, %s, %s, %s)",
            (
                datos_evento["id_usuario"],
                datos_evento["id_cita"],
                datos_evento["accion"],
                datos_evento.get("detalles", ""),
            ),
        )
        conn.commit()
        print(
            f"[SERVICIO-HISTORIAL] [v] Evento '{datos_evento['accion']}' guardado en BD para cita {datos_evento['id_cita']}",
            flush=True,
        )
    except Exception as e:
        print(
            f"[SERVICIO-HISTORIAL] [x] Error al guardar en la BD de historial: {str(e)}",
            flush=True,
        )
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# RABBITMQ


def conectar_y_escuchar():
    try:
        print("[SERVICIO-HISTORIAL] Iniciando hilo de RabbitMQ...", flush=True)
        rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")

        connection = None
        for i in range(100):
            try:
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=rabbitmq_host)
                )
                print(
                    f"[SERVICIO-HISTORIAL] Conectado exitosamente a RabbitMQ en el intento {i+1}",
                    flush=True,
                )
                break
            except pika.exceptions.AMQPConnectionError:
                print(
                    f"[SERVICIO-HISTORIAL] Esperando a RabbitMQ... (Intento {i+1})",
                    flush=True,
                )
                time.sleep(3)

        if not connection:
            print(
                "[SERVICIO-HISTORIAL] [x] ERROR FATAL: No se pudo conectar a RabbitMQ",
                flush=True,
            )
            return

        channel = connection.channel()

        # Dejado exactamente con tu cola original
        channel.queue_declare(queue="eventos_citas", durable=True)

        def callback(ch, method, properties, body):
            datos_evento = json.loads(body)
            print(
                f"[SERVICIO-HISTORIAL] Evento recibido desde eventos_citas: {datos_evento['accion']} para cita {datos_evento['id_cita']}",
                flush=True,
            )
            guardar_evento_en_bd(datos_evento)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue="eventos_citas", on_message_callback=callback)
        print(
            "[SERVICIO-HISTORIAL] Escuchando eventos en la cola 'eventos_citas' en segundo plano...",
            flush=True,
        )
        channel.start_consuming()
    except Exception as e:
        print(
            f"[SERVICIO-HISTORIAL] [x] El hilo de RabbitMQ colapsó: {str(e)}",
            flush=True,
        )


# ENDPOINTS


@app.route("/historial/<int:id_usuario>", methods=["GET"])
def ver_historial(id_usuario):
    print(
        f"[SERVICIO-HISTORIAL] Solicitud GET recibida para historial del usuario {id_usuario}",
        flush=True,
    )
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """SELECT id_cita, accion, detalles, fecha_evento 
               FROM RegistroHistorial 
               WHERE id_usuario = %s 
               ORDER BY fecha_evento DESC""",
            (id_usuario,),
        )
        datos = cur.fetchall()

        historial = []
        for fila in datos:
            historial.append(
                {
                    "id_cita": fila[0],
                    "accion": fila[1],
                    "detalles": fila[2],
                    "fecha": str(fila[3]),
                }
            )

        print(
            f"[SERVICIO-HISTORIAL] Consulta exitosa. Se devolvieron {len(historial)} registros.",
            flush=True,
        )
        return jsonify({"id_usuario": id_usuario, "historial": historial}), 200
    except Exception as e:
        print(f"[SERVICIO-HISTORIAL] [x] Error en GET /historial: {str(e)}", flush=True)
        return jsonify({"error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.route("/historial", methods=["POST"])
def agregar_historial_manual():
    print("[SERVICIO-HISTORIAL] Solicitud POST recibida para nota manual", flush=True)
    conn = None
    cur = None
    try:
        datos = request.get_json()

        id_usuario = datos.get("id_usuario")
        id_cita = datos.get("id_cita")
        accion = datos.get("accion", "NOTA_MANUAL")
        detalles = datos.get("detalles")

        if not id_usuario or not id_cita or not detalles:
            print(
                "[SERVICIO-HISTORIAL] Error: Faltan campos obligatorios en el POST",
                flush=True,
            )
            return (
                jsonify({"Error": "id_usuario, id_cita y detalles son obligatorios"}),
                400,
            )

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO RegistroHistorial (id_usuario, id_cita, accion, detalles) 
            VALUES (%s, %s, %s, %s)
            """,
            (id_usuario, id_cita, accion, detalles),
        )
        conn.commit()

        print(
            f"[SERVICIO-HISTORIAL] Nota manual guardada con éxito. ID Registro: {cur.lastrowid}",
            flush=True,
        )
        return (
            jsonify(
                {
                    "mensaje": "Nota manual agregada al historial de la cita correctamente",
                    "id_registro": cur.lastrowid,
                }
            ),
            201,
        )

    except Exception as e:
        print(f"[SERVICIO-HISTORIAL] [x] Error en POST manual: {str(e)}", flush=True)
        return jsonify({"Error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.route("/health")
def health():

    print("Health check solicitado en historial", flush=True)

    return {"status": "ok", "servicio": "Historial"}


# INICIO DE LA APLICACION

hilo_rabbitmq = threading.Thread(target=conectar_y_escuchar)
hilo_rabbitmq.daemon = True
hilo_rabbitmq.start()

if __name__ == "__main__":
    print("[SERVICIO-HISTORIAL] Inicializando servidor Flask...", flush=True)
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
