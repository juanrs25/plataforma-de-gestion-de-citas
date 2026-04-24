from flask import Flask, request, jsonify
import requests

app = Flask(__name__)


# RUTAS HACIA EL SERVICIO DE AUTENTICACIÓN


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
    params = {"id_doctor": id_doctor} if id_doctor else {}

    try:
        response = requests.get(
            "http://citas:5000/disponibilidad", params=params, timeout=3
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        print(
            "[Gateway] ¡ERROR! Servicio de citas caído o no responde al consultar disponibilidad",
            flush=True,
        )
        return jsonify({"error": "Servicio de citas no disponible"}), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
