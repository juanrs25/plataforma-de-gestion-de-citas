
from flask import Flask
import requests 
from flask import Flask, request, jsonify

app = Flask(__name__)

productos = [
    {
        "id": 1,
        "nombre": "Laptop",
        "stock": 10,
        "precio": 3500
    },
    {
        "id": 2,
        "nombre": "Mouse",
        "stock": 25,
        "precio": 80
    },
    {
        "id": 3,
        "nombre": "Teclado",
        "stock": 15,
        "precio": 150
    }
]

@app.route("/")
def home():
    return "Servicio de Inventario funcionando"

@app.route("/health")
def health():

    print(
        "Health check solicitado en inventario",
        flush=True
    )

    return {
        "status": "ok",
        "servicio": "inventario"
    }
@app.route("/inventario")
def inventario():

    print(
        "Solicitud recibida en endpoint /inventario",
        flush=True
    )

    print(
        f"Cantidad de productos enviados: {len(productos)}",
        flush=True
    )

    print(
        "Respuesta",
        flush=True
    )

    return jsonify(productos)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)