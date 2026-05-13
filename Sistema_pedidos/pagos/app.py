from flask import Flask
import requests 
from flask import Flask, request, jsonify
app = Flask(__name__)
pagos = [
    {
        "id_pago": 1,
        "pedido_id": 101,
        "estado": "aprobado",
        "metodo": "tarjeta",
        "valor": 250000
    },
    {
        "id_pago": 2,
        "pedido_id": 102,
        "estado": "pendiente",
        "metodo": "nequi",
        "valor": 80000
    },
    {
        "id_pago": 3,
        "pedido_id": 103,
        "estado": "rechazado",
        "metodo": "paypal",
        "valor": 120000
    }
]


@app.route("/")
def home():
    return "Servicio de Pagos funcionando"

@app.route("/health")
def health():

    print(
        "Health check solicitado en pagos",
        flush=True
    )

    return {
        "status": "ok",
        "servicio": "pagos"
    }
@app.route("/pagos")
def obtener_pagos():

    print(
        "Solicitud recibida en endpoint /pagos",
        flush=True
    )

    print(
        f"Cantidad de productos enviados: {len(pagos)}",
        flush=True
    )

    print(
        "Respuesta",
        flush=True
    )

    return jsonify(pagos)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)