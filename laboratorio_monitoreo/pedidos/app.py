from flask import Flask
import requests 
from flask import Flask, request, jsonify

app = Flask(__name__)

pedidos = [
    {
        "pedido_id": 101,
        "cliente": "Juan",
        "producto": "Laptop",
        "cantidad": 1,
        "estado": "en proceso"
    },
    {
        "pedido_id": 102,
        "cliente": "Maria",
        "producto": "Mouse",
        "cantidad": 2,
        "estado": "enviado"
    },
    {
        "pedido_id": 103,
        "cliente": "Carlos",
        "producto": "Teclado",
        "cantidad": 1,
        "estado": "entregado"
    }
]

@app.route("/")
def home():
    return "Servicio de Pedidos funcionando"

@app.route("/health")
def health():

    print(
        "Health check solicitado en pedidos",
        flush=True
    )

    return {
        "status": "ok",
        "servicio": "pedidos"
    }

@app.route("/pedidos")
def obtener_pedidos():

    print(
        "Solicitud recibida en endpoint /pedidos",
        flush=True
    )

    print(
        f"Cantidad de productos enviados: {len(pedidos)}",
        flush=True
    )

    print(
        "Respuesta",
        flush=True
    )

    return jsonify(pedidos)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)