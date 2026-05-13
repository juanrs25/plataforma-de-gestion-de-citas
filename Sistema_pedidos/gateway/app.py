from flask import Flask, jsonify
import requests
import time

app = Flask(__name__)


@app.route("/")
def home():
    return "API FUNCIONANDO"


# =========================
# HEALTH CHECK PEDIDOS
# =========================

@app.route("/estado/pedidos")
def estado_pedidos():

    print(
        "Solicitud de health check para pedidos",
        flush=True
    )

    try:

        response = requests.get(
            "http://pedidos:5000/health",
            timeout=2
        )

        print(
            "Servicio pedidos disponible",
            flush=True
        )

        print(
            f"Codigo HTTP: {response.status_code}",
            flush=True
        )

        return jsonify(response.json())

    except Exception as e:

        print(
            f"Servicio pedidos caido: {e}",
            flush=True
        )

        return jsonify({
            "status": "Caido",
            "service": "Pedidos"
        }), 503


# =========================
# HEALTH CHECK INVENTARIO
# =========================

@app.route("/estado/inventario")
def estado_inventario():

    print(
        "Solicitud de health check para inventario",
        flush=True
    )

    try:

        response = requests.get(
            "http://inventario:5000/health",
            timeout=2
        )

        print(
            "Servicio inventario disponible",
            flush=True
        )

        print(
            f"Codigo HTTP: {response.status_code}",
            flush=True
        )

        return jsonify(response.json())

    except Exception as e:

        print(
            f"Servicio inventario caido: {e}",
            flush=True
        )

        return jsonify({
            "status": "Caido",
            "service": "Inventario"
        }), 503


# =========================
# HEALTH CHECK PAGOS
# =========================

@app.route("/estado/pagos")
def estado_pagos():

    print(
        "Solicitud de health check para pagos",
        flush=True
    )

    try:

        response = requests.get(
            "http://pagos:5000/health",
            timeout=2
        )

        print(
            "Servicio pagos disponible",
            flush=True
        )

        print(
            f"Codigo HTTP: {response.status_code}",
            flush=True
        )

        return jsonify(response.json())

    except Exception as e:

        print(
            f"Servicio pagos caido: {e}",
            flush=True
        )

        return jsonify({
            "status": "Caido",
            "service": "Pagos"
        }), 503


# =========================
# INVENTARIO
# =========================

@app.route("/inventario")
def obtener_inventario():

    print(
        "Solicitud recibida para inventario",
        flush=True
    )

    inicio = time.time()

    try:

        respuesta = requests.get(
            "http://inventario:5000/inventario",
            timeout=3
        )

        print(
            "Servicio inventario respondió correctamente",
            flush=True
        )

        print(
            f"Codigo HTTP: {respuesta.status_code}",
            flush=True
        )

        datos = respuesta.json()

        fin = time.time()

        tiempo_respuesta = fin - inicio

        print(
            f"Tiempo de respuesta inventario: {tiempo_respuesta:.4f} segundos",
            flush=True
        )

        return jsonify(datos)

    except Exception as e:

        print(
            f"Error al conectar con inventario: {e}",
            flush=True
        )

        return jsonify({
            "error": "Servicio inventario no disponible"
        }), 503


# =========================
# PAGOS
# =========================

@app.route("/pagos")
def obtener_pagos():

    print(
        "Solicitud recibida para pagos",
        flush=True
    )

    inicio = time.time()

    try:

        respuesta = requests.get(
            "http://pagos:5000/pagos",
            timeout=3
        )

        print(
            "Servicio pagos respondió correctamente",
            flush=True
        )

        print(
            f"Codigo HTTP: {respuesta.status_code}",
            flush=True
        )

        datos = respuesta.json()

        fin = time.time()

        tiempo_respuesta = fin - inicio

        print(
            f"Tiempo de respuesta pagos: {tiempo_respuesta:.4f} segundos",
            flush=True
        )

        return jsonify(datos)

    except Exception as e:

        print(
            f"Error al conectar con pagos: {e}",
            flush=True
        )

        return jsonify({
            "error": "Servicio pagos no disponible"
        }), 503


# =========================
# PEDIDOS
# =========================

@app.route("/pedidos")
def obtener_pedidos():

    print(
        "Solicitud recibida para pedidos",
        flush=True
    )

    inicio = time.time()

    try:

        respuesta = requests.get(
            "http://pedidos:5000/pedidos",
            timeout=3
        )

        print(
            "Servicio pedidos respondió correctamente",
            flush=True
        )

        print(
            f"Codigo HTTP: {respuesta.status_code}",
            flush=True
        )

        datos = respuesta.json()

        fin = time.time()

        tiempo_respuesta = fin - inicio

        print(
            f"Tiempo de respuesta pedidos: {tiempo_respuesta:.4f} segundos",
            flush=True
        )

        return jsonify(datos)

    except Exception as e:

        print(
            f"Error al conectar con pedidos: {e}",
            flush=True
        )

        return jsonify({
            "error": "Servicio pedidos no disponible"
        }), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
