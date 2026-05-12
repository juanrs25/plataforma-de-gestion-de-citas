from flask import Flask, request, jsonify


app=Flask(__name__)
@app.route("/usuarios")
def usuarios():
    return jsonify([
        {"id":1, "nombre": "Juan"},
        {"id":2, "nombre": "Manuel"},
        {"id": 3, "nombre": "Maria"}

    ])
@app.route("/usuarios/<int:id_usuario>", methods=["GET"])
def obtener_usuarios(id_usuario):
    if id_usuario == 1:
        return jsonify({"id": 1, "nombre": "Juan"})
    elif id_usuario == 2:
        return jsonify({"id": 2, "nombre": "Manuel"})
    elif id_usuario == 3:
        return jsonify({"id": 3, "nombre": "Maria"})
    else:
        return jsonify({"error": "Usuario no encontrado"}), 404
    
    

if __name__== "__main__":
    app.run(host="0.0.0.0", port=5000)