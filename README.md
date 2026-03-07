# PROTOTIPO TÉCNICO INICIAL


## Información del Proyecto

### Descripción
Este proyecto contiene un **prototipo técnico inicial** que levanta **dos servicios web** usando **Docker Compose**.  
Cada servicio expone una interfaz HTML estática servida por **Nginx** dentro de su contenedor.

### Servicios incluidos
-  **Servicio de Autenticación**
  - Páginas: `login.html`, `registro.html`
  - Puerto: `8081`
-  **Servicio de Historial**
  - Página: `History.html`
  - Puerto: `8082`

---

##  Estructura del proyecto

    Sistemas_D
    │ 
    ├── Servicio-autenticacion

    │   ├── Dockerfile

    │   └── sitio

    │       ├── login.html

    │       └── registro.html

    ├── Servicio-historial

    │   ├── Dockerfile

    │   └── sitio

    │       └── History.html

    └── docker-compose.yml



---

## Requisitos

Antes de ejecutar el proyecto, asegúrate de tener instalado:

- **Docker**
- **Docker Compose**

---

## Cómo ejecutar el proyecto

### 1) Ir a la carpeta raíz
Ubícate en la carpeta donde está `docker-compose.yml`:


### 2) Construir y levantar servicios
Ejecuta:

`docker compose up -d --build`


### ¿Qué hace este comando?
- **Construye** las imágenes de los servicios
- **Crea y levanta** los contenedores
- Deja los servicios corriendo en **segundo plano** (`-d`)

---

## Acceso a los servicios

Cuando todo esté arriba, abre en tu navegador:

### Servicio de Autenticación
- **Login:** `http://localhost:8081/login.html`
- **Registro:** `http://localhost:8081/registro.html`

### Servicio de Historial
- **Historial:** `http://localhost:8082/History.html`

---

## Docker Compose (docker-compose.yml)

    services:

      autenticacion:

        build: ./Servicio-autenticacion

        ports:

          - "8081:80"

      historial:

        build: ./Servicio-historial

        ports:

          - "8082:80"


---

## Cómo detener los servicios

Para detener y eliminar los contenedores:

`docker compose down`


---

## Verificar contenedores en ejecución

Para comprobar el estado:

`docker compose ps`


---

## Notas

- El servicio de autenticación expone el puerto **8081**
- El servicio de historial expone el puerto **8082**
- Los archivos HTML se sirven directamente desde **Nginx** dentro de cada contenedor
