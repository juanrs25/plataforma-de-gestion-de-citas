# Laboratorio Implementacion Circuit Breaker

## FASE 1 – Analisis 
### Que hace el sistema actualmente?
El sistema funciona mediante una arquitectura distribuida compuesta por tres servicios: usuarios, mascotas y un API Gateway que centraliza las solicitudes.
El gateway recibe las peticiones de los clientes y se comunica con los microservicios correspondientes para obtener la información. Además, implementa el patrón Circuit Breaker en el endpoint de mascotas para manejar fallos de conexión.

>
Cuando un servicio falla varias veces consecutivas(En este caso 3 veces), el circuito se abre y el gateway deja de enviar solicitudes a ese servicio, respondiendo directamente con un error 503. Esto permite evitar sobrecarga, mejorar la estabilidad del sistema y mantener disponible el resto de funcionalidades.

- **Servicio interrumpido:**
<img width="835" height="202" alt="image" src="https://github.com/user-attachments/assets/783793ae-fdad-497f-a746-909dd8ac4209" />

- **Circuito abierto apartir de los tres fallos:**
<img width="853" height="300" alt="image" src="https://github.com/user-attachments/assets/d61cc471-e34d-4e2f-b95f-a8e496b90e94" />

### ¿Se protege o insiste?
Después de detectar varios errores consecutivos, el API Gateway deja de insistir en conectarse con el backend. Esto evita generar más carga sobre un servicio que ya está fallando y ayuda a prevenir una caída mayor del sistema.
>
En lugar de seguir intentando la conexión en cada petición, el gateway corta temporalmente la comunicación y responde inmediatamente con un error controlado.
Este comportamiento es precisamente el objetivo del patrón Circuit Breaker: detectar fallos repetitivos y proteger tanto al backend como a la estabilidad general del sistema.

## FASE 2 – Implementacion de patron Circuit Breaker 

En esta fase se extendió la implementación del patrón Circuit Breaker a los demás endpoints del API Gateway. Inicialmente, el comportamiento solo estaba implementado en el endpoint `/mascotas`, pero posteriormente se aplicó también a `/usuarios` y `/listar`.

El objetivo fue mejorar la tolerancia a fallos y evitar que el gateway continuara realizando solicitudes a servicios que no se encuentran disponibles.

### Implementación Circuit Breaker en `/usuarios`
---
Para el endpoint `/usuarios` se implementó un Circuit Breaker independiente del servicio de mascotas.  

El sistema ahora detecta fallos consecutivos al intentar conectarse con el microservicio de usuarios. Cuando el número de errores alcanza el límite definido, el circuito se abre automáticamente y el gateway deja de enviar solicitudes al servicio.

- **Servicio usuarios interrumpido:**
  <img width="800" height="199" alt="image" src="https://github.com/user-attachments/assets/df7fe743-e676-48a6-8b6d-941574ce0649" />
  
- **Circuito abierto apartir de los tres fallos:**
<img width="862" height="289" alt="image" src="https://github.com/user-attachments/assets/cf2ace83-d177-4934-9c73-8b64773c4897" />

- **Mensaje mostrado al usuario:**
<img width="578" height="169" alt="image" src="https://github.com/user-attachments/assets/81f0f67c-2874-4e64-9fad-077dd99b56dd" />

### Implementación Circuit Breaker  en `/listar`
---
El endpoint `/listar` fue modificado para soportar fallos individuales de los microservicios.

Actualmente, el gateway consulta la información de usuarios y mascotas por separado. Si alguno de los servicios no está disponible, el sistema continúa funcionando y devuelve únicamente el mensaje del servicio afectado.

Esto permite mantener disponibilidad parcial del sistema y evita que una falla detenga completamente el gateway.

- **Servicio usuarios interrumpido para esta prueba:**
<img width="800" height="199" alt="F2_interrumpido" src="https://github.com/user-attachments/assets/0f4e3644-1fe3-4211-a483-dff6718d9291" />

- **Respuesta al usuario solo el endpoint disponible:**
<img width="620" height="399" alt="image" src="https://github.com/user-attachments/assets/6c79131f-376b-477a-b2c2-08b36c8b8354" />

### Análisis 
---
- **¿Cada servicio debe tener su propio contador de fallos?**
>
Sí. Cada microservicio debe manejar un contador de fallos independiente porque los errores pueden ocurrir de manera diferente en cada servicio. Por ejemplo, el servicio de usuarios puede fallar mientras el servicio de mascotas continúa funcionando correctamente. Tener contadores separados permite detectar con precisión qué servicio presenta problemas y aplicar el patrón Circuit Breaker únicamente al servicio afectado.

- **¿El circuito debe abrirse de forma independiente por servicio?**
>
Sí. El circuito debe abrirse de manera independiente para evitar que la falla de un servicio afecte a todo el sistema. Si el servicio de usuarios presenta varios fallos consecutivos, solamente se abre el circuito de usuarios, mientras que el servicio de mascotas puede seguir atendiendo solicitudes normalmente. Esto mejora la disponibilidad y estabilidad del sistema distribuido.

- **¿Qué pasa si falla un servicio pero el otro sigue funcionando?**
>
Cuando uno de los servicios falla, el gateway continúa procesando las solicitudes del servicio que todavía está disponible. En el endpoint /listar, por ejemplo, el sistema puede seguir mostrando la información de mascotas aunque el servicio de usuarios no responda. De esta manera se mantiene una disponibilidad parcial del sistema y se evita que una única falla detenga completamente la aplicación.
>
## FASE 3 - Investigación Half-Open
- **¿Qué significa “half-open”?**
>
El estado half-open es una fase del patrón Circuit Breaker que ocurre después de que el circuito ha permanecido abierto durante un tiempo. En este estado, el sistema permite realizar una pequeña cantidad de solicitudes de prueba para verificar si el servicio ya volvió a funcionar correctamente.
- **¿Cuándo se vuelve a intentar una llamada?**
>
La llamada se vuelve a intentar después de que el circuito ha estado abierto durante un tiempo determinado. El objetivo es comprobar si el microservicio ya se recuperó y puede volver a atender solicitudes normalmente sin generar más fallos.
- **¿Qué pasa si el servicio vuelve a fallar?**
>
Si el servicio falla nuevamente durante el estado half-open, el circuito se abre otra vez automáticamente. Esto provoca que el gateway deje de enviar solicitudes al servicio afectado y continúe respondiendo con errores controlados hasta que el sistema vuelva a intentar otra verificación más adelante.
