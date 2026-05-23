from flask import Flask, request, jsonify
import mysql.connector
import os

app = Flask(__name__)


# CONFIGURACION DE BASE DE DATOS


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("AUTH_DB_HOST"),
        user=os.getenv("AUTH_DB_USER"),
        password=os.getenv("AUTH_DB_PASSWORD"),
        database=os.getenv("AUTH_DB_NAME"),
    )


# ENDPOINTS


@app.route("/")
def login():
    print(
        "[SERVICIO-AUTENTICACION] Solicitud recibida en endpoint raíz (/)", flush=True
    )
    return "Servicio de autenticación funcionando"


@app.route("/test-db")
def test_db():
    print(
        "[SERVICIO-AUTENTICACION] Solicitud recibida para prueba de base de datos (/test-db)",
        flush=True,
    )
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        print("[SERVICIO-AUTENTICACION] Prueba de BD exitosa", flush=True)
        return f"Conexión exitosa a bd de autenticacion: {result}"
    except Exception as e:
        print(f"[SERVICIO-AUTENTICACION] Error en prueba de BD: {str(e)}", flush=True)
        return f"Error de conexión: {str(e)}"


@app.route("/login", methods=["POST"])
def login_user():
    print(
        "[SERVICIO-AUTENTICACION] Solicitud recibida para inicio de sesión (/login)",
        flush=True,
    )
    data = request.json

    correo_usuario = data.get("correo_usuario")
    password_usuario = data.get("password_usuario")

    if not correo_usuario or not password_usuario:
        print("[SERVICIO-AUTENTICACION] Error: Credenciales incompletas", flush=True)
        return jsonify({"Error": "Correo y contraseña son obligatorios"}), 400

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM usuarios WHERE correo_usuario = %s AND password_usuario = %s",
            (correo_usuario, password_usuario),
        )

        user = cursor.fetchone()

        if user:
            print(
                f"[SERVICIO-AUTENTICACION] Usuario '{user[1]}' inició sesión correctamente",
                flush=True,
            )
            return jsonify({"Exitoso": "Login exitoso"}), 200
        else:
            print("[SERVICIO-AUTENTICACION] Error: Credenciales erróneas", flush=True)
            return jsonify({"Error": "Credenciales erróneas"}), 401
    except Exception as e:
        print(f"[SERVICIO-AUTENTICACION] Error en login: {str(e)}", flush=True)
        return jsonify({"Error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/registro", methods=["POST"])
def register_user():
    print(
        "[SERVICIO-AUTENTICACION] Solicitud recibida para registro de usuario (/registro)",
        flush=True,
    )
    data = request.json

    nombre_usuario = data.get("nombre_usuario")
    password_usuario = data.get("password_usuario")
    correo_usuario = data.get("correo_usuario")
    telefono_usuario = data.get("telefono_usuario")
    direccion_usuario = data.get("direccion_usuario")

    if not nombre_usuario or not password_usuario or not correo_usuario:
        print(
            "[SERVICIO-AUTENTICACION] Error: Datos obligatorios faltantes", flush=True
        )
        return jsonify({"Error": "Nombre, correo y contraseña son obligatorios"}), 400

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO usuarios (nombre_usuario, password_usuario, correo_usuario, telefono_usuario, direccion_usuario) 
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                nombre_usuario,
                password_usuario,
                correo_usuario,
                telefono_usuario,
                direccion_usuario,
            ),
        )

        conn.commit()

        print(
            f"[SERVICIO-AUTENTICACION] Usuario '{nombre_usuario}' registrado correctamente",
            flush=True,
        )
        return jsonify({"Exitoso": "Usuario registrado exitosamente"}), 201

    except Exception as e:
        print(
            f"[SERVICIO-AUTENTICACION] Error al registrar usuario '{nombre_usuario}': {str(e)}",
            flush=True,
        )
        return jsonify({"Error": str(e)}), 400
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/listar", methods=["GET"])
def list_users():
    print(
        "[SERVICIO-AUTENTICACION] Solicitud recibida para listar usuarios (/listar)",
        flush=True,
    )
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_usuario, nombre_usuario, rol_usuario FROM usuarios")
        users = cursor.fetchall()

        user_list = [
            {"id_usuario": user[0], "nombre_usuario": user[1], "rol_usuario": user[2]}
            for user in users
        ]

        print(
            f"[SERVICIO-AUTENTICACION] Listado exitoso. Total usuarios: {len(user_list)}",
            flush=True,
        )
        return jsonify(user_list), 200
    except Exception as e:
        print(
            f"[SERVICIO-AUTENTICACION] Error al listar usuarios: {str(e)}", flush=True
        )
        return jsonify({"Error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Este endpoint sera usado internamente por citas para verificar al doctor
@app.route("/usuarios/<int:id_usuario>", methods=["GET"])
def obtenerUsuarioID(id_usuario):
    print(
        f"[SERVICIO-AUTENTICACION] Solicitud recibida para obtener usuario ID {id_usuario}",
        flush=True,
    )
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_usuario, nombre_usuario, rol_usuario FROM usuarios WHERE id_usuario = %s",
            (id_usuario,),
        )
        user = cursor.fetchone()

        if user:
            print(
                f"[SERVICIO-AUTENTICACION] Usuario ID {id_usuario} encontrado",
                flush=True,
            )
            return (
                jsonify(
                    {
                        "id_usuario": user[0],
                        "nombre_usuario": user[1],
                        "rol_usuario": user[2],
                    }
                ),
                200,
            )
        else:
            print(
                f"[SERVICIO-AUTENTICACION] Usuario ID {id_usuario} no encontrado",
                flush=True,
            )
            return jsonify({"error": "Usuario no encontrado"}), 404
    except Exception as e:
        print(f"[SERVICIO-AUTENTICACION] Error al buscar usuario: {str(e)}", flush=True)
        return jsonify({"Error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/health")
def health():
    print("[SERVICIO-AUTENTICACION] Health check solicitado", flush=True)
    return jsonify({"status": "ok", "servicio": "Autenticacion"}), 200


# INICIO DE LA APLICACION

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
