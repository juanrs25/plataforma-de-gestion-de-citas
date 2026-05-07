from flask import Flask, request, jsonify
import requests

import time

app = Flask(__name__)

fallos_backend = 0
circuito_abierto = False
ultimo_fallo_backend = 0
tiempo_recuerpacion = 15


fallos_usuarios = 0
circuito_abierto_usuarios = False
ultimo_fallo_usuarios = 0


# @app.route("/usuarios")
# def usuarios():
#     print("[Gateway] llamando al servicio de usuarios...", flush=True)
#     global fallos_usuarios, circuito_abierto_usuarios

#     if circuito_abierto_usuarios:
#         print("[Gateway] Peticion a rechazada, el circuito ta abierto", flush=True)
#         return jsonify(
#             {"error": "Servicio de usuarios temporalmente fuera de servicio"}
#         )

#     try:
#         response = requests.get("http://usuarios:5000/usuarios", timeout=3)
#         fallos_usuarios = 0
#         print("[Gateway] Respuesta exitosa desde usuarios", flush=True)
#         return jsonify(response.json())

#     except:
#         fallos_usuarios += 1
#         print(f"[Gateway] Numero de fallos: {fallos_usuarios}", flush=True)

#         if fallos_usuarios >= 3:
#             circuito_abierto_usuarios = True
#             print("[Gateway] Circuito de servicio usuario abierto", flush=True)
#         return jsonify({"error": "Servicio de usuarios no disponible"}), 503


@app.route("/usuarios")
def usuarios():
    print("[Gateway] llamando al servicio de usuarios...", flush=True)
    global fallos_usuarios, circuito_abierto_usuarios, ultimo_fallo_usuarios

    if circuito_abierto_usuarios:
        tiempo_actual = time.time()
        tiempo_transcurrido = tiempo_actual - ultimo_fallo_usuarios

        if tiempo_transcurrido > tiempo_recuerpacion:
            print(
                f"[Gateway] Han pasado {tiempo_transcurrido}. Intentando petición de prueba a usuarios (MEDIO-ABIERTO)...",
                flush=True,
            )
        else:
            tiempo_restante = tiempo_recuerpacion - tiempo_transcurrido
            print(
                f"[Gateway] Circuito de usuarios ABIERTO. Rechazando. Faltan {tiempo_restante} para probar de nuevo.",
                flush=True,
            )
            return (
                jsonify(
                    {"error": "Servicio de usuarios temporalmente fuera de servicio"}
                ),
                503,
            )

    try:
        response = requests.get("http://usuarios:5000/usuarios", timeout=3)

        if circuito_abierto_usuarios:
            print(
                "[Gateway] ¡Prueba a usuarios exitosa! El servicio ya funciona",
                flush=True,
            )

        fallos_usuarios = 0
        circuito_abierto_usuarios = False
        print("[Gateway] Respuesta exitosa desde usuarios", flush=True)
        return jsonify(response.json())

    except:
        fallos_usuarios += 1
        ultimo_fallo_usuarios = time.time()
        print(
            f"[Gateway] Fallo de conexión en usuarios número {fallos_usuarios}",
            flush=True,
        )

        if fallos_usuarios >= 3:
            if circuito_abierto_usuarios:
                print(
                    "[Gateway] La prueba a usuarios falló. El circuito vuelve a estar completamente ABIERTO.",
                    flush=True,
                )
            else:
                print(
                    "[Gateway] Se alcanzó el límite de fallos en usuarios. Circuito ABIERTO.",
                    flush=True,
                )
            circuito_abierto_usuarios = True

        return jsonify({"error": "Servicio de usuarios no disponible"}), 503


# @app.route("/mascotas")
# def mascotas():
#     print("[Gateway] llamando al backend...", flush=True)
#     global fallos_backend, circuito_abierto

#     if circuito_abierto:
#         print("[Gateway] Petición a mascotas rechazada circuito abierto", flush=True)
#         return jsonify({"error": "Servicio Backend temporalmente fuera de servicio"})

#     try:
#         response = requests.get("http://backend:5000/mascotas", timeout=2)
#         fallos_backend = 0
#         print("[Gateway] Respuesta exitosas de servicio mascotas", flush=True)
#         return jsonify(response.json())

#     except:
#         fallos_backend += 1
#         print(f"Fallo numero {fallos_backend}", flush=True)

#         if fallos_backend >= 3:
#             circuito_abierto = True
#             print("[Gateway] Circuito abierto", flush=True)
#         return jsonify({"error": "Servicio no disponible"}), 503


# =======================================================================================================================================================
# ==========================INTENTO DE HALF-OPEN=======================================================
# =============================================================================


@app.route("/mascotas")
def mascotasDos():
    print("[Gateway] llamando al backend de mascotas...", flush=True)
    global fallos_backend, circuito_abierto, ultimo_fallo_backend

    if circuito_abierto:
        tiempo_actual = time.time()
        tiempo_transcurrido = tiempo_actual - ultimo_fallo_backend

        if tiempo_transcurrido > tiempo_recuerpacion:
            print(
                f"[Gateway] Han pasado {tiempo_transcurrido}. Intentando petición de prueba (MEDIO-ABIERTO)...",
                flush=True,
            )

        else:

            tiempo_restante = tiempo_recuerpacion - tiempo_transcurrido
            print(
                f"[Gateway] Circuito ABIERTO. Rechazando. Faltan {tiempo_restante} para probar de nuevo.",
                flush=True,
            )
            return (
                jsonify({"error": "Servicio Backend temporalmente fuera de servicio"}),
                503,
            )

    try:
        response = requests.get("http://backend:5000/mascotas", timeout=2)

        if circuito_abierto:

            print("[Gateway] prueba exitosa! El servicio ya funciona", flush=True)

        fallos_backend = 0
        circuito_abierto = False
        print("[Gateway] Respuesta exitosa de servicio mascotas", flush=True)
        return jsonify(response.json())

    except:
        fallos_backend += 1
        ultimo_fallo_backend = time.time()
        print(f"[Gateway]  Fallo de conexión número {fallos_backend}", flush=True)

        if fallos_backend >= 3:
            if circuito_abierto:
                print(
                    "[Gateway] La prueba falló. El circuito vuelve a estar completamente ABIERTO.",
                    flush=True,
                )
            else:
                print(
                    "[Gateway] Se alcanzó el límite de fallos. Circuito ABIERTO.",
                    flush=True,
                )
            circuito_abierto = True

        return jsonify({"error": "Servicio no disponible"}), 503


# ==========================================================================================fin del intento


# RETO: Obtener mascota por ID con manejo de errores


# @app.route("/mascotas/<int:id>")
# def obtener_mascota(id):
#     print(f"[Gateway] Buscando mascota {id} en el backend...", flush=True)
#     global fallos_backend, circuito_abierto

#     if circuito_abierto:
#         print(
#             "[Gateway] Peticin a mascota por ID rechazada  por que el circuito abierto",
#             flush=True,
#         )
#         return (
#             jsonify({"error": "Servicio de Backend temporalmente fuera de servicio"}),
#             503,
#         )

#     try:
#         response = requests.get(f"http://backend:5000/mascotas/{id}", timeout=3)
#         if response.status_code == 404:
#             print(
#                 f"[Gateway] La mascota {id} no fue encontrada (Error 404)", flush=True
#             )
#             return jsonify({"error": "La mascota no existe"}), 404
#         fallos_backend = 0
#         print(f"[Gateway] Respuesta exitosa para mascota con id: {id}", flush=True)
#         return jsonify(response.json())

#     except:
#         fallos_backend += 1
#         print(f"[Gateway] Fallo en mascotas (ID) numero {fallos_backend}", flush=True)
#         if fallos_backend >= 3:
#             circuito_abierto = True
#             print("[Gateway] Circuito de mascotas esta abierto ", flush=True)
#         return jsonify({"error": "El backend de mascotas está fuera de línea"}), 503


# RETO: Obtener mascota por ID con manejo de errores
@app.route("/mascotas/<int:id>")
def obtener_mascota(id):
    print(f"[Gateway] Buscando mascota {id} en el backend...", flush=True)
    # IMPORTANTE: Compartimos las mismas variables que el endpoint /mascotas
    global fallos_backend, circuito_abierto, ultimo_fallo_backend

    # === LÓGICA HALF-OPEN ===
    if circuito_abierto:
        tiempo_actual = time.time()
        tiempo_transcurrido = tiempo_actual - ultimo_fallo_backend

        if tiempo_transcurrido > tiempo_recuerpacion:
            print(
                f"[Gateway] Han pasado {tiempo_transcurrido:.0f}s. Intentando petición de prueba a mascota {id} (MEDIO-ABIERTO)...",
                flush=True,
            )
        else:
            tiempo_restante = tiempo_recuerpacion - tiempo_transcurrido
            print(
                f"[Gateway] Circuito ABIERTO. Rechazando búsqueda de ID {id}. Faltan {tiempo_restante:.0f}s para probar de nuevo.",
                flush=True,
            )
            return (
                jsonify(
                    {"error": "Servicio de Backend temporalmente fuera de servicio"}
                ),
                503,
            )

    # === INTENTO DE CONEXIÓN ===
    try:
        response = requests.get(f"http://backend:5000/mascotas/{id}", timeout=3)

        # Si llegamos aquí, el backend respondió (ya sea un 200 o un 404)
        if circuito_abierto:
            print(
                "[Gateway] ¡Prueba por ID exitosa! El servicio de mascotas ya funciona",
                flush=True,
            )

        fallos_backend = 0
        circuito_abierto = False

        if response.status_code == 404:
            print(
                f"[Gateway] La mascota {id} no fue encontrada (Error 404)", flush=True
            )
            return jsonify({"error": "La mascota no existe"}), 404

        print(f"[Gateway] Respuesta exitosa para mascota con id: {id}", flush=True)
        return jsonify(response.json())

    except:
        fallos_backend += 1
        ultimo_fallo_backend = time.time()
        print(f"[Gateway] Fallo en mascotas (ID) numero {fallos_backend}", flush=True)

        if fallos_backend >= 3:
            if circuito_abierto:
                print(
                    "[Gateway] La prueba (ID) falló. El circuito vuelve a estar completamente ABIERTO.",
                    flush=True,
                )
            else:
                print(
                    "[Gateway] Se alcanzó el límite de fallos en mascotas (ID). Circuito ABIERTO.",
                    flush=True,
                )
            circuito_abierto = True

        return jsonify({"error": "El backend de mascotas está fuera de línea"}), 503


# Reto resumen
@app.route("/resumen")
def resumen():
    print("[Gateway] llamando al endpoint resumen...", flush=True)
    global circuito_abierto_usuarios, circuito_abierto

    if circuito_abierto or circuito_abierto_usuarios:
        print(
            "[Gateway] Resumen fallido: El sistema ta caido por que algun servicio ta caido ( tienen el circuito abierto))",
            flush=True,
        )
        return jsonify({"error": "El sistema esta caido"}), 503

    try:
        print("[Gateway] Resumen intentando conectar con usuarios...", flush=True)
        res_u = requests.get("http://usuarios:5000/usuarios", timeout=2)
        datos_usuarios = res_u.json() if res_u.status_code == 200 else []
        print("[Gateway] Resumen obtuvo datos de usuarios correctamente", flush=True)
    except:
        print("[Gateway] Fallo al obtener usuarios desde resumen", flush=True)
        return jsonify({"error": "El servucio de usuarios inaccesible"}), 503
        # datos_usuarios = "Error: Servicio de usuarios inaccesible"

    try:
        print("[Gateway] Resumen intentando conectar con mascotas...", flush=True)
        res_m = requests.get("http://backend:5000/mascotas", timeout=2)
        datos_mascotas = res_m.json() if res_m.status_code == 200 else []
        print("[Gateway] Resumen obtuvo datos de mascotas correctamente", flush=True)
    except:
        print(
            "[Gateway] Fallo al obtener mascotas desde resumen esto es backend",
            flush=True,
        )
        return jsonify({"error": "El sertvicio de backend inaccesible"}), 503
        # datos_mascotas = "Error: Servicio de mascotas inaccesible"
    print("[Gateway] Endpoint resumen completado con éxito", flush=True)
    return jsonify({"usuarios": datos_usuarios, "mascotas": datos_mascotas})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
