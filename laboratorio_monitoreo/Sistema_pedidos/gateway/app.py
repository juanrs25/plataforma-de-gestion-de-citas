from flask import Flask, jsonify
import requests
import time

app = Flask(__name__)

fallos_pagos = 0
fallos_inventario = 0
fallos_pedidos = 0

fallos_health_pedidos = 0
fallos_health_inventario = 0
fallos_health_pagos = 0

@app.route("/")
def home():
    return "API FUNCIONANDO"


# HEALTH CHECK PEDIDOS


@app.route("/estado/pedidos")
def estado_pedidos():

    global fallos_health_pedidos

    print(
        "Solicitud de health check para pedidos",
        flush=True
    )
    

    inicio = time.time()

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

        # reiniciar contador si funciona
        fallos_health_pedidos = 0

        return jsonify(response.json())

    except Exception as e:

        # aumentar contador
        fallos_health_pedidos += 1

        print(
            f"Servicio pedidos caido: {e}",
            flush=True
        )

        print(
            f"Cantidad de fallos health pedidos: {fallos_health_pedidos}",
            flush=True
        )

        return jsonify({
            "status": "Caido",
            "service": "Pedidos"
        }), 503

    finally:

        fin = time.time()

        print(
            f"[INFO] Tiempo de respuesta Pedidos: {fin - inicio:.4f} segundos",
            flush=True
        )



# HEALTH CHECK INVENTARIO

@app.route("/estado/inventario")
def estado_inventario():

    global fallos_health_inventario

    print(
        "Solicitud de health check para inventario",
        flush=True
    )

    inicio = time.time()

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

        # reiniciar contador si funciona
        fallos_health_inventario = 0

        return jsonify(response.json())

    except Exception as e:

        # aumentar contador
        fallos_health_inventario += 1

        print(
            f"Servicio inventario caido: {e}",
            flush=True
        )

        print(
            f"Cantidad de fallos health inventario: {fallos_health_inventario}",
            flush=True
        )

        return jsonify({
            "status": "Caido",
            "service": "Inventario"
        }), 503

    finally:

        fin = time.time()

        print(
            f"[INFO] Tiempo de respuesta Inventario: {fin - inicio:.4f} segundos",
            flush=True
        )


# HEALTH CHECK PAGOS

@app.route("/estado/pagos")
def estado_pagos():

    global fallos_health_pagos

    print(
        "Solicitud de health check para pagos",
        flush=True
    )

    inicio = time.time()

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

        # reiniciar contador si funciona
        fallos_health_pagos = 0

        return jsonify(response.json())

    except Exception as e:

        # aumentar contador
        fallos_health_pagos += 1

        print(
            f"Servicio pagos caido: {e}",
            flush=True
        )

        print(
            f"Cantidad de fallos health pagos: {fallos_health_pagos}",
            flush=True
        )

        return jsonify({
            "status": "Caido",
            "service": "Pagos"
        }), 503

    finally:

        fin = time.time()

        print(
            f"[INFO] Tiempo de respuesta Pagos: {fin - inicio:.4f} segundos",
            flush=True
        )


# INVENTARIO


@app.route("/inventario")
def obtener_inventario():

    global fallos_inventario
   
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

        # reiniciar contador si funciona
        fallos_inventario = 0

        return jsonify(datos)

    except Exception as e:

        # aumentar contador
        fallos_inventario += 1

        print(
            f"Error al conectar con inventario: {e}",
            flush=True
        )

        print(
            f"Cantidad de fallos en inventario: {fallos_inventario}",
            flush=True
        )

        return jsonify({
            "error": "Servicio inventario no disponible"
        }), 503

    finally:

        fin = time.time()

        tiempo_respuesta = fin - inicio

        print(
            f"Tiempo de respuesta inventario: {tiempo_respuesta:.4f} segundos",
            flush=True
        )


# PAGOS


@app.route("/pagos")
def obtener_pagos():

    global fallos_pagos

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

        # reiniciar contador si funciona
        fallos_pagos = 0

        return jsonify(datos)

    except Exception as e:

        # aumentar contador
        fallos_pagos += 1

        print(
            f"Error al conectar con pagos: {e}",
            flush=True
        )

        print(
            f"Cantidad de fallos en pagos: {fallos_pagos}",
            flush=True
        )

        return jsonify({
            "error": "Servicio pagos no disponible"
        }), 503

    finally:

        fin = time.time()

        tiempo_respuesta = fin - inicio

        print(
            f"Tiempo de respuesta pagos: {tiempo_respuesta:.4f} segundos",
            flush=True
        )

# PEDIDOS


@app.route("/pedidos")
def obtener_pedidos():

    global fallos_pedidos

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

        print(
            "Respuesta recibida correctamente",
            flush=True
        )

        # reiniciar contador si funciona
        fallos_pedidos = 0

        return jsonify(datos)

    except Exception as e:

        fallos_pedidos += 1

        print(
            f"Error al conectar con pedidos: {e}",
            flush=True
        )

        print(
            f"Cantidad de fallos en pedidos: {fallos_pedidos}",
            flush=True
        )

        return jsonify({
            "error": "Servicio pedidos no disponible"
        }), 503

    finally:

        fin = time.time()

        tiempo_respuesta = fin - inicio

        print(
            f"Tiempo de respuesta pedidos: {tiempo_respuesta:.4f} segundos",
            flush=True
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
