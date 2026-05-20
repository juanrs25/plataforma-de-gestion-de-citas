from time import time
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Configuracion de servicios para monitoreo
servicios = {
    "Autenticacion": "http://autenticacion:5000/health",
    "Citas": "http://citas:5000/health",
    "Historial": "http://historial:5000/health",
    "Notificaciones": "http://notificaciones:5000/health",
}

# Contadores de fallos independientes
fallos_health_autenticacion = 0
fallos_health_citas = 0
fallos_health_historial = 0
fallos_health_notificaciones = 0


# RUTAS HACIA SERVICIOS AUTENTICACION


@app.route("/")
def home():
    return "API GATEWAY FUNCIONANDO"


@app.route("/usuarios/listar", methods=["GET"])
def listar_usuarios():
    print("[Gateway] Solicitando lista de usuarios", flush=True)
    try:
        response = requests.get("http://autenticacion:5000/listar", timeout=3)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        print("[Gateway] Error: Servicio de autenticacion caido", flush=True)
        return jsonify({"error": "Servicio de autenticacion no disponible"}), 503


@app.route("/usuarios/registro", methods=["POST"])
def registro_usuario():
    print("[Gateway] Procesando registro de usuario", flush=True)
    try:
        response = requests.post(
            "http://autenticacion:5000/registro", json=request.json, timeout=3
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        print("[Gateway] Error: Servicio de autenticacion caido", flush=True)
        return jsonify({"error": "Servicio de autenticacion no disponible"}), 503


@app.route("/usuarios/login", methods=["POST"])
def login_usuario():
    print("[Gateway] Procesando login", flush=True)
    try:
        response = requests.post(
            "http://autenticacion:5000/login", json=request.json, timeout=3
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        print("[Gateway] Error: Servicio de autenticacion caido", flush=True)
        return jsonify({"error": "Servicio de autenticacion no disponible"}), 503


# RUTAS HACIA SERVICIOS CITAS


@app.route("/citas/agendar", methods=["POST"])
def agendar_cita():
    print("[Gateway] Agendando cita", flush=True)
    try:
        response = requests.post(
            "http://citas:5000/agendar", json=request.json, timeout=3
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        print("[Gateway] Error: Servicio de citas caido", flush=True)
        return jsonify({"error": "Servicio de citas no disponible"}), 503


@app.route("/citas/paciente", methods=["GET"])
def citas_por_paciente():
    print("[Gateway] Consultando citas de paciente", flush=True)
    params = {"id_paciente": request.args.get("id_paciente")}
    try:
        response = requests.get(
            "http://citas:5000/citas_paciente", params=params, timeout=3
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        print("[Gateway] Error: Servicio de citas caido", flush=True)
        return jsonify({"error": "Servicio de citas no disponible"}), 503


@app.route("/citas/cancelar/<int:id_citas>", methods=["PUT"])
def cancelar_cita(id_citas):
    print(f"[Gateway] Solicitando cancelación de cita {id_citas}", flush=True)
    try:
        response = requests.put(f"http://citas:5000/cancelar/{id_citas}", timeout=3)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        print("[Gateway] Error: Servicio de citas caido al cancelar", flush=True)
        return jsonify({"error": "Servicio de citas no disponible"}), 503


@app.route("/citas/reprogramar/<int:id_citas>", methods=["PUT"])
def reprogramar_cita(id_citas):
    print(f"[Gateway] Solicitando reprogramación de cita {id_citas}", flush=True)
    try:
        response = requests.put(
            f"http://citas:5000/reprogramar/{id_citas}", json=request.json, timeout=3
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        print("[Gateway] Error: Servicio de citas caido al reprogramar", flush=True)
        return jsonify({"error": "Servicio de citas no disponible"}), 503


# RUTAS HACIA SERVICIOS HISTORIAL


@app.route("/historial/<int:id_usuario>", methods=["GET"])
def get_historial(id_usuario):
    print(f"[Gateway] Consultando historial usuario {id_usuario}", flush=True)
    try:
        response = requests.get(
            f"http://historial:5000/historial/{id_usuario}", timeout=3
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        print("[Gateway] Error: Servicio de historial caido", flush=True)
        return jsonify({"error": "Servicio de historial no disponible"}), 503


@app.route("/historial", methods=["POST"])
def post_historial():
    print("[Gateway] Agregando nota manual a historial", flush=True)
    try:
        response = requests.post(
            "http://historial:5000/historial", json=request.json, timeout=3
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        print("[Gateway] Error: Servicio de historial caido", flush=True)
        return jsonify({"error": "Servicio de historial no disponible"}), 503


# RUTAS HACIA SERVICIOS NOTIFICACIONES


@app.route("/notificaciones/<int:id_usuario>", methods=["GET"])
def get_notificaciones(id_usuario):
    print(f"[Gateway] Consultando notificaciones usuario {id_usuario}", flush=True)
    try:
        response = requests.get(
            f"http://notificaciones:5000/notificaciones/{id_usuario}", timeout=3
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        print("[Gateway] Error: Servicio de notificaciones caido", flush=True)
        return jsonify({"error": "Servicio de notificaciones no disponible"}), 503


@app.route("/notificaciones/marcar-leidas/<int:id_usuario>", methods=["PUT"])
def marcar_leidas(id_usuario):
    print(
        f"[Gateway] Marcando notificaciones como leidas usuario {id_usuario}",
        flush=True,
    )
    try:
        response = requests.put(
            f"http://notificaciones:5000/notificaciones/marcar-leidas/{id_usuario}",
            timeout=3,
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        print("[Gateway] Error: Servicio de notificaciones caido", flush=True)
        return jsonify({"error": "Servicio de notificaciones no disponible"}), 503


# ESTADO Y MONITOREO


@app.route("/estado/autenticacion", methods=["GET"])
def estado_autenticacion():
    global fallos_health_autenticacion
    inicio = time()
    try:
        response = requests.get("http://autenticacion:5000/health", timeout=2)
        fallos_health_autenticacion = 0
        return jsonify(response.json())
    except Exception as e:
        fallos_health_autenticacion += 1
        print(f"[Gateway] Fallo health autenticacion: {e}", flush=True)
        return jsonify({"status": "Caido", "service": "Autenticacion"}), 503
    finally:
        print(
            f"[Gateway] Tiempo respuesta Autenticacion: {time() - inicio:.4f}s",
            flush=True,
        )


@app.route("/estado/citas", methods=["GET"])
def estado_citas():
    global fallos_health_citas
    inicio = time()
    try:
        response = requests.get("http://citas:5000/health", timeout=2)
        fallos_health_citas = 0
        return jsonify(response.json())
    except Exception as e:
        fallos_health_citas += 1
        print(f"[Gateway] Fallo health citas: {e}", flush=True)
        return jsonify({"status": "Caido", "service": "Citas"}), 503
    finally:
        print(f"[Gateway] Tiempo respuesta Citas: {time() - inicio:.4f}s", flush=True)


@app.route("/estado/historial", methods=["GET"])
def estado_historial():
    global fallos_health_historial
    inicio = time()
    try:
        response = requests.get("http://historial:5000/health", timeout=2)
        fallos_health_historial = 0
        return jsonify(response.json())
    except Exception as e:
        fallos_health_historial += 1
        print(f"[Gateway] Fallo health historial: {e}", flush=True)
        return jsonify({"status": "Caido", "service": "Historial"}), 503
    finally:
        print(
            f"[Gateway] Tiempo respuesta Historial: {time() - inicio:.4f}s", flush=True
        )


@app.route("/estado/notificaciones", methods=["GET"])
def estado_notificaciones():
    global fallos_health_notificaciones
    inicio = time()
    try:
        response = requests.get("http://notificaciones:5000/health", timeout=2)
        fallos_health_notificaciones = 0
        return jsonify(response.json())
    except Exception as e:
        fallos_health_notificaciones += 1
        print(f"[Gateway] Fallo health notificaciones: {e}", flush=True)
        return jsonify({"status": "Caido", "service": "Notificaciones"}), 503
    finally:
        print(
            f"[Gateway] Tiempo respuesta Notificaciones: {time() - inicio:.4f}s",
            flush=True,
        )


@app.route("/monitoreo", methods=["GET"])
def monitoreo():
    print("[Gateway] Verificando estado de microservicios", flush=True)
    resultados = {}
    for nombre, url in servicios.items():
        try:
            resp = requests.get(url, timeout=2)
            resultados[nombre] = {"status": "OK", "http": resp.status_code}
        except:
            resultados[nombre] = {"status": "Caido"}
    return jsonify(resultados)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
