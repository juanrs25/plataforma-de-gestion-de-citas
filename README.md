
# PROTOTIPO TÉCNICO - AVANCE CON MICROSERVICIOS


## Información del Proyecto

### Descripción
En este avance, el sistema evoluciona de un prototipo estático a una arquitectura de **microservicios**, utilizando **Docker** y **Docker Compose** para ejecutar cada servicio en contenedores independientes.

Los servicios se comunican mediante **HTTP** (REST) y manejan la información en formato JSON. Además, se utilizan **variables de entorno** para gestionar configuraciones como credenciales y conexiones, lo que mejora la seguridad y permite modificar el entorno sin cambiar el código.

### Servicios incluidos
- **API Gateway**
  - Punto de entrada principal
  - Puerto: `5000`

- **Servicio de Autenticación**
  - Registro, login y gestión de usuarios
  - Puerto: `5001`

- **Servicio de Citas**
  - Agendamiento, consulta de citas y disponibilidad
  - Puerto: `5002`

- **Base de datos Autenticación**
  - MySQL
  - Puerto: `3307`

- **Base de datos Citas**
  - MySQL
  - Puerto: `3308`

## Estructura del proyecto

    Avance Dos
    │
    ├── Citas medicas - avance dos
    │   │
    │   ├── Servicio-autenticacion
    │   │   ├── db
    │   │   │   └── db_autenticacion.sql
    │   │   ├── app.py
    │   │   ├── Dockerfile
    │   │   └── requirements.txt
    │   │
    │   ├── Servicio-citas
    │   │   ├── db
    │   │   │   └── Citas_db.sql
    │   │   ├── app.py
    │   │   ├── Dockerfile
    │   │   └── requirements.txt
    │   │
    │   ├── Servicio-gateway
    │   │   ├── app.py
    │   │   └── Dockerfile
    |   |   └── requirements.txt
    │   │
    │   ├── docker-compose.yml
    │   └── .env
---

## Requisitos

Antes de ejecutar el proyecto, asegúrate de tener instalado:

- **Docker**
- **Docker Compose**

---


## Cómo ejecutar el proyecto

### 1) Ir a la carpeta raíz
Ubícate en la carpeta donde está `docker-compose.yml`:

### 2) Crear archivo `.env`

Crear un archivo `.env` en la raíz del proyecto.

Este archivo no está incluido en el repositorio por seguridad, ya que contiene configuraciones sensibles como credenciales.

Ejemplo de variables que debes definir:

- Variables de base de datos para autenticación  
- Variables de base de datos para citas  
- Contraseñas de MySQL  
- Nombres de las bases de datos
  
### 3) Construir y levantar servicios
Ejecuta:

`docker compose up -d --build`


### ¿Qué hace este comando?
- **Construye** las imágenes de los servicios
- **Crea y levanta** los contenedores
- Deja los servicios corriendo en **segundo plano** (`-d`)

---

## Acceso a los servicios

Cuando todo esté arriba, abre en tu navegador:

- **API Gateway:** `http://localhost:5000`
- **Autenticacion:** `http://localhost:5001`
- **Citas:** `http://localhost:5002`

---

## Docker Compose (docker-compose.yml)
```yaml
services:

  gateway:
    build: ./Servicio-gateway
    ports:
      - "5000:5000"
    depends_on:
      - autenticacion
      - citas

  autenticacion:
    build: ./Servicio-autenticacion
    ports:
      - "5001:5000"
    depends_on:
      - db_autenticacion
    env_file:
      - .env

  db_autenticacion:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${AUTH_MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${AUTH_MYSQL_DATABASE}
    ports:
      - "3307:3306"
    volumes:
      - db_auth_data:/var/lib/mysql

  citas:
    build: ./Servicio-citas
    ports:
      - "5002:5000"
    depends_on:
      - db_citas
    env_file:
      - .env

  db_citas:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${CITA_MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${CITA_MYSQL_DATABASE}
    ports:
      - "3308:3306"
    volumes:
      - db_citas_data:/var/lib/mysql

volumes:
  db_auth_data:
  db_citas_data:
```
## Descripción básica de endpoints

###API Gateway

- GET /usuarios/listar → Lista usuarios  
- POST /usuarios/registro → Registrar usuario  
- POST /usuarios/login → Iniciar sesión  

- POST /citas/agendar → Crear cita  
- GET /citas/paciente?id_paciente=1 → Consultar citas de un paciente  
- GET /citas/disponibilidad?id_doctor=1 → Consultar disponibilidad 

### Servicio de Autenticación

- GET / → Estado del servicio  
- GET /test-db → Verifica conexión a la base de datos  
- POST /login → Autenticación de usuario  
- POST /registro → Registro de usuario  
- GET /listar → Lista usuarios  

---

### Servicio de Citas

- GET / → Estado del servicio  
- GET /test-db → Verifica conexión a la base de datos  
- POST /agendar → Crear cita  
- GET /citas_paciente?id_paciente=1 → Consultar citas de un paciente  
- GET /disponibilidad?id_doctor=1 → Consultar disponibilidad  

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
- Si algún servicio no responde, verificar que todos los contenedores estén activos con `docker compose ps`.
- En caso de errores, se recomienda revisar los logs con `docker compose logs`.
- Las variables de entorno deben configurarse correctamente antes de ejecutar el sistema.
-  No se recomienda subir el archivo `.env` al repositorio por seguridad.

