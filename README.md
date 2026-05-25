
# PROTOTIPO TÉCNICO - AVANCE CON MICROSERVICIOS


## Información del Proyecto

### Descripción
En esta parte final del proyecto el sistema cuenta con cada uno de sus servicios implementados que son **autenticacion, gestion de citas medicas, historial clinico, notificaciones** y una **API Gateway** encargado de centralizar solicitudes. La comunicación entre los servicios se realiza mediante APIs REST utilizando HTTP y JSON, mientras que las variables de entorno permiten gestionar configuraciones sensibles y mejorar la portabilidad y seguridad de la aplicación.

Además, se implementó **RabbitMQ** como sistema de mensajería para permitir la **comunicación asíncrona** entre microservicios, especialmente en el servicio de **notificaciones**, el cual procesa eventos relacionados con las **citas médicas** y almacena las notificaciones en la **base de datos**. El sistema también incorpora el patrón **Circuit Breaker** en el API Gateway para aumentar la tolerancia a fallos y mejorar la disponibilidad de los servicios, junto con endpoints de **monitoreo y health checks** que permiten supervisar el estado y tiempo de respuesta de cada microservicio en tiempo real.
### Arquitectura
<img width="1600" height="1262" alt="arquitectura" src="https://github.com/user-attachments/assets/6a4b9727-5235-446d-9c2b-4a44902b3114" />

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
    
- **Servicio de historial**
  - Guardad cada una de las citas agendadas
  - Puerto: `5003`

- **Servicio de notificaciones**
  - notificar al usuario, guardar las notificaciones
  - Puerto: `5004`
  - 
- **RabbitMQ**
  - Servicio de mensajería entre microservicios
  - Puerto: `5672`
  - Panel web: `15672`
 
  

- **Base de datos Autenticación**
  - MySQL
  - Puerto: `3307`

- **Base de datos Citas**
  - MySQL
  - Puerto: `3308`
- **Base de datos historial**
  - MySQL
  - Puerto: `3309`
    
- **Base de datos notificaciones**
  - MySQL
  - Puerto: `3310`


## Estructura del proyecto

    Plataforma-de-gestion-de-citas
    │
    ├── Proyecto_Final
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
    |   |
    |   |── Servicio-historial
    │   │   ├── db
    │   │   │   └── historial_db.sql
    │   │   ├── app.py
    │   │   ├── Dockerfile
    │   │   └── requirements.txt
    |   |
    |   |── Servicio-notificaciones
    │   │   ├── db
    │   │   │   └── notificaciones_db.sql
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
    │   └── .env.example
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
- **Historial:** `http://localhost:5003`
- **Notificaciones:** `http://localhost:5004`

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
      - historial
      - notificaciones

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

  historial:
    build: ./Servicio-historial
    ports:
      - "5003:5000"
    depends_on:
      - db_historial
      - rabbitmq
    env_file:
      - .env

  db_historial:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${HISTORIAL_MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${HISTORIAL_MYSQL_DATABASE}
    ports:
      - "3309:3306"
    volumes:
      - db_historial_data:/var/lib/mysql

  notificaciones:
    build: ./Servicio-notificaciones
    ports:
      - "5004:5000"
    depends_on:
      - db_notificaciones
      - rabbitmq
    env_file:
      - .env

  db_notificaciones:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${NOTIFICACIONES_MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${NOTIFICACIONES_MYSQL_DATABASE}
    ports:
      - "3310:3306"
    volumes:
      - db_notificaciones_data:/var/lib/mysql

  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"

volumes:
  db_auth_data:
  db_citas_data:
  db_historial_data:
  db_notificaciones_data:
```
## Descripción básica de endpoints

### API Gateway
### GET
- GET /usuarios/listar → Lista usuarios
- GET /citas/paciente?id_paciente=1 → Consultar citas de un paciente  
- GET /citas/disponibilidad?id_doctor=1 → Consultar disponibilidad
- GET /estado/autenticacion → Estado del servicio de autenticación
- GET /estado/citas → Estado del servicio de citas
- GET /estado/historial → Estado del servicio de historial
- GET /estado/notificaciones → Estado del servicio de notificaciones
- GET /monitoreo → Monitoreo general de servicios y Circuit Breaker
- GET /historial/id_usuario → Consultar historial de un usuario
- GET /notificaciones/id_usuario → Consultar notificaciones de un usuario

### POST
- POST /usuarios/registro → Registrar usuario  
- POST /usuarios/login → Iniciar sesión  
- POST /citas/agendar → Crear cita
- POST /historial → Agregar nota manual al historial

### PUT
- PUT /citas/cancelar/id_citas → Cancelar una cita
- PUT /citas/reprogramar/id_citas → Reprogramar una cita
- PUT /notificaciones/marcar-leidas/id_usuario → Marcar notificaciones como leída



### Servicio de Autenticación

- GET / → Estado del servicio  
- GET /test-db → Verifica conexión a la base de datos  
- POST /login → Autenticación de usuario  
- POST /registro → Registro de usuario  
- GET /listar → Lista usuarios
- GET /usuarios/id_usuario→ Consulta un usuario por ID
- GET /health → Health check del servicio

---

### Servicio de Citas

- GET / → Estado del servicio  
- GET /test-db → Verifica conexión a la base de datos  
- POST /agendar → Crear cita  
- GET /citas_paciente?id_paciente=1 → Consultar citas de un paciente  
- GET /disponibilidad?id_doctor=1 → Consultar disponibilidad  
- GET /health → Health check del servicio
- PUT /cancelar/id_citas → Cancelar una cita
- PUT /reprogramar/id_citas → Reprogramar una cita
### Servicio de Historial
- GET /health → Estado del servicio
- GET /historial/id_usuario → Consultar historial de un usuario
- POST /historial → Agregar nota manual al historial de una cita

### Servicio de Notificaciones
- GET /health → Estado del servicio
- GET /notificaciones/id_usuario → Consultar notificaciones de un usuario
- PUT /notificaciones/marcar-leidas/id_usuario → Marcar notificaciones como leidas
---

## Cómo detener los servicios

Para detener y eliminar los contenedores:

`docker compose down`


---

## Verificar contenedores en ejecución

Para comprobar el estado:

`docker compose ps`


---

## Tecnologias utilizadas

| Tecnología | Concepto básico | Funcionalidad en el proyecto |
|---|---|---|
| Python | Lenguaje de programación de alto nivel orientado a objetos y fácil de interpretar. | Desarrollo de la lógica de los microservicios y manejo de endpoints. |
| Flask | Framework ligero de Python para desarrollo web y APIs REST. | Creación de los servicios y endpoints REST del sistema. |
| MySQL | Sistema de gestión de bases de datos relacional. | Almacenamiento de usuarios, citas, historial y notificaciones. |
| RabbitMQ | Broker de mensajería para comunicación asíncrona entre servicios. | Envío de eventos entre microservicios como historial y notificaciones. |
| Docker | Plataforma de contenedores para empaquetar aplicaciones y dependencias. | Ejecución aislada de cada microservicio y base de datos. |
| Docker Compose | Herramienta para definir y administrar múltiples contenedores Docker. | Orquestación de todos los servicios del sistema mediante `docker-compose.yml`. |
| Docker Desktop | Aplicación gráfica para administrar Docker en Windows/Mac. | Gestión visual de contenedores, imágenes y volúmenes del proyecto. |
| Postman | Plataforma para pruebas y documentación de APIs. | Pruebas de endpoints REST y validación de respuestas HTTP. |
| Lucidchart | Herramienta web para diagramas y modelado visual. | Diseño de diagramas de arquitectura y flujo de microservicios. |
| GitHub | Plataforma de alojamiento y control de versiones basada en Git. | Almacenamiento remoto y colaboración del proyecto. |
| GitHub Desktop | Cliente gráfico para Git y GitHub. | Gestión visual de commits, ramas y sincronización con GitHub. |
| Git Bash | Terminal que permite usar comandos Linux y Git en Windows. | Ejecución de comandos Git y administración del proyecto desde consola. |

## Descripción de los servicios del proyecto
### API Gateway
Servicio encargado de centralizar todas las solicitudes del sistema. Actúa como punto de entrada para los clientes, redirigiendo las peticiones hacia los microservicios correspondientes. Además, implementa monitoreo, health checks y el patrón Circuit Breaker para mejorar la tolerancia a fallos y disponibilidad del sistema.

---

### Servicio de Autenticación
Microservicio encargado de la gestión de usuarios y autenticación. Permite registrar usuarios, iniciar sesión, listar usuarios y consultar información individual de cada usuario. También valida la existencia y rol de los doctores utilizados en el servicio de citas.

---

### Servicio de Citas
Servicio encargado de la administración de citas médicas. Permite agendar, consultar, cancelar y reprogramar citas. Además, valida disponibilidad médica y publica eventos en RabbitMQ para notificar cambios a los servicios de historial y notificaciones.

---

### Servicio de Historial
Microservicio encargado de almacenar el historial de eventos relacionados con las citas médicas. Consume eventos enviados desde RabbitMQ y registra acciones como creación, cancelación o reprogramación de citas. También permite agregar notas manuales al historial clínico.

---

### Servicio de Notificaciones
Servicio encargado de gestionar las notificaciones de los usuarios. Consume eventos desde RabbitMQ y genera mensajes automáticos relacionados con cambios en las citas médicas. Permite consultar y marcar notificaciones como leídas.

---

### RabbitMQ
Broker de mensajería utilizado para la comunicación asíncrona entre microservicios. Permite desacoplar los servicios mediante colas de mensajes, facilitando el envío de eventos desde el servicio de citas hacia historial y notificaciones.
