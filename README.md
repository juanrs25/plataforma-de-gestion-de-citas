# Plataforma de Gestión de Citas Médicas

## Prototipo técnico basado en microservicios

Este proyecto corresponde al desarrollo de una **plataforma de gestión de citas médicas** implementada bajo una arquitectura de **microservicios**, utilizando **Docker**, **Docker Compose**, comunicación **HTTP/REST** y comunicación asíncrona mediante **RabbitMQ**.

La plataforma permite gestionar diferentes procesos relacionados con la atención médica, incluyendo el registro y autenticación de usuarios, gestión y consulta de citas, control de disponibilidad de médicos, cancelación y reprogramación de citas, almacenamiento del historial de eventos y generación de notificaciones para los usuarios.

La solución se encuentra organizada en servicios independientes, cada uno con responsabilidades específicas y su propia configuración. Los servicios que requieren persistencia cuentan con una base de datos MySQL independiente, permitiendo mantener una separación clara entre los diferentes componentes del sistema.

La comunicación entre los servicios se realiza mediante dos mecanismos principales:

- **Comunicación síncrona mediante HTTP/REST**: Utilizada principalmente para las solicitudes entre el API Gateway y los microservicios, así como para determinadas validaciones internas.
- **Comunicación asíncrona mediante RabbitMQ**: Utilizada para distribuir eventos relacionados con las citas hacia los servicios de historial y notificaciones.

Adicionalmente, el API Gateway incorpora un mecanismo de **Circuit Breaker**, encargado de controlar las fallas de comunicación con los microservicios y evitar solicitudes repetitivas hacia servicios que se encuentren temporalmente fuera de funcionamiento.

El proyecto también incorpora mecanismos de **Health Check y monitoreo**, permitiendo consultar el estado de los servicios y observar información relacionada con tiempos de respuesta, cantidad de fallos y estado de los circuitos.

### Tecnologías principales

- Python
- Flask
- MySQL
- Docker
- Docker Compose
- RabbitMQ
- HTTP/REST
- JSON

## Arquitectura del sistema

La plataforma está implementada mediante una arquitectura de **microservicios**, en la que cada componente se encarga de una responsabilidad específica y se ejecuta de manera independiente dentro de un contenedor Docker.

El sistema está compuesto por un **API Gateway**, cuatro microservicios funcionales, cuatro bases de datos MySQL independientes y un servidor de mensajería **RabbitMQ**.

### Componentes principales

| Componente | Responsabilidad | Puerto |
| :--- | :--- | :---: |
| API Gateway | Punto de entrada para las solicitudes de los clientes y gestión del Circuit Breaker | `5000` |
| Servicio de Autenticación | Registro, autenticación y consulta de usuarios | `5001` |
| Servicio de Citas | Gestión, consulta, cancelación y reprogramación de citas | `5002` |
| Servicio de Historial | Registro y consulta de eventos relacionados con las citas | `5003` |
| Servicio de Notificaciones | Gestión de notificaciones generadas a partir de eventos | `5004` |
| MySQL Autenticación | Persistencia de usuarios | `3307` |
| MySQL Citas | Persistencia de citas | `3308` |
| MySQL Historial | Persistencia del historial | `3309` |
| MySQL Notificaciones | Persistencia de notificaciones | `3310` |
| RabbitMQ | Comunicación asíncrona mediante eventos | `5672` |
| RabbitMQ Management | Interfaz de administración de RabbitMQ | `15672` |

### Diagrama de arquitectura

```text
                         CLIENTE
                            |
                            | HTTP/REST
                            v
                   +-------------------+
                   |    API GATEWAY    |
                   |    Puerto 5000    |
                   |                   |
                   |  Circuit Breaker  |
                   |     Monitoreo     |
                   +---------+---------+
                             |
          +------------------+------------------+
          |                  |                  |
          | HTTP             | HTTP             | HTTP
          v                  v                  v
+----------------+   +-------------+    +-------------+
| Autenticación  |   |    Citas    |    |  Historial  |
|     :5001      |   |    :5002    |    |    :5003    |
+-------+--------+   +------+------+    +------+------+
        |                   |                  |
        v                   v                  v
   +---------+         +---------+        +---------+
   |  MySQL  |         |  MySQL  |        |  MySQL  |
   |  Auth   |         |  Citas  |        |Historial|
   +---------+         +---------+        +---------+
                            |
                            | Eventos
                            v
                      +-------------+
                      |  RabbitMQ   |
                      |    :5672    |
                      +------+------+
                             |
                             |
                +------------+------------+
                |                         |
                v                         v
         +-------------+         +----------------+
         |  Historial  |         | Notificaciones |
         |             |         |     :5004      |
         +-------------+         +-------+--------+
                                         |
                                         v
                                  +--------------+
                                  |    MySQL     |
                                  |Notificaciones|
                                  +--------------+
```
## Comunicación entre componentes

El sistema utiliza dos mecanismos principales de comunicación.

### Comunicación síncrona mediante HTTP

El API Gateway recibe las solicitudes provenientes del cliente y las redirige hacia el microservicio correspondiente.

Por ejemplo:

```text
Cliente
   |
   | POST /citas/agendar
   v
API Gateway
   |
   | POST /agendar
   v
Servicio de Citas
```

El Servicio de Citas también realiza comunicación HTTP interna con el Servicio de Autenticación cuando necesita validar información de un usuario, como ocurre durante la consulta de disponibilidad de un médico.
```text
Servicio de Citas
       |
       | GET /usuarios/<id_usuario>
       v
Servicio de Autenticación
```

### Comunicación asíncrona mediante RabbitMQ

Las operaciones realizadas sobre las citas pueden generar eventos que deben ser procesados por otros servicios.

El Servicio de Citas publica los eventos en RabbitMQ. Actualmente utiliza dos colas:

- `eventos_citas`
- `eventos_notificaciones`

El Servicio de Historial consume los eventos de la cola `eventos_citas`, mientras que el Servicio de Notificaciones consume los eventos de `eventos_notificaciones`.

```text
                  Servicio de Citas
                         |
                         | Publica evento
                         v
                   +----------+
                   | RabbitMQ |
                   +----+-----+
                        |
         +--------------+--------------+
         |                             |
         v                             v
   eventos_citas             eventos_notificaciones
         |                             |
         v                             v
     Servicio                      Servicio
     Historial                  Notificaciones
         |                             |
         v                             v
  MySQL Historial             MySQL Notificaciones
```

Este mecanismo permite desacoplar la generación de eventos de su procesamiento, evitando que el Servicio de Citas tenga que realizar directamente las operaciones de historial y notificaciones.

## Persistencia de datos

Cada servicio que requiere almacenamiento utiliza una base de datos MySQL independiente:

- **Servicio de Autenticación** -> MySQL Autenticación
- **Servicio de Citas** -> MySQL Citas
- **Servicio de Historial** -> MySQL Historial
- **Servicio de Notificaciones** -> MySQL Notificaciones

Esta separación permite mantener los datos asociados a cada dominio de manera independiente.

## Contenedores Docker

Los componentes de la plataforma se ejecutan mediante **Docker Compose**. Cada microservicio se construye a partir de su propio `Dockerfile`, mientras que las bases de datos y RabbitMQ utilizan imágenes base proporcionadas por Docker.

La comunicación interna entre los contenedores se realiza utilizando los nombres de los servicios definidos en el archivo `docker-compose.yml`, por ejemplo:

- `http://autenticacion:5000`
- `http://citas:5000`
- `http://historial:5000`
- `http://notificaciones:5000`

Los puertos publicados permiten acceder desde el equipo local a los servicios que exponen una interfaz HTTP:

- **Gateway:** `http://localhost:5000`
- **Autenticación:** `http://localhost:5001`
- **Citas:** `http://localhost:5002`
- **Historial:** `http://localhost:5003`
- **Notificaciones:** `http://localhost:5004`

## Estructura del proyecto

El proyecto se encuentra organizado en diferentes directorios, donde cada microservicio mantiene sus propios archivos de aplicación, configuración y dependencias.

La estructura principal del proyecto es la siguiente:

```text
plataforma-de-gestion-de-citas/
│
├── .env.example
├── .gitignore
├── README.md
├── docker-compose.yml
│
├── Servicio-autenticacion/
│   ├── app.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── db/
│       └── db_autenticacion.sql
│
├── Servicio-citas/
│   ├── app.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── db/
│       └── citas_db.sql
│
├── Servicio-gateway/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── Servicio-historial/
│   ├── app.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── db/
│       └── historial_db.sql
│
├── Servicio-Notificaciones/
│   ├── app.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── db/
│       └── norificacionesdb.sql
│
└── evidencias/
    ├── 1_Docker_PS.png
    ├── 1_contenedores_ejecutandose.png
    ├── 2_consumo_HTTP_autenticacion.png
    ├── 2_consumo_HTTP_citas.png
    ├── 2_consumo_HTTP_gateway.png
    ├── 2_consumo_entre_servicios.png
    ├── 2_consumo_respuesta.png
    ├── 3_citasDB.png
    ├── 3_historialDB.png
    ├── 3_notificacionesDB.png
    ├── 3_usuariosDB.png
    ├── 4_circuito_abierto.png
    ├── 4_circuito_cerrado_nuevamente.png
    ├── 4_servicio_caido.png
    ├── 4_servicio_funcionando.png
    ├── 5_monitoreo_healthcheck.png
    └── 5_monitoreo_logs.png
```

### Descripción de los directorios y archivos

#### `Servicio-gateway/`

Contiene el API Gateway de la plataforma. Este servicio funciona como punto de entrada para las solicitudes HTTP realizadas por los clientes y se encarga de comunicarse con los demás microservicios.

Además, implementa la lógica del **Circuit Breaker**, los endpoints de estado de los servicios y el endpoint de monitoreo.

Sus archivos principales son:

- `app.py`: Implementación del API Gateway.
- `Dockerfile`: Configuración para construir la imagen Docker del servicio.
- `requirements.txt`: Dependencias de Python utilizadas por el servicio.

El Gateway no posee una carpeta `db/`, ya que no administra una base de datos propia.

#### `Servicio-autenticacion/`

Gestiona las operaciones relacionadas con los usuarios de la plataforma.

Entre sus responsabilidades se encuentran:

- Registro de usuarios.
- Inicio de sesión.
- Consulta de usuarios.
- Listado de usuarios.
- Verificación del estado del servicio.
- Acceso a la base de datos de autenticación.

La carpeta `db/` contiene el script SQL utilizado para la estructura y datos iniciales de la base de datos:

```text
db/
└── db_autenticacion.sql
```
#### `Servicio-citas/`

Gestiona las operaciones relacionadas con las citas médicas.

Entre sus responsabilidades se encuentran:

- Creación de citas.
- Consulta de citas de un paciente.
- Consulta de disponibilidad de médicos.
- Cancelación de citas.
- Reprogramación de citas.
- Validación de médicos mediante el Servicio de Autenticación.
- Publicación de eventos en RabbitMQ.
- Verificación del estado del servicio.

La carpeta `db/` contiene:

```text
db/
└── citas_db.sql
```

#### `Servicio-historial/`

Se encarga de almacenar y consultar los eventos relacionados con las citas.

El servicio recibe eventos mediante RabbitMQ y los almacena en su propia base de datos. También permite consultar el historial de un usuario y agregar registros manualmente.

La carpeta `db/` contiene:

```text
db/
└── historial_db.sql
```


#### `Servicio-Notificaciones/`

Se encarga de procesar los eventos recibidos mediante RabbitMQ y generar notificaciones asociadas a los usuarios.

Entre sus responsabilidades se encuentran:

- Recepción de eventos desde RabbitMQ.
- Almacenamiento de notificaciones.
- Consulta de notificaciones por usuario.
- Marcado de notificaciones como leídas.
- Verificación del estado del servicio.

La carpeta `db/` contiene el script SQL de la base de datos de notificaciones:

```text
db/
└── norificacionesdb.sql
```


#### `docker-compose.yml`

Define los servicios que componen la plataforma y permite construir, configurar y ejecutar los diferentes contenedores mediante Docker Compose.

En este archivo se definen:

- API Gateway.
- Servicio de Autenticación.
- Base de datos de Autenticación.
- Servicio de Citas.
- Base de datos de Citas.
- Servicio de Historial.
- Base de datos de Historial.
- Servicio de Notificaciones.
- Base de datos de Notificaciones.
- RabbitMQ.

También se configuran los puertos, dependencias entre servicios, variables de entorno y volúmenes utilizados para la persistencia de las bases de datos.

#### `.env.example`

Contiene un ejemplo de las variables de entorno necesarias para configurar el proyecto.

El archivo sirve como referencia para crear el archivo `.env` utilizado durante la ejecución de Docker Compose.

El archivo `.env` no debe incluirse en el repositorio cuando contenga credenciales o información sensible.

#### `evidencias/`

Contiene las capturas utilizadas para documentar las diferentes pruebas realizadas sobre la plataforma.

Las evidencias incluyen:

- Ejecución de contenedores Docker.
- Consumo de endpoints HTTP.
- Comunicación entre servicios.
- Estado de las bases de datos.
- Funcionamiento del Circuit Breaker.
- Recuperación del Circuit Breaker.
- Estado de los servicios.
- Health Checks.
- Monitoreo y logs.




## Microservicios

La plataforma está dividida en cinco servicios principales. Cada uno tiene una responsabilidad específica dentro del sistema y se ejecuta de manera independiente.

### 1. API Gateway

El **API Gateway** constituye el punto de entrada principal de la plataforma.

Su función es recibir las solicitudes de los clientes y dirigirlas hacia el microservicio correspondiente. De esta manera, el cliente no necesita comunicarse directamente con cada uno de los servicios internos.

Entre sus principales responsabilidades se encuentran:

- Gestionar las solicitudes relacionadas con usuarios.
- Gestionar las solicitudes relacionadas con citas.
- Gestionar las consultas de historial.
- Gestionar las consultas y actualizaciones de notificaciones.
- Comunicarse mediante HTTP con los microservicios internos.
- Implementar el mecanismo de **Circuit Breaker**.
- Consultar el estado de salud de los servicios.
- Proporcionar información de monitoreo.
- Registrar información relacionada con las solicitudes y fallos de comunicación.

El servicio se ejecuta en el puerto `5000`.

### 2. Servicio de Autenticación

El **Servicio de Autenticación** administra la información relacionada con los usuarios de la plataforma.

Entre sus principales funcionalidades se encuentran:

- Registro de nuevos usuarios.
- Inicio de sesión.
- Listado de usuarios.
- Consulta de un usuario mediante su identificador.
- Verificación de conexión con la base de datos.
- Health Check del servicio.

Este servicio utiliza una base de datos MySQL independiente para almacenar la información de los usuarios.

El servicio se ejecuta internamente en el puerto `5000` y se publica en el equipo local mediante:

- `http://localhost:5001`

El servicio también puede ser consultado internamente por otros contenedores mediante:

- `http://autenticacion:5000`

Una de sus funciones internas es permitir que el Servicio de Citas valide la existencia y el rol de un usuario cuando necesita comprobar si determinado usuario corresponde a un médico.

### 3. Servicio de Citas

El **Servicio de Citas** administra las operaciones relacionadas con la programación y gestión de citas médicas.

Entre sus principales funcionalidades se encuentran:

- Crear citas.
- Consultar las citas de un paciente.
- Consultar la disponibilidad de un médico.
- Cancelar citas.
- Reprogramar citas.
- Validar médicos mediante el Servicio de Autenticación.
- Validar conflictos de horarios.
- Publicar eventos en RabbitMQ.
- Verificar el estado del servicio.

El servicio utiliza una base de datos MySQL independiente para almacenar las citas.

El servicio se ejecuta internamente en `http://citas:5000` y se publica en el equipo local mediante:

- `http://localhost:5002`

Cuando se crea, cancela o reprograma una cita, el servicio genera un evento que es publicado en RabbitMQ.

Los eventos contienen información como la siguiente:

```json
{
    "id_usuario": 1,
    "id_cita": 10,
    "accion": "CITA AGENDADA",
    "detalles": "Cita programada para el 2026-08-14 a las 10:00:00"
}
```

4. Servicio de Historial

El Servicio de Historial se encarga de registrar los eventos relacionados con las citas y permitir su posterior consulta.

El servicio recibe eventos de manera asíncrona mediante RabbitMQ a través de la cola:

eventos_citas

Cuando recibe un evento, almacena la información correspondiente en su base de datos.

Entre sus principales funcionalidades se encuentran:

Recibir eventos provenientes de RabbitMQ.
Registrar eventos relacionados con las citas.
Consultar el historial de un usuario.
Agregar registros manuales al historial.
Verificar el estado del servicio.

El servicio utiliza una base de datos MySQL independiente.

Internamente se encuentra disponible mediante:

http://historial:5000

y se publica en el equipo local mediante:

http://localhost:5003

La comunicación con RabbitMQ se ejecuta en segundo plano mediante un hilo independiente, permitiendo que el servicio mantenga simultáneamente su servidor HTTP y el consumidor de eventos.

### 5. Servicio de Notificaciones

El **Servicio de Notificaciones** administra las notificaciones generadas a partir de los eventos producidos por el Servicio de Citas.

Este servicio consume eventos de RabbitMQ mediante la cola:

- `eventos_notificaciones`

Cuando recibe un evento, genera un mensaje para el usuario y lo almacena en su propia base de datos.

Entre sus principales funcionalidades se encuentran:

- Consumir eventos desde RabbitMQ.
- Generar notificaciones para los usuarios.
- Consultar las notificaciones de un usuario.
- Marcar las notificaciones como leídas.
- Verificar el estado del servicio.

El servicio utiliza una base de datos MySQL independiente.

Internamente se encuentra disponible mediante:

- `http://notificaciones:5000`

Y se publica en el equipo local mediante:

- `http://localhost:5004`

Al igual que el Servicio de Historial, el consumidor de RabbitMQ se ejecuta en un hilo independiente del servidor Flask.

## Comunicación entre los microservicios

Los microservicios utilizan diferentes mecanismos dependiendo del tipo de operación.

### Comunicación HTTP

La comunicación HTTP se utiliza para operaciones que requieren una respuesta inmediata.

El API Gateway se comunica con los servicios internos mediante sus nombres dentro de la red de Docker:

```text
Gateway
   |
   +----> autenticacion:5000
   |
   +----> citas:5000
   |
   +----> historial:5000
   |
   +----> notificaciones:5000
```

Adicionalmente, el Servicio de Citas se comunica directamente con el Servicio de Autenticación para validar la información de un usuario.

```
Servicio de Citas
       |
       | HTTP
       v
Servicio de Autenticación
Comunicación mediante eventos
```
Las operaciones relacionadas con las citas generan eventos que son publicados por el Servicio de Citas en RabbitMQ.
```

Servicio de Citas
       |
       | Publicación de evento
       v
    RabbitMQ
       |
       +----------------------+
       |                      |
       v                      v
eventos_citas        eventos_notificaciones
       |                      |
       v                      v
  Historial             Notificaciones
```
  De esta forma, los servicios de Historial y Notificaciones pueden procesar los eventos de manera independiente sin que el Servicio de Citas tenga que realizar directamente esas operaciones.

  


## Endpoints de la API

La plataforma expone diferentes endpoints HTTP para permitir la comunicación con los microservicios. El API Gateway centraliza las operaciones principales y posteriormente las dirige hacia el servicio correspondiente.

### API Gateway

El API Gateway se encuentra disponible mediante:

```text
http://localhost:5000
```
## Endpoints de la API

La plataforma expone diferentes endpoints HTTP para permitir la comunicación con los microservicios. El **API Gateway** centraliza las operaciones principales y las dirige hacia el servicio correspondiente.

El API Gateway se encuentra disponible en: `http://localhost:5000`

### Estado del Gateway

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| GET | `/` | Verifica que el API Gateway se encuentre funcionando. |

### Usuarios

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| GET | `/usuarios/listar` | Obtiene el listado de usuarios. |
| POST | `/usuarios/registro` | Registra un nuevo usuario. |
| POST | `/usuarios/login` | Realiza la autenticación de un usuario. |

### Citas

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| GET | `/citas/disponibilidad` | Consulta los horarios disponibles de un médico. |
| POST | `/citas/agendar` | Crea una nueva cita médica. |
| GET | `/citas/paciente` | Consulta las citas asociadas a un paciente. |
| PUT | `/citas/cancelar/<id_citas>` | Cancela una cita existente. |
| PUT | `/citas/reprogramar/<id_citas>` | Reprograma una cita existente. |

### Historial

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| GET | `/historial/<id_usuario>` | Consulta el historial de eventos de un usuario. |
| POST | `/historial` | Agrega manualmente un registro al historial. |

### Notificaciones

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| GET | `/notificaciones/<id_usuario>` | Consulta las notificaciones de un usuario. |
| PUT | `/notificaciones/marcar-leidas/<id_usuario>` | Marca como leídas las notificaciones de un usuario. |

### Estado y Monitoreo

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| GET | `/estado/autenticacion` | Consulta el estado del Servicio de Autenticación. |
| GET | `/estado/citas` | Consulta el estado del Servicio de Citas. |
| GET | `/estado/historial` | Consulta el estado del Servicio de Historial. |
| GET | `/estado/notificaciones` | Consulta el estado del Servicio de Notificaciones. |
| GET | `/monitoreo` | Obtiene información de estado, tiempos de respuesta, fallos y Circuit Breaker de los servicios. |

### Servicio de Autenticación

El Servicio de Autenticación se encuentra disponible externamente mediante:

- `http://localhost:5001`

Dentro de la red de Docker puede ser consultado mediante:

- `http://autenticacion:5000`

#### Endpoints

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| GET | `/` | Verifica que el servicio se encuentre funcionando. |
| GET | `/test-db` | Comprueba la conexión con la base de datos de autenticación. |
| POST | `/login` | Autentica un usuario mediante correo y contraseña. |
| POST | `/registro` | Registra un nuevo usuario. |
| GET | `/listar` | Obtiene el listado de usuarios. |
| GET | `/usuarios/<id_usuario>` | Consulta un usuario específico mediante su identificador. |
| GET | `/health` | Retorna el estado de salud del servicio. |

### Registro de usuario

El endpoint:

```text
POST /registro
```
recibe información del usuario en formato JSON.

Los campos utilizados son:
```
{
    "nombre_usuario": "Nombre del usuario",
    "password_usuario": "contraseña",
    "correo_usuario": "correo@example.com",
    "telefono_usuario": "3000000000",
    "direccion_usuario": "Dirección"
}
```
Los campos nombre_usuario, password_usuario y correo_usuario son obligatorios.

## Inicio de sesión

El endpoint:
```
POST /login
```
recibe:
```
{
    "correo_usuario": "correo@example.com",
    "password_usuario": "contraseña"
}
```
El servicio verifica las credenciales directamente contra la base de datos de usuarios.

## Servicio de Citas

El Servicio de Citas se encuentra disponible externamente mediante:
```
http://localhost:5002
```
### Servicio de Citas


#### Endpoints

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| GET | `/` | Verifica que el servicio se encuentre funcionando. |
| GET | `/test-db` | Comprueba la conexión con la base de datos de citas. |
| POST | `/agendar` | Crea una nueva cita. |
| GET | `/citas_paciente` | Consulta las citas de un paciente. |
| GET | `/disponibilidad` | Consulta los horarios disponibles de un médico. |
| PUT | `/cancelar/<id_citas>` | Cancela una cita. |
| PUT | `/reprogramar/<id_citas>` | Reprograma una cita. |
| GET | `/health` | Retorna el estado de salud del servicio. |
Crear una cita

El endpoint:
```
POST /agendar
```
recibe:
```
{
    "id_paciente_citas": 1,
    "id_doctor_citas": 2,
    "estado_citas": "Agendado",
    "fecha_programacion_citas": "2026-08-14",
    "hora_programacion_citas": "10:00:00"
}
```
Los identificadores del paciente y del doctor, así como la fecha y hora, son necesarios para crear la cita.

Antes de insertar la cita, el servicio comprueba que el médico no tenga otra cita activa en el mismo horario.

### Consultar citas de un paciente

```text
GET /citas_paciente?id_paciente=1
```
Permite obtener las citas asociadas al paciente indicado.

### Consultar disponibilidad
```
GET /disponibilidad?id_doctor=2&fecha=2026-08-14
```

El servicio valida primero que el usuario exista y que tenga el rol de Doctor mediante una solicitud HTTP al Servicio de Autenticación.

Posteriormente consulta las citas existentes y determina los horarios disponibles.

Si no se proporciona la fecha, el servicio utiliza la fecha actual.

### Cancelar una cita
```
PUT /cancelar/1
```
Actualiza el estado de la cita a:
```
Cancelado
```
Después de realizar la operación se publica un evento en RabbitMQ.

### Reprogramar una cita
```
PUT /reprogramar/1
```
recibe la nueva fecha y hora:
```
{
    "fecha_programacion_citas": "2026-08-15",
    "hora_programacion_citas": "14:00:00"
}
```
El servicio valida que la cita exista, que no esté cancelada y que el nuevo horario no esté ocupado.

Al completar la operación, el estado de la cita pasa a:
```
Reprogramado
```

También se publica un evento en RabbitMQ.

### Servicio de Historial

El **Servicio de Historial** se encuentra disponible externamente mediante:

- `http://localhost:5003`

Dentro de la red de Docker puede ser consultado mediante:

- `http://historial:5000`

#### Endpoints

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| GET | `/historial/<id_usuario>` | Consulta el historial de un usuario. |
| POST | `/historial` | Agrega manualmente un registro al historial. |
| GET | `/health` | Retorna el estado de salud del servicio. |

El servicio también mantiene un consumidor de RabbitMQ que escucha la cola:

- `eventos_citas`

Cuando recibe un evento, registra en la base de datos información como:

- Usuario.
- Cita.
- Acción realizada.
- Detalles.
- Fecha del evento.

### Consultar historial

```text
GET /historial/1
```
Retorna los registros asociados al usuario indicado.

Agregar registro manual
```
POST /historial
```
Ejemplo:
```
{
    "id_usuario": 1,
    "id_cita": 10,
    "accion": "NOTA_MANUAL",
    "detalles": "Observación registrada manualmente"
}
```
Los campos id_usuario, id_cita y detalles son obligatorios.

### Servicio de Notificaciones

El **Servicio de Notificaciones** se encuentra disponible externamente mediante:

- `http://localhost:5004`

Dentro de la red de Docker puede ser consultado mediante:

- `http://notificaciones:5000`

#### Endpoints

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| GET | `/notificaciones/<id_usuario>` | Consulta las notificaciones de un usuario. |
| PUT | `/notificaciones/marcar-leidas/<id_usuario>` | Marca como leídas las notificaciones del usuario. |
| GET | `/health` | Retorna el estado de salud del servicio. |

El servicio mantiene un consumidor de RabbitMQ que escucha la cola:

- `eventos_notificaciones`

Cuando recibe un evento generado por el Servicio de Citas, genera una notificación y la almacena en la base de datos.

### Consultar notificaciones

```text
GET /notificaciones/1
```
Permite consultar las notificaciones almacenadas para el usuario indicado.

Marcar notificaciones como leídas
```
PUT /notificaciones/marcar-leidas/1
```
Actualiza las notificaciones pendientes del usuario y las establece como leídas.

La respuesta incluye la cantidad de notificaciones que fueron actualizadas.

### Health Checks

Los servicios de Autenticación, Citas, Historial y Notificaciones cuentan con un endpoint /health.

Estos endpoints son utilizados por el API Gateway para verificar si los servicios se encuentran disponibles.

Las respuestas tienen una estructura similar a:
```
{
    "status": "ok",
    "servicio": "Citas"
}
```
El API Gateway utiliza estos mecanismos para proporcionar información sobre el estado de los servicios y para alimentar el sistema de monitoreo.




## 6. Endpoints de la API Gateway

La **API Gateway** funciona como punto de entrada principal para los clientes. Las solicitudes recibidas son redirigidas al microservicio correspondiente mediante comunicación HTTP.

### Autenticación

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/usuarios/listar` | Lista los usuarios registrados. |
| `POST` | `/usuarios/registro` | Registra un nuevo usuario. |
| `POST` | `/usuarios/login` | Permite iniciar sesión. |

### Gestión de citas

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/citas/disponibilidad` | Consulta los horarios disponibles de un doctor. |
| `POST` | `/citas/agendar` | Crea una nueva cita. |
| `GET` | `/citas/paciente` | Consulta las citas asociadas a un paciente. |
| `PUT` | `/citas/cancelar/<id_citas>` | Cancela una cita existente. |
| `PUT` | `/citas/reprogramar/<id_citas>` | Reprograma la fecha y hora de una cita. |

### Historial

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/historial/<id_usuario>` | Consulta el historial de eventos de un usuario. |
| `POST` | `/historial` | Agrega una nota manual al historial de una cita. |

### Notificaciones

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/notificaciones/<id_usuario>` | Consulta las notificaciones de un usuario. |
| `PUT` | `/notificaciones/marcar-leidas/<id_usuario>` | Marca como leídas las notificaciones de un usuario. |

### Estado de los servicios

La Gateway también proporciona endpoints para verificar individualmente el estado de los microservicios:

| Método | Endpoint | Servicio |
|---|---|---|
| `GET` | `/estado/autenticacion` | Autenticación |
| `GET` | `/estado/citas` | Citas |
| `GET` | `/estado/historial` | Historial |
| `GET` | `/estado/notificaciones` | Notificaciones |
| `GET` | `/monitoreo` | Monitoreo general de todos los servicios |

El endpoint `/monitoreo` permite consultar información como el estado HTTP, tiempo de respuesta, cantidad de fallos y estado actual del circuito de cada servicio.

## 7. Endpoints de los microservicios

Además de los endpoints expuestos por la API Gateway, cada microservicio cuenta con sus propios endpoints internos. Estos son utilizados directamente por la Gateway o por otros servicios cuando es necesario.

### Servicio de Autenticación

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/` | Verifica que el servicio de autenticación esté funcionando. |
| `GET` | `/health` | Health check del servicio. |
| `GET` | `/test-db` | Verifica la conexión con la base de datos de autenticación. |
| `POST` | `/login` | Autentica un usuario mediante correo y contraseña. |
| `POST` | `/registro` | Registra un nuevo usuario. |
| `GET` | `/listar` | Obtiene la lista de usuarios. |
| `GET` | `/usuarios/<id_usuario>` | Consulta un usuario específico mediante su ID. |

### Servicio de Citas

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/` | Verifica que el servicio de citas esté funcionando. |
| `GET` | `/health` | Health check del servicio. |
| `GET` | `/test-db` | Verifica la conexión con la base de datos de citas. |
| `POST` | `/agendar` | Crea una nueva cita y genera el evento correspondiente. |
| `GET` | `/citas_paciente` | Consulta las citas asociadas a un paciente. |
| `GET` | `/disponibilidad` | Consulta la disponibilidad de un doctor para una fecha determinada. |
| `PUT` | `/cancelar/<id_citas>` | Cancela una cita existente y genera un evento. |
| `PUT` | `/reprogramar/<id_citas>` | Modifica la fecha y hora de una cita y genera un evento. |

El servicio de citas también se comunica con el **Servicio de Autenticación** mediante HTTP para validar que el usuario seleccionado como doctor exista y tenga el rol correspondiente.

### Servicio de Historial

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/health` | Health check del servicio. |
| `GET` | `/historial/<id_usuario>` | Consulta el historial de eventos de un usuario. |
| `POST` | `/historial` | Permite agregar manualmente un registro al historial. |

El Servicio de Historial recibe eventos publicados mediante **RabbitMQ** en la cola `eventos_citas` y almacena estos eventos en su propia base de datos.

### Servicio de Notificaciones

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/health` | Health check del servicio. |
| `GET` | `/notificaciones/<id_usuario>` | Consulta las notificaciones de un usuario. |
| `PUT` | `/notificaciones/marcar-leidas/<id_usuario>` | Marca como leídas las notificaciones de un usuario. |

El Servicio de Notificaciones recibe eventos mediante **RabbitMQ** desde la cola `eventos_notificaciones` y genera los registros correspondientes en su propia base de datos.

> Los microservicios están diseñados para ejecutarse dentro de la red de Docker Compose. Por esta razón, las comunicaciones internas utilizan los nombres de los servicios definidos en `docker-compose.yml`, como `autenticacion`, `citas`, `historial`, `notificaciones` y `rabbitmq`.
