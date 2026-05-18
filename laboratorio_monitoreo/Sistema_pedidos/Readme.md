# Sistema de Pedidos Distribuido

## Descripción

Este proyecto implementa un sistema distribuido basado en microservicios utilizando Flask y Docker Compose.

El sistema está compuesto por los siguientes servicios:

- Gateway
- Inventario
- Pedidos
- Pagos

Cada microservicio funciona en un contenedor independiente y se comunica mediante HTTP usando la red interna de Docker.

---

# Tecnologías utilizadas

- Python
- Flask
- Docker
- Docker Compose

---

# Arquitectura del sistema

El gateway actúa como punto central de acceso y se comunica con los demás microservicios.
<img width="662" height="802" alt="Arquitectura" src="https://github.com/user-attachments/assets/05f60c00-e178-440c-b77a-e10c088aab93" />


---

# Ejecución del proyecto

## Levantar contenedores

```bash
docker compose up --build
```

## Ver contenedores activos

```bash
docker ps
```

---

# Endpoints principales

| Servicio | Endpoint |
|---|---|
| Gateway | `/` |
| Inventario | `/inventario` |
| Pedidos | `/pedidos` |
| Pagos | `/pagos` |
| Health Check | `/health` |

---

# FASE 1 — Logs

## Objetivo

Implementar logs descriptivos para monitorear las solicitudes realizadas entre los microservicios y facilitar la detección de errores.

---

# Logs implementados

Se agregaron logs en el gateway y en los microservicios para registrar:

- solicitudes recibidas
- respuestas exitosas
- tiempos de respuesta
- errores de conexión
- códigos HTTP



# Análisis

Los logs permitieron:

- monitorear el flujo de solicitudes
- identificar errores rápidamente
- conocer el tiempo de respuesta de cada servicio
- verificar la comunicación entre microservicios

Esto facilita la observabilidad y el monitoreo del sistema distribuido.

---

# Captura — Logs del sistema

<img width="1469" height="697" alt="image" src="https://github.com/user-attachments/assets/85413425-cea4-4eb8-9aed-0f1033b27067" />



---

# FASE 2 — Health Checks

## Objetivo

Implementar endpoints de health check para verificar la disponibilidad y el estado de cada microservicio.

---

# Endpoints implementados

Cada servicio cuenta con un endpoint:

```txt
/health
```

Ejemplo:

```python
@app.route("/health")
def health():
    return {
        "status": "ok",
        "servicio": "inventario"
    }
```

---

# Funcionamiento

El gateway consulta los endpoints `/health` de cada microservicio para verificar si el servicio está disponible.

Ejemplo:

```python
requests.get("http://inventario:5000/health")
```

---

Si el servicio responde correctamente:

```json
{
  "status": "ok",
  "servicio": "inventario"
}
```

Si el servicio está caído:

```json
{
  "status": "Caido",
  "service": "Inventario"
}
```


# Análisis

Los health checks permiten:

- verificar disponibilidad
- detectar servicios caídos
- monitorear el estado del sistema
- validar comunicación entre microservicios

Estos endpoints son fundamentales en sistemas distribuidos para supervisar el funcionamiento de los servicios.

---

# Captura — Health Checks funcionando
<img width="980" height="123" alt="image" src="https://github.com/user-attachments/assets/7e5b26d0-9293-4f93-b46e-b1a73df2fd41" />


---
# FASE 3 — Monitoreo

## Objetivo

Implementar monitoreo básico en el gateway para consultar el estado de los microservicios y medir sus tiempos de respuesta.

Los servicios monitoreados fueron:

- inventario
- pedidos
- pagos

---

# Endpoints implementados

## Health Checks

| Endpoint | Función |
|---|---|
| `/estado/inventario` | Verifica estado de inventario |
| `/estado/pedidos` | Verifica estado de pedidos |
| `/estado/pagos` | Verifica estado de pagos |

---

## Endpoints monitoreados con tiempos de respuesta

| Endpoint | Función |
|---|---|
| `/inventario` | Consulta productos del inventario |
| `/pedidos` | Consulta pedidos registrados |
| `/pagos` | Consulta pagos realizados |

---

# Monitoreo de tiempos de respuesta

El gateway también registró el tiempo que tardó cada servicio en responder.

# Captura — Monitoreo y tiempos de respuesta

<img width="972" height="311" alt="image" src="https://github.com/user-attachments/assets/aacefe9c-999d-4c9b-b476-ce2cfe430341" />


---

# Conclusión

El monitoreo permitió verificar disponibilidad, detectar servicios caídos y medir tiempos de respuesta de los microservicios.

Los logs y health checks facilitaron el análisis del estado general del sistema distribuido.


# FASE 4 — Simulación de fallos

## Objetivo

El objetivo de esta fase fue analizar el comportamiento del sistema distribuido cuando uno de los microservicios deja de estar disponible.

Para esta prueba se apagó el servicio `pagos` con el fin de evaluar:

- manejo de errores
- disponibilidad del sistema
- funcionamiento de los health checks
- comportamiento de los logs
- tolerancia a fallos

---

# Procedimiento realizado

Se apagó el microservicio `pagos` utilizando Docker:

```bash
docker compose stop pagos
```

Después de apagar el servicio, se realizaron solicitudes desde el gateway hacia los diferentes endpoints para verificar el comportamiento del sistema.

---

# Verificación del servicio caído

Se intentó acceder al endpoint:

```txt
/estado/pagos
```

El gateway detectó correctamente que el servicio no estaba disponible y respondió con un código HTTP `503 Service Unavailable`.

## Resultado esperado

```json
{
  "status": "Caido",
  "service": "Pagos"
}
```

---

# Captura — Servicio pagos caído

<img width="667" height="217" alt="image" src="https://github.com/user-attachments/assets/93102368-9c40-4119-aee7-c3d5f7a4e5c8" />


# Captura — Servicio logs servicio de pagos caido
<img width="1463" height="190" alt="image" src="https://github.com/user-attachments/assets/2360d49d-fea4-48db-a2b6-84d880606a68" />




---

## Análisis

Los logs muestran que:

- el gateway recibió correctamente la solicitud
- el sistema intentó comunicarse con el servicio pagos
- la conexión falló porque el contenedor estaba apagado
- el gateway registró el error correctamente
- el sistema devolvió un código HTTP 503 indicando indisponibilidad

Esto permitió identificar rápidamente el servicio afectado y el tipo de error ocurrido.

---

# Verificación de servicios disponibles

A pesar de que el servicio `pagos` fue apagado, los demás servicios continuaron funcionando correctamente.

## Endpoint inventario

```txt
/inventario
```
## Captura servicio inventario y pedidos funcionando correctamente
<img width="674" height="178" alt="image" src="https://github.com/user-attachments/assets/87d0791b-3a3a-4164-b3b6-46735ff7a8b1" />

<img width="649" height="165" alt="image" src="https://github.com/user-attachments/assets/0a62721a-a113-4140-b7fd-3c62aaa21b25" />



### Captura Logs obtenidos con pagos caido y los demas servicios disponibles
<img width="1466" height="414" alt="image" src="https://github.com/user-attachments/assets/0f4b7b88-b8aa-4572-930f-4554cde72df5" />



---

# Captura — Servicio inventario funcionando

<img width="676" height="529" alt="image" src="https://github.com/user-attachments/assets/75984275-d93c-4dbb-98fd-701f1a85997f" />



---

# Captura — Servicio pedidos funcionando

<img width="661" height="570" alt="image" src="https://github.com/user-attachments/assets/0890db80-68b0-4f74-a262-8af866db8871" />



---

# Análisis de disponibilidad

## Estado de los servicios

| Servicio | Estado |
|---|---|
| Gateway | Disponible |
| Inventario | Disponible |
| Pedidos | Disponible |
| Pagos | Caído |

## Interpretación

El sistema continuó funcionando parcialmente aun cuando uno de los microservicios dejó de estar disponible.

Esto demuestra:

- desacoplamiento entre servicios
- independencia funcional
- tolerancia parcial a fallos
- capacidad de detección de errores



---

# Manejo de errores

El gateway implementó manejo de excepciones para evitar que la caída de un servicio afectara completamente al sistema.

Cuando el servicio pagos no respondió, el gateway devolvió una respuesta controlada:

```json
{
  "error": "Servicio pagos caido"
}
```

y registró el error en los logs.

---

# FASE 5 — Métricas

## Objetivo

Implementar métricas básicas para analizar el comportamiento del sistema distribuido y medir el rendimiento de los microservicios.

Durante esta fase se monitorearon:

- tiempos de respuesta
- cantidad de errores
- disponibilidad de servicios
- respuestas HTTP

---

# Métricas implementadas

El gateway fue configurado para registrar información relacionada con el rendimiento y estado de los servicios.

Las métricas se obtuvieron mediante:

- logs
- medición de tiempo
- manejo de excepciones
- códigos HTTP

---

# Medición de tiempos de respuesta

Se utilizó el módulo `time` de Python para calcular cuánto tarda cada microservicio en responder.

## Ejemplo implementado

```python
inicio = time.time()

respuesta = requests.get(
    "http://inventario:5000/inventario"
)

fin = time.time()

tiempo_respuesta = fin - inicio
```

---
### Captura de los tiempos de respuesta

<img width="1356" height="399" alt="image" src="https://github.com/user-attachments/assets/49a96163-d5c0-410f-a2dd-5052afa732ee" />

---

# Análisis de tiempos de respuesta

Los tiempos registrados permitieron:

- verificar el rendimiento de los microservicios
- identificar posibles retrasos
- monitorear latencia de comunicación
- validar rapidez de respuesta del sistema

Durante las pruebas, los servicios respondieron en tiempos bajos, indicando una comunicación eficiente entre contenedores.


# Medición de cantidad de errores

El sistema también registró errores cuando un microservicio no estuvo disponible.

## Captura Microservicio no disponible 
<img width="1448" height="190" alt="image" src="https://github.com/user-attachments/assets/bab4d3d2-f59c-4006-b316-851858defa1d" />



# Análisis de errores

Los logs permitieron identificar:

- servicios caídos
- errores de conexión
- Numero de fallos de comunicación
- respuestas HTTP de error

Cuando el servicio `pagos` fue apagado, el gateway detectó correctamente la falla y devolvió un código HTTP `503 Service Unavailable`.

---

# Códigos HTTP registrados

| Código | Significado |
|---|---|
| 200 | Servicio funcionando correctamente |
| 503 | Servicio no disponible |


---

# Conteo de errores detectados

Durante las pruebas:

- los endpoints disponibles respondieron correctamente con código `200`
- el servicio apagado generó errores `503`
- el gateway registró y manejó las excepciones sin detener el sistema


# Monitoreo de disponibilidad

Las métricas también permitieron monitorear disponibilidad mediante los endpoints `/health`.

Esto ayudó a verificar:

- qué servicios estaban activos
- cuáles presentaban fallos
- comportamiento del sistema durante la simulación de errores

---

# Interpretación general

Las métricas implementadas permitieron analizar el comportamiento del sistema distribuido en tiempo real.

El monitoreo de tiempos de respuesta y errores ayudó a:

- detectar fallos rápidamente
- analizar rendimiento
- validar disponibilidad
- mejorar observabilidad del sistema

---

# Conclusión

La implementación de métricas permitió medir el rendimiento y estabilidad de los microservicios.

Los tiempos de respuesta mostraron una comunicación rápida entre servicios, mientras que los logs y códigos HTTP facilitaron la detección de errores y servicios caídos.

Esto demuestra la importancia del monitoreo y las métricas en sistemas distribuidos para garantizar disponibilidad y observabilidad.
