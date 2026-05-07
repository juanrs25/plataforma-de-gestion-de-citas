from flask import Flask, request, jsonify

app = Flask(__name__)

db_usuarios = [{"id": 1, "nombre": "Axl"}, {"id": 2, "nombre": "Carl"}]


@app.route("/")
def inicio():
    return "Funcionando usuarios"


@app.route("/usuarios")
def usuarios():
    return jsonify(db_usuarios)

# Reto

@app.route("/usuarios/<int:id>")
def obtener_usuario(id):
    
    usuarios = next((usuario for usuario in db_usuarios if usuario["id"] == id), None)
    if usuarios:
        return jsonify(usuarios)
    else:
        return jsonify({"error": "Usuario no encontrado"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
