from flask import Flask, jsonify
import mysql.connector  # Cambiamos la librería
import pika
import json
import threading
import os
import time

app = Flask(__name__)



def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("HISTORIAL_DB_HOST", "db_historial"),
        user=os.getenv("HISTORIAL_DB_USER", "root"),
        password=os.getenv("HISTORIAL_DB_PASSWORD", "root"),
        database=os.getenv("HISTORIAL_DB_NAME", "historial_db"),
    )


@app.route("/historial/<int:id_usuario>", methods=["GET"])
def ver_historial(id_usuario):
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

        return jsonify({"id_usuario": id_usuario, "historial": historial}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


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
            f"[SERVICIO-HISTORIAL] Historial guardado en BD para la cita {datos_evento['id_cita']}",
            flush=True,
        )
    except Exception as e:
        print(
            f"[SERVICIO-HISTORIAL] Error al guardar en la BD de historial: {e}",
            flush=True,
        )
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()



# LOGICA DE RABBITMQ 

def conectar_y_escuchar():
    try:
        print("[SERVICIO-HISTORIAL] Iniciando hilo de RabbitMQ...", flush=True)
        rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")

        connection = None
        for i in range(10):
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
                "[SERVICIO-HISTORIAL] ERROR FATAL: No se pudo conectar a RabbitMQ",
                flush=True,
            )
            return

        channel = connection.channel()
        channel.queue_declare(queue="eventos_citas", durable=True)

        def callback(ch, method, properties, body):
            datos_evento = json.loads(body)
            print(
                f"[SERVICIO-HISTORIAL] Evento recibido: {datos_evento['accion']} para cita {datos_evento['id_cita']}",
                flush=True,
            )
            guardar_evento_en_bd(datos_evento)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue="eventos_citas", on_message_callback=callback)
        print(
            "[SERVICIO-HISTORIAL] Escuchando eventos de citas en segundo plano...",
            flush=True,
        )
        channel.start_consuming()
    except Exception as e:
        print(
            f"[SERVICIO-HISTORIAL] El hilo de RabbitMQ colapsó: {str(e)}",
            flush=True,
        )

@app.route("/health")
def health():

    print(
        "Health check solicitado en historial",
        flush=True
    )

    return {
        "status": "ok",
        "servicio": "Historial"
    }

# Lanzamos el escuchador
hilo_rabbitmq = threading.Thread(target=conectar_y_escuchar)
hilo_rabbitmq.daemon = True
hilo_rabbitmq.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
