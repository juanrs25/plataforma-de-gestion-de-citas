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
        host=os.getenv("NOTIFICACIONES_DB_HOST", "db_notificaciones"),
        user=os.getenv("NOTIFICACIONES_DB_USER", "root"),
        password=os.getenv("NOTIFICACIONES_DB_PASSWORD", "root"),
        database=os.getenv("NOTIFICACIONES_DB_NAME", "notificaciones_db"),
    )


# insertar en bd

def procesar_notificacion(datos_evento):
    conn = None
    cur = None
    try:
        mensaje_usuario = f"Hola! Tu cita cambió al estado: {datos_evento['accion']}. Detalles: {datos_evento['detalles']}"
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO notificaciones (id_usuario, mensaje) VALUES (%s, %s)",
            (datos_evento["id_usuario"], mensaje_usuario)
        )
        conn.commit()
        print(f"[SERVICIO-NOTIFICACIONES]  Registro guardado en BD para usuario {datos_evento['id_usuario']}", flush=True)
    except Exception as e:
        print(f"[SERVICIO-NOTIFICACIONES] Error de BD al guardar notificación: {str(e)}", flush=True)
    finally:
        if cur: cur.close()
        if conn: conn.close()


# RabbitMQ - conexion y escucha

def conectar_y_escuchar():
    try:
        print("[SERVICIO-NOTIFICACIONES] Iniciando hilo de RabbitMQ...", flush=True)
        rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
        
        connection = None
        for i in range(100):
            try:
                connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
                print(f"[SERVICIO-NOTIFICACIONES] Conectado exitosamente a RabbitMQ en el intento {i+1}", flush=True)
                break
            except pika.exceptions.AMQPConnectionError:
                print(f"[SERVICIO-NOTIFICACIONES] Esperando a RabbitMQ... (Intento {i+1})", flush=True)
                time.sleep(3)

        if not connection:
            print("[SERVICIO-NOTIFICACIONES] [x] ERROR FATAL: No se pudo conectar a RabbitMQ", flush=True)
            return

        channel = connection.channel()
        channel.queue_declare(queue="eventos_notificaciones", durable=True)

        def callback(ch, method, properties, body):
            datos_evento = json.loads(body)
            print(f"[SERVICIO-NOTIFICACIONES]Evento recibido desde eventos_notificaciones: {datos_evento['accion']}", flush=True)
            procesar_notificacion(datos_evento)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue="eventos_notificaciones", on_message_callback=callback)
        print("[SERVICIO-NOTIFICACIONES] Escuchando eventos en la cola 'eventos_notificaciones' en segundo plano...", flush=True)
        channel.start_consuming()
    except Exception as e:
        print(f"[SERVICIO-NOTIFICACIONES] El hilo de RabbitMQ colapsó: {str(e)}", flush=True)


# ENDPOINTS 

@app.route("/notificaciones/<int:id_usuario>", methods=["GET"])
def ver_notificaciones(id_usuario):
    print(f"[SERVICIO-NOTIFICACIONES] Solicitud GET recibida para notificaciones del usuario {id_usuario}", flush=True)
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """SELECT id_notificacion, mensaje, leido, fecha_creacion 
               FROM notificaciones 
               WHERE id_usuario = %s 
               ORDER BY fecha_creacion DESC""",
            (id_usuario,)
        )
        notificaciones = cur.fetchall()
        for n in notificaciones:
            n['fecha_creacion'] = str(n['fecha_creacion'])
        
        print(f"[SERVICIO-NOTIFICACIONES] Consulta exitosa. Se devolvieron {len(notificaciones)} notificaciones.", flush=True)
        return jsonify({"id_usuario": id_usuario, "notificaciones": notificaciones}), 200
    except Exception as e:
        print(f"[SERVICIO-NOTIFICACIONES] Error en GET /notificaciones: {str(e)}", flush=True)
        return jsonify({"error": str(e)}), 500
    finally:
        if cur: cur.close()
        if conn: conn.close()

@app.route("/notificaciones/marcar-leidas/<int:id_usuario>", methods=["PUT"])
def marcar_notificaciones_leidas(id_usuario):
    print(f"[SERVICIO-NOTIFICACIONES] Solicitud PUT recibida para marcar leídas del usuario {id_usuario}", flush=True)
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(
            """
            UPDATE notificaciones 
            SET leido = TRUE 
            WHERE id_usuario = %s AND leido = FALSE
            """,
            (id_usuario,)
        )
        conn.commit()
        
        cantidad_actualizadas = cur.rowcount
        print(f"[SERVICIO-NOTIFICACIONES] El usuario {id_usuario} marcó {cantidad_actualizadas} notificaciones como leídas", flush=True)
        
        return jsonify({
            "mensaje": "Notificaciones actualizadas correctamente",
            "id_usuario": id_usuario,
            "notificaciones_marcadas": cantidad_actualizadas
        }), 200

    except Exception as e:
        print(f"[SERVICIO-NOTIFICACIONES] Error al actualizar notificaciones (PUT): {str(e)}", flush=True)
        return jsonify({"Error": str(e)}), 500
    finally:
        if cur: cur.close()
        if conn: conn.close()


@app.route("/health")
def health():

    print("Health check solicitado en historial", flush=True)

    return {"status": "ok", "servicio": "Historial"}



hilo_rabbitmq = threading.Thread(target=conectar_y_escuchar)
hilo_rabbitmq.daemon = True
hilo_rabbitmq.start()

if __name__ == "__main__":
    print("[SERVICIO-NOTIFICACIONES] Inicializando servidor Flask...", flush=True)
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)