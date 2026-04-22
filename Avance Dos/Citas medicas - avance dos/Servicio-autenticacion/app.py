from ast import If

from flask import Flask, request, jsonify
import mysql.connector
import requests
import os

app = Flask(__name__)


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("AUTH_DB_HOST"),
        user=os.getenv("AUTH_DB_USER"),
        password=os.getenv("AUTH_DB_PASSWORD"),
        database=os.getenv("AUTH_DB_NAME"),
    )


@app.route("/")
def login():
    return "Servicio de autenticación funcionando"


@app.route("/test-db")
def test_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return f"Conexión exitosa a bd de autenticacion: {result}"
    except Exception as e:
        return f"Error de conexión: {str(e)}"


@app.route("/login", methods=["POST"])
def login_user():
    data = request.json
    correo_usuario = data.get("correo_usuario")
    password_usuario = data.get("password_usuario")
    Connection = get_db_connection()
    cursor = Connection.cursor()
    cursor.execute(
        "SELECT * FROM usuarios WHERE correo_usuario = %s AND password_usuario = %s",
        (correo_usuario, password_usuario),
    )
    user = cursor.fetchone()
    cursor.close()
    Connection.close()

    if user:
        return {"Exitoso": "Login exitoso"}
    else:
        return {"Error": "Credenciales erroneas"}, 401


@app.route("/registro", methods=["POST"])
def register_user():
    data = request.json
    nombre_usuario = data.get("nombre_usuario")
    password_usuario = data.get("password_usuario")
    correo_usuario = data.get("correo_usuario")
    telefono_usuario = data.get("telefono_usuario")
    direccion_usuario = data.get("direccion_usuario")
    Connection = get_db_connection()
    cursor = Connection.cursor()

    try:
        cursor.execute(
            "INSERT INTO usuarios (nombre_usuario, password_usuario,correo_usuario, telefono_usuario,direccion_usuario) VALUES (%s, %s, %s, %s,%s)",
            (
                nombre_usuario,
                password_usuario,
                correo_usuario,
                telefono_usuario,
                direccion_usuario,
            ),
        )
        Connection.commit()
        return {"Exitoso": "Usuario registrado exitosamente"}
    except Exception as e:
        return {"Error": str(e)}, 400
    finally:
        cursor.close()
        Connection.close()


@app.route("/listar", methods=["GET"])
def list_users():
    Connection = get_db_connection()
    cursor = Connection.cursor()
    cursor.execute("SELECT id_usuario, nombre_usuario, rol_usuario FROM usuarios")
    users = cursor.fetchall()
    cursor.close()
    Connection.close()

    user_list = [
        {"id_usuario": user[0], "nombre_usuario": user[1], "rol_usuario": user[2]}
        for user in users
    ]
    return jsonify(user_list)


# Este ees el endpint que hara se comunica con el servicio de citas


@app.route("/disponibilidad", methods=["GET"])
def ver_disponibilidad():
    # en el json no olvidar que enviamos el id de doctor sino no funciona xd
    id_doctor = request.args.get("id_doctor")

    params = {}
    if id_doctor:
        params["id_doctor"] = id_doctor

    try:
        #    aca es llamamos al endpoin interno c:
        respuesta = requests.get(
            "http://citas:5000/disponibilidad", params=params, timeout=3
        )
        respuesta.raise_for_status()

        datos = respuesta.json()

        return (
            jsonify(
                {
                    "mensaje": "Consulta exitosa desde Autenticación",
                    "datos_citas": datos,
                }
            ),
            200,
        )

    except requests.exceptions.RequestException as e:
        #  manejo de errors
        return (
            jsonify(
                {
                    "Error": "Servicio de gestión de citas temporalmente no disponible.",
                    "Detalle_tecnico": str(e),
                }
            ),
            503,
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
