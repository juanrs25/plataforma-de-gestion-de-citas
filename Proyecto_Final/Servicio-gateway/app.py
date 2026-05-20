from time import time

from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

fallos_health_citas = 0
fallos_health_autenticacion = 0
fallos_health_historial = 0

servicios = {
    "Autenticacion": "http://autenticacion:5000/health",
    "Citas": "http://citas:5000/health",
    "Historial": "http://historial:5000/health"
}
#.
# RUTAS HACIA EL SERVICIO AUTENTICACION
@app.route("/")
def home():
    return "API FUNCIONANDO"


@app.route("/usuarios/listar", methods=["GET"])
def listar_usuarios():
    print("[Gateway] Solicitando lista de usuarios...", flush=True)
    try:
        response = requests.get("http://autenticacion:5000/listar", timeout=3)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        print(
            "[Gateway] ¡ERROR! Servicio de autenticación caído o no responde al listar usuarios",
            flush=True,
        )
        return jsonify({"error": "Servicio de autenticación no disponible"}), 503


@app.route("/usuarios/registro", methods=["POST"])
def registro_usuario():
    print("[Gateway] Procesando registro de usuario...", flush=True)
    try:
        response = requests.post(
            "http://autenticacion:5000/registro", json=request.json, timeout=3
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        print(
            "[Gateway] ¡ERROR! Servicio de autenticación caído al intentar registrar usuario",
            flush=True,
        )
        return jsonify({"error": "Servicio de autenticación no disponible"}), 503


@app.route("/usuarios/login", methods=["POST"])
def login_usuario():
    print("[Gateway] Procesando login...", flush=True)
    try:
        response = requests.post(
            "http://autenticacion:5000/login", json=request.json, timeout=3
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        print(
            "[Gateway] ¡ERROR! Servicio de autenticación caído al intentar hacer login",
            flush=True,
        )
        return jsonify({"error": "Servicio de autenticación no disponible"}), 503


# RUTAS HACIA EL SERVICIO DE CITAS


@app.route("/citas/agendar", methods=["POST"])
def agendar_cita():
    print("[Gateway] Agendando nueva cita...", flush=True)
    try:
        response = requests.post(
            "http://citas:5000/agendar", json=request.json, timeout=3
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        print(
            "[Gateway] ¡ERROR! No se pudo agendar, el servicio de citas está caído",
            flush=True,
        )
        return jsonify({"error": "Servicio de citas no disponible"}), 503


@app.route("/citas/paciente", methods=["GET"])
def citas_por_paciente():
    print("[Gateway] Consultando citas de un paciente...", flush=True)
    id_paciente = request.args.get("id_paciente")

    if not id_paciente:
        print("[Gateway] Error: Petición rechazada, falta id_paciente", flush=True)
        return (
            jsonify(
                {
                    "error": "Debes proporcionar el id_paciente en la URL (ej: ?id_paciente=1)"
                }
            ),
            400,
        )
    params = {"id_paciente": id_paciente}
    try:
        response = requests.get(
            "http://citas:5000/citas_paciente", params=params, timeout=3
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        print(
            "[Gateway] ¡ERROR! Servicio de citas caído al consultar historial del paciente",
            flush=True,
        )
        return jsonify({"error": "Servicio de citas no disponible"}), 503


@app.route("/citas/disponibilidad", methods=["GET"])
def consultar_disponibilidad():
    print("[Gateway] Consultando disponibilidad de doctores...", flush=True)
    id_doctor = request.args.get("id_doctor")
    fecha = request.args.get("fecha")
    params = {}
    if id_doctor:
        params["id_doctor"] = id_doctor
    if fecha:
        params["fecha"] = fecha
    try:
        response = requests.get(
            "http://citas:5000/disponibilidad", params=params, timeout=3
        )
        return jsonify(response.json()), response.status_code

    except requests.exceptions.ConnectionError:
        print(
            "[Gateway] ¡ERROR! Servicio de citas caído al consultar disponibilidad",
            flush=True,
        )
        return jsonify({"error": "Servicio de citas no disponible"}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/estado/autenticacion", methods=["GET"])
def estado_autenticacion():

    global fallos_health_autenticacion

    print(
        "Solicitud de health check para autenticación recibida",
        flush=True
    )
    

    inicio = time()

    try:

        response = requests.get(
            "http://autenticacion:5000/health",
            timeout=2
        )

        print(
            "Servicio autenticacion disponible",
            flush=True
        )

        print(
            f"Codigo HTTP: {response.status_code}",
            flush=True
        )

        # reiniciar contador si funciona
        fallos_health_autenticacion = 0

        return jsonify(response.json())

    except Exception as e:

        # aumentar contador
        fallos_health_autenticacion += 1

        print(
            f"Servicio autenticacion caido: {e}",
            flush=True
        )

        print(
            f"Cantidad de fallos health autenticacion: {fallos_health_autenticacion}",
            flush=True
        )

        return jsonify({
            "status": "Caido",
            "service": "Autenticacion"
        }), 503

    finally:

        fin = time()

        print(
            f"[INFO] Tiempo de respuesta Autenticacion: {fin - inicio:.4f} segundos",
            flush=True
        )

@app.route("/estado/citas", methods=["GET"])
def estado_citas():

    global fallos_health_citas

    print(
        "Solicitud de health check para citas recibida",
        flush=True
    )
    

    inicio = time()

    try:

        response = requests.get(
            "http://citas:5000/health",
            timeout=2
        )

        print(
            "Servicio citas disponible",
            flush=True
        )

        print(
            f"Codigo HTTP: {response.status_code}",
            flush=True
        )

        # reiniciar contador si funciona
        fallos_health_citas = 0

        return jsonify(response.json())

    except Exception as e:

        # aumentar contador
        fallos_health_citas += 1

        print(
            f"Servicio citas caido: {e}",
            flush=True
        )

        print(
            f"Cantidad de fallos health citas: {fallos_health_citas}",
            flush=True
        )

        return jsonify({
            "status": "Caido",
            "service": "Citas"
        }), 503

    finally:

        fin = time()

        print(
            f"[INFO] Tiempo de respuesta Citas: {fin - inicio:.4f} segundos",
            flush=True
        )

@app.route("/estado/historial", methods=["GET"])
def estado_historial():

    global fallos_health_historial

    print(
        "Solicitud de health check para historial recibida",
        flush=True
    )
    

    inicio = time()

    try:

        response = requests.get(
            "http://historial:5000/health",
            timeout=2
        )

        print(
            "Servicio historial disponible",
            flush=True
        )

        print(
            f"Codigo HTTP: {response.status_code}",
            flush=True
        )

        # reiniciar contador si funciona
        fallos_health_historial = 0

        return jsonify(response.json())

    except Exception as e:

        # aumentar contador
        fallos_health_historial += 1

        print(
            f"Servicio historial caido: {e}",
            flush=True
        )

        print(
            f"Cantidad de fallos health historial: {fallos_health_historial}",
            flush=True
        )

        return jsonify({
            "status": "Caido",
            "service": "Historial"
        }), 503

    finally:

        fin = time()

        print(
            f"[INFO] Tiempo de respuesta Historial: {fin - inicio:.4f} segundos",
            flush=True
        )


@app.route("/monitoreo", methods=["GET"])
def monitoreo():

    print(
        "[MONITOREO] Verificando estado de microservicios...",
        flush=True
    )

    estados = {}

    servicios_ok = []
    servicios_caidos = []

    for nombre_servicio, url in servicios.items():

        inicio = time()

        try:

            response = requests.get(
                url,
                timeout=2
            )

            fin = time()

            tiempo = f"{fin - inicio:.4f} segundos"

            estados[nombre_servicio] = {
                "status": "OK",
                "codigo_http": response.status_code,
                "tiempo_respuesta": tiempo
            }

            servicios_ok.append(nombre_servicio)

            print(
                f"{nombre_servicio} funcionando correctamente",
                flush=True
            )

            print(
                f"Tiempo de respuesta {nombre_servicio}: {tiempo}",
                flush=True
            )

        except Exception as e:

            estados[nombre_servicio] = {
                "status": "Caido",
                "error": "Servicio no responde"
            }

            servicios_caidos.append(nombre_servicio)

            print(
                f"Servicio {nombre_servicio} no disponible",
                flush=True
            )
    # resumen final

    if len(servicios_caidos) == 0:

        print(
            "Todos los servicios OK",
            flush=True
        )

    else:

        print(
            f"Servicios caidos: {', '.join(servicios_caidos)}",
            flush=True
        )

        print(
            f"Servicios OK: {', '.join(servicios_ok)}",
            flush=True
        )

    return jsonify(estados)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
