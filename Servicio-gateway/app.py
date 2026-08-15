from flask import Flask, request, jsonify
import requests
import time

app = Flask(__name__)

# ==============================================================================
# VARIABLES DEL CIRCUIT BREAKER
# ==============================================================================
circuitos = {
    "autenticacion": {"fallos": 0, "estado": "cerrado", "tiempo_apertura": 0},
    "citas":         {"fallos": 0, "estado": "cerrado", "tiempo_apertura": 0},
    "historial":     {"fallos": 0, "estado": "cerrado", "tiempo_apertura": 0},
    "notificaciones":{"fallos": 0, "estado": "cerrado", "tiempo_apertura": 0}
}

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


# ==============================================================================
# LÓGICA CENTRAL DEL CIRCUIT BREAKER Y HALF-OPEN
# ==============================================================================
def enviar_peticion(servicio, metodo, url, **kwargs):

    estado_actual = circuitos[servicio]["estado"]
    tiempo_apertura = circuitos[servicio]["tiempo_apertura"]

    # =========================
    # VALIDAR ESTADO DEL CIRCUITO
    # =========================
    if estado_actual == "Abierto":

        tiempo_transcurrido = time.time() - tiempo_apertura

        # Si ya pasaron 10 segundos -> HALF_OPEN
        if tiempo_transcurrido > 10:

            circuitos[servicio]["estado"] = "HALF_OPEN"

            print(
                f"[Gateway] {servicio} entrando en estado HALF_OPEN. "
                f"Intentando reconexión al servicio...",
                flush=True
            )

        else:

            tiempo_restante = 10 - tiempo_transcurrido

            print(
                f"[Gateway] Circuito ABIERTO en {servicio}. "
                f"Esperando {tiempo_restante:.1f}s para intentar nuevamente.",
                flush=True
            )

            return {
                "error": f"Servicio de {servicio} temporalmente no disponible",
            }, 503

    # =========================
    # INTENTAR PETICIÓN
    # =========================
    try:

        inicio = time.time()

        kwargs.setdefault("timeout", 3)

        response = requests.request(
            metodo,
            url,
            **kwargs
        )

        tiempo_respuesta = time.time() - inicio

        print(
            f"[Gateway] Datos obtenidos exitosamente de {servicio}",
            flush=True
        )

        # Reiniciar contador de fallos
        circuitos[servicio]["fallos"] = 0

        # =========================
        # SI ESTABA EN HALF_OPEN
        # =========================
        if circuitos[servicio]["estado"] == "HALF_OPEN":

            print(
                f"[Gateway] {servicio} respondió correctamente en HALF_OPEN. "
                f"Cerrando circuito...",
                flush=True
            )

            circuitos[servicio]["estado"] = "cerrado"

            print(
                f"[Gateway] Circuito cerrado nuevamente para {servicio}",
                flush=True
            )

        print(
            f"[Gateway] Tiempo respuesta {servicio}: "
            f"{tiempo_respuesta:.4f}s",
            flush=True
        )

        try:
            return response.json(), response.status_code

        except ValueError:
            return response.text, response.status_code

    # =========================
    # MANEJO DE ERRORES
    # =========================
    except requests.exceptions.RequestException as e:

        circuitos[servicio]["fallos"] += 1

        print(
            f"[Gateway] Fallo en {servicio} numero "
            f"{circuitos[servicio]['fallos']}. "
            f"Detalle: {e}",
            flush=True
        )

        # =========================
        # FALLÓ EN HALF_OPEN
        # =========================
        if circuitos[servicio]["estado"] == "HALF_OPEN":

            print(
                f"[Gateway] {servicio} falló en estado HALF_OPEN. "
                f"Reabriendo circuito...",
                flush=True
            )

        # =========================
        # ABRIR CIRCUITO
        # =========================
        if (
            circuitos[servicio]["estado"] == "HALF_OPEN"
            or circuitos[servicio]["fallos"] >= 3
        ):

            circuitos[servicio]["estado"] = "Abierto"

            circuitos[servicio]["tiempo_apertura"] = time.time()

            print(
                f"[Gateway] Circuito ABIERTO en {servicio}",
                flush=True
            )

        return {
            "error": f"Servicio de {servicio} no disponible"
        }, 503

# ==============================================================================
# RUTAS DE SERVICIOS 
# ==============================================================================

@app.route("/")
def home():
    return "API GATEWAY FUNCIONANDO"

# --- AUTENTICACIÓN ---
@app.route("/usuarios/listar", methods=["GET"])
def listar_usuarios():
    print("[Gateway] Solicitando lista de usuarios", flush=True)
    data, status = enviar_peticion("autenticacion", "GET", "http://autenticacion:5000/listar")
    return jsonify(data), status

@app.route("/usuarios/registro", methods=["POST"])
def registro_usuario():
    print("[Gateway] Procesando registro de usuario", flush=True)
    data, status = enviar_peticion("autenticacion", "POST", "http://autenticacion:5000/registro", json=request.json)
    return jsonify(data), status

@app.route("/usuarios/login", methods=["POST"])
def login_usuario():
    print("[Gateway] Procesando login", flush=True)
    data, status = enviar_peticion("autenticacion", "POST", "http://autenticacion:5000/login", json=request.json)
    return jsonify(data), status


# --- CITAS ---

@app.route("/citas/disponibilidad", methods=["GET"])
def consultar_disponibilidad_gateway():
    print("[Gateway] Consultando disponibilidad de doctor", flush=True)

    params = {
        "id_doctor": request.args.get("id_doctor"),
        "fecha": request.args.get("fecha"),
    }

    data, status = enviar_peticion(
        "citas",
        "GET",
        "http://citas:5000/disponibilidad",
        params=params
    )

    return jsonify(data), status
@app.route("/citas/agendar", methods=["POST"])
def agendar_cita():
    print("[Gateway] Agendando cita", flush=True)
    data, status = enviar_peticion("citas", "POST", "http://citas:5000/agendar", json=request.json)
    return jsonify(data), status

@app.route("/citas/paciente", methods=["GET"])
def citas_por_paciente():
    print("[Gateway] Consultando citas de paciente", flush=True)
    params = {"id_paciente": request.args.get("id_paciente")}
    data, status = enviar_peticion("citas", "GET", "http://citas:5000/citas_paciente", params=params)
    return jsonify(data), status

@app.route("/citas/cancelar/<int:id_citas>", methods=["PUT"])
def cancelar_cita(id_citas):
    print(f"[Gateway] Solicitando cancelación de cita {id_citas}", flush=True)
    data, status = enviar_peticion("citas", "PUT", f"http://citas:5000/cancelar/{id_citas}")
    return jsonify(data), status

@app.route("/citas/reprogramar/<int:id_citas>", methods=["PUT"])
def reprogramar_cita(id_citas):
    print(f"[Gateway] Solicitando reprogramación de cita {id_citas}", flush=True)
    data, status = enviar_peticion("citas", "PUT", f"http://citas:5000/reprogramar/{id_citas}", json=request.json)
    return jsonify(data), status


# --- HISTORIAL ---
@app.route("/historial/<int:id_usuario>", methods=["GET"])
def get_historial(id_usuario):
    print(f"[Gateway] Consultando historial usuario {id_usuario}", flush=True)
    data, status = enviar_peticion("historial", "GET", f"http://historial:5000/historial/{id_usuario}")
    return jsonify(data), status

@app.route("/historial", methods=["POST"])
def post_historial():
    print("[Gateway] Agregando nota manual a historial", flush=True)
    data, status = enviar_peticion("historial", "POST", "http://historial:5000/historial", json=request.json)
    return jsonify(data), status


# --- NOTIFICACIONES ---
@app.route("/notificaciones/<int:id_usuario>", methods=["GET"])
def get_notificaciones(id_usuario):
    print(f"[Gateway] Consultando notificaciones usuario {id_usuario}", flush=True)
    data, status = enviar_peticion("notificaciones", "GET", f"http://notificaciones:5000/notificaciones/{id_usuario}")
    return jsonify(data), status

@app.route("/notificaciones/marcar-leidas/<int:id_usuario>", methods=["PUT"])
def marcar_leidas(id_usuario):
    print(f"[Gateway] Marcando notificaciones como leidas usuario {id_usuario}", flush=True)
    data, status = enviar_peticion("notificaciones", "PUT", f"http://notificaciones:5000/notificaciones/marcar-leidas/{id_usuario}")
    return jsonify(data), status




# ==============================================================================
# ESTADOS Y MONITOREO 
# ==============================================================================

@app.route("/estado/notificaciones", methods=["GET"])
def estado_notificaciones():
    global fallos_health_notificaciones
    inicio = time.time()
    try:
        response = requests.get("http://notificaciones:5000/health", timeout=2)
        fallos_health_notificaciones = 0
        return jsonify(response.json())
    except Exception as e:
        fallos_health_notificaciones += 1
        print(f"[Gateway] Fallo health notificaciones: {e}", flush=True)
        return jsonify({"status": "Caido", "service": "Notificaciones"}), 503
    finally:
        print(f"[Gateway] Tiempo respuesta Notificaciones: {time.time() - inicio:.4f}s", flush=True)

@app.route("/estado/autenticacion", methods=["GET"])
def estado_autenticacion():
    global fallos_health_autenticacion
    inicio = time.time()
    try:
        response = requests.get("http://autenticacion:5000/health", timeout=2)
        fallos_health_autenticacion = 0
        return jsonify(response.json())
    except Exception as e:
        fallos_health_autenticacion += 1
        print(f"[Gateway] Fallo health autenticacion: {e}", flush=True)
        return jsonify({"status": "Caido", "service": "Autenticacion"}), 503
    finally:
        print(f"[Gateway] Tiempo respuesta Autenticacion: {time.time() - inicio:.4f}s", flush=True)


@app.route("/estado/citas", methods=["GET"])
def estado_citas():
    global fallos_health_citas
    inicio = time.time()
    try:
        response = requests.get("http://citas:5000/health", timeout=2)
        fallos_health_citas = 0
        return jsonify(response.json())
    except Exception as e:
        fallos_health_citas += 1
        print(f"[Gateway] Fallo health citas: {e}", flush=True)
        return jsonify({"status": "Caido", "service": "Citas"}), 503
    finally:
        print(f"[Gateway] Tiempo respuesta Citas: {time.time() - inicio:.4f}s", flush=True)
        
@app.route("/estado/historial", methods=["GET"])
def estado_historial():
    global fallos_health_historial
    inicio = time.time()
    try:
        response = requests.get("http://historial:5000/health", timeout=2)
        fallos_health_historial = 0
        return jsonify(response.json())
    except Exception as e:
        fallos_health_historial += 1
        print(f"[Gateway] Fallo health historial: {e}", flush=True)
        return jsonify({"status": "Caido", "service": "Historial"}), 503
    finally:
        print(f"[Gateway] Tiempo respuesta Historial: {time.time() - inicio:.4f}s", flush=True)

@app.route("/monitoreo", methods=["GET"])
def monitoreo():

    resultados = {}

    nombres_circuito = {
        "Autenticacion": "autenticacion",
        "Citas": "citas",
        "Historial": "historial",
        "Notificaciones": "notificaciones"
    }

    for nombre, url in servicios.items():

        servicio_cb = nombres_circuito[nombre]

        inicio = time.time()

        try:

            response = requests.get(
                url,
                timeout=2
            )

            fin = time.time()

            tiempo_respuesta = fin - inicio

            resultados[nombre] = {
                "http": response.status_code,
                "status": "OK",
                "tiempo_respuesta": f"{tiempo_respuesta:.4f}s",
                "fallos": circuitos[servicio_cb]["fallos"],
                "estado_circuito": circuitos[servicio_cb]["estado"]
            }

        except Exception:

            fin = time.time()

            tiempo_respuesta = fin - inicio

            resultados[nombre] = {
                "status": "Caido",
                "tiempo_respuesta": f"{tiempo_respuesta:.4f}s",
                "fallos": circuitos[servicio_cb]["fallos"],
                "estado_circuito": circuitos[servicio_cb]["estado"]
            }

    return jsonify(resultados)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)