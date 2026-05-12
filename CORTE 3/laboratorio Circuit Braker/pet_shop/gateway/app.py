from flask import Flask, request, jsonify
import requests 
import time

app = Flask(__name__)



##para mascotas
fallos_backend = 0
circuito_abierto= False
tiempo_espera = 10
momento_apertura = 0
half_open = False

#para usuarios

fallos_usuarios = 0
circuito_usuarios_abierto = False
tiempo_espera_usuarios = 10
momento_apertura_usuarios = 0
half_open_usuarios = False


@app.route("/usuarios")
def usuarios():

    global fallos_usuarios
    global circuito_usuarios_abierto

    global momento_apertura_usuarios
    global half_open_usuarios


    if circuito_usuarios_abierto:

        tiempo_actual = time.time()

        if tiempo_actual - momento_apertura_usuarios >= tiempo_espera_usuarios:

            print(
                "Usuarios pasando a HALF-OPEN",
                flush=True
            )

            circuito_usuarios_abierto = False
            half_open_usuarios = True

        else:

            return jsonify({
                "error": "Servicio usuarios caido, espere unos segundos"
            }), 503

  

    try:

        response = requests.get(
            "http://usuarios:5000/usuarios",
            timeout=2
        )

        

        if half_open_usuarios:

            print(
                "Servicio usuarios recuperado - circuito cerrado",
                flush=True
            )

            half_open_usuarios = False

        fallos_usuarios = 0

        return jsonify(response.json())

    except:

        fallos_usuarios += 1

        print(
            f"Fallo usuarios numero {fallos_usuarios}",
            flush=True
        )

        

        if half_open_usuarios:

            print(
                "Half-open usuarios fallo - circuito abierto nuevamente",
                flush=True
            )

            circuito_usuarios_abierto = True
            half_open_usuarios = False

            momento_apertura_usuarios = time.time()

   

        elif fallos_usuarios >= 3:

            circuito_usuarios_abierto = True

            momento_apertura_usuarios = time.time()

            print(
                "Circuito usuarios abierto",
                flush=True
            )

        return jsonify({
            "error": "Servicio usuarios no disponible"
        }), 503

@app.route("/mascotas")
def mascotas():

    global fallos_backend
    global circuito_abierto
    global momento_apertura
    global half_open

   

    if circuito_abierto:

        tiempo_actual = time.time()

        # revisar si ya pasó el tiempo de espera
        if tiempo_actual - momento_apertura >= tiempo_espera:

            print(
                "Pasando a HALF-OPEN",
                flush=True
            )

            circuito_abierto = False
            half_open = True

        else:
            return jsonify({
                "error": "Circuito abierto, espere unos segundos"
            }), 503

   
    try:

        response = requests.get(
            "http://backend:5000/mascotas",
            timeout=2
        )

        

        if half_open:

            print(
                "Servicio recuperado - circuito cerrado",
                flush=True
            )

            half_open = False

        fallos_backend = 0

        return jsonify(response.json())

    except:

        fallos_backend += 1

        print(
            f"Fallo numero {fallos_backend}",
            flush=True
        )

      
        if half_open:

            print(
                "Half-open fallo - circuito abierto nuevamente",
                flush=True
            )

            circuito_abierto = True
            half_open = False
            momento_apertura = time.time()

        
        elif fallos_backend >= 3:

            circuito_abierto = True
            momento_apertura = time.time()

            print(
                "Circuito abierto",
                flush=True
            )

        return jsonify({
            "error": "Servicio no disponible"
        }), 503



fallos_usuarios = 0
circuito_usuarios_abierto = False


@app.route("/resumen")
def resumen():

    global fallos_backend
    global circuito_abierto

    global fallos_usuarios
    global circuito_usuarios_abierto

    data = {}


    if circuito_usuarios_abierto:

        print(
            "Circuito usuarios abierto",
            flush=True
        )

        data["Error"] = "Servicio usuarios temporalmente no disponible"

    else:
        try:
            response_usuarios = requests.get(
                "http://usuarios:5000/usuarios",
                timeout=2
            )

            usuarios_data = response_usuarios.json()

           
            fallos_usuarios = 0

            data["usuarios"] = usuarios_data

        except:

            fallos_usuarios += 1

            print(
                f"Fallo usuarios numero {fallos_usuarios}",
                flush=True
            )

            if fallos_usuarios >= 3:
                circuito_usuarios_abierto = True

                print(
                    "Circuito usuarios abierto por fallos repetidos",
                    flush=True
                )

            data["Error"] = "Servicio usuarios no disponible"


    if circuito_abierto:

        print(
            "Circuito mascotas abierto",
            flush=True
        )

        data["Error"] = "Servicio mascotas temporalmente no disponible"

    else:
        try:
            response_mascotas = requests.get(
                "http://backend:5000/mascotas",
                timeout=2
            )

            mascotas_data = response_mascotas.json()

            # Reiniciar fallos si funciona
            fallos_backend = 0

            data["mascotas"] = mascotas_data

        except:

            fallos_backend += 1

            print(
                f"Fallo mascotas numero {fallos_backend}",
                flush=True
            )

            if fallos_backend >= 3:
                circuito_abierto = True

                print(
                    "Circuito mascotas abierto por fallos repetidos",
                    flush=True
                )

            data["Error"] = "Servicio mascotas no disponible"

    return jsonify(data)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)