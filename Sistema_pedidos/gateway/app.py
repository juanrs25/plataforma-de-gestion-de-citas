from flask import Flask, request, jsonify
import requests 
import time


app = Flask(__name__)


@app.route("/")
def home():
    return "API FUNCIONANDO"


@app.route("/estado/inventario")
def estado_inventario():
    try:
        response = requests.get("http://inventario:5000/health", timeout=2)
        return jsonify(response.json()) 
    except:
        return jsonify({
            "status": "Caido",
            "service": "Inventario"
        }), 503

@app.route("/estado/pedidos")
def estado_pedidos():
    try:
        response = requests.get("http://pedidos:5000/health", timeout=2)
        return jsonify(response.json()) 
    except:
        return jsonify({
            "status": "Caido",
            "service": "Pedidos"
        }), 503
    
@app.route("/estado/pagos")
def estado_pagos():
    try:
        response = requests.get("http://pagos:5000/health", timeout=2)
        return jsonify(response.json()) 
    except:
        return jsonify({
            "status": "Caido",
            "service": "Pagos"
        }), 503
    
@app.route("/inventario")
def obtener_inventario():

    print("Solicitud recibida para inventario", flush=True)

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
            f"Error al conectar con inventario",
            flush=True
        )

        return jsonify({
            "error": "Servicio no disponible"
        }), 503

@app.route("/pagos")
def obtener_pagos():

    print("Solicitud recibida para pagos", flush=True)

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
            f"Error al conectar con pagos",
            flush=True
        )

        return jsonify({
            "error": "Servicio no disponible"
        }), 503
@app.route("/pedidos")
def obtener_pedidos():

    print("Solicitud recibida para pedidos", flush=True)

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
            f"Error al conectar con pedidos",
            flush=True
        )

        return jsonify({
            "error": "Servicio no disponible"
        }), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)