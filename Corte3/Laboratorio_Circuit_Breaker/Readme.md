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
>
## FASE 4 - Implementacion del estado Half-Open

En esta fase se implementado el estado Half-Open en los servicios del API Gateway.

El objetivo fue permitir que el sistema pudiera verificar automáticamente si un servicio que había fallado anteriormente ya se recuperó.
Cuando el circuito permanece abierto durante un tiempo determinado, el gateway realiza una solicitud de prueba al microservicio. Dependiendo del resultado:

- Si la solicitud funciona, el circuito vuelve a cerrarse.
- Si la solicitud falla nuevamente, el circuito se reabre automáticamente.
---
## Implementación HALF-OPEN en `/usuarios`

Se agregó un temporizador y un estado HALF-OPEN para el servicio de usuarios.

Actualmente, después de varios fallos consecutivos:
1. el circuito se abre.
2. el gateway deja de enviar solicitudes.
3. después de un tiempo de espera, el sistema realiza una petición de prueba.
4. si el servicio responde correctamente, el circuito vuelve al estado cerrado.

Esto permite recuperar automáticamente el funcionamiento normal sin necesidad de reiniciar manualmente el gateway.

---
- **implementación HALF-OPEN `/usuarios`:**
  <img width="967" height="786" alt="image" src="https://github.com/user-attachments/assets/6904c5c5-fac7-45c4-b425-e604ab1b9407" />

>
- **Fallos consecutivos y apertura del circuito `/usuarios`:**
  <img width="1420" height="410" alt="image" src="https://github.com/user-attachments/assets/c951fa48-a261-4dfd-9527-47e5de47a4d3" />

>
- **Evidencia de logs "Pasando a estado HALF-OPEN", además  se observa que debido a que el servicio sigue sin funcionar se vuelve a reabrir el circuito `/usuarios`:**
  <img width="1435" height="492" alt="image" src="https://github.com/user-attachments/assets/ee15eb23-7c0a-4a8a-9749-281a6d55cb55" />
>
---
## Implementación HALF-OPEN en `/mascotas`
El mismo comportamiento fue implementado para el servicio de mascotas.

Ahora el gateway puede:
- Detectar múltiples fallos consecutivos.
- Abrir automáticamente el circuito.
- Esperar un tiempo definido.
- Realizar una solicitud de prueba.
- Cerrar o reabrir el circuito dependiendo de la respuesta del servicio.

Esta implementación mejora la tolerancia a fallos y permite una recuperación automática del sistema distribuido.


- **Implementación HALF-OPEN `/mascotas`:**
 <img width="881" height="818" alt="image" src="https://github.com/user-attachments/assets/6cbfca2f-e7f9-4090-822a-35c3bdf0c52e" />
 
>
- **Fallos consecutivos y apertura del circuito  `/mascotas`:**
 <img width="1438" height="417" alt="image" src="https://github.com/user-attachments/assets/428e31a0-3575-4c9c-9870-a98824c3c46e" />
 
>
- **Evidencia de logs "Pasando a estado HALF-OPEN"`/mascotas`:**
 <img width="1417" height="521" alt="image" src="https://github.com/user-attachments/assets/473dff80-1f52-4598-b331-5fb82116d144" />

>
---
## Implementación HALF-OPEN en `/listar`
El endpoint `/listar` fue ajustado para trabajar junto con los Circuit Breakers de cada servicio.

Actualmente:
- Consulta usuarios y mascotas por separado.
- Detecta si alguno de los circuitos está abierto.
- Evita solicitudes innecesarias a servicios caídos.
- Mantiene disponibilidad parcial del sistema.

Esto permite que el gateway continúe respondiendo aunque uno de los microservicios falle.

- **Respuesta cuando ambos servicios funcionan `/listar`:**
  <img width="592" height="664" alt="image" src="https://github.com/user-attachments/assets/da44b8da-a012-432b-98a3-1c4aa1c7ebac" />
>

- **Respuesta cuando falla usuarios `/listar`:**
<img width="669" height="398" alt="image" src="https://github.com/user-attachments/assets/31acd371-d1f5-4f00-9963-a3f95b98d51d" />

>
- **Respuesta cuando falla mascotas `/listar`:**
<img width="676" height="460" alt="image" src="https://github.com/user-attachments/assets/5c791f04-f761-4d54-b3ce-657905d95a61" />
>

### FASE 5 - Validar

Las pruebas de validación fueron realizadas principalmente sobre el endpoint `/usuarios`, ya que este implementa el mismo comportamiento de Circuit Breaker y HALF-OPEN utilizado en el servicio de mascotas.

El objetivo fue comprobar el funcionamiento del sistema en diferentes escenarios de fallo y recuperación del microservicio.

---
### 1. Servicio funcionando correctamente

En este escenario los microservicios de usuarios y mascotas se encuentran activos y responden correctamente a las solicitudes realizadas desde el gateway.

El sistema devuelve la información normalmente y el circuito permanece en estado cerrado (*CLOSED*).
>
<img width="600" height="651" alt="image" src="https://github.com/user-attachments/assets/a339d8f9-266e-4e54-a93b-820c81747b32" />

### 2. Servicio caído

En esta prueba se detuvo manualmente uno de los microservicios para simular una falla de conexión.

El gateway intentó realizar varias solicitudes al servicio (usuarios), registrando cada fallo consecutivo.

<img width="1415" height="529" alt="image" src="https://github.com/user-attachments/assets/f6070315-a50e-4dfa-a013-d8db64361ddc" />

### 3. Circuito abierto
Después de varios fallos consecutivos, el Circuit Breaker cambió automáticamente al estado *OPEN*.

En este estado el gateway deja de enviar solicitudes al microservicio afectado y responde inmediatamente con un mensaje de error controlado.

Esto evita tiempos de espera innecesarios y protege la estabilidad del sistema.
>

- **Evidencia del mensaje mostrado al usuario 'Circuit Breaker abierto'**
  
  <img width="839" height="206" alt="image" src="https://github.com/user-attachments/assets/dbdb8d50-3248-4bde-8d81-5b2010a1db33" />
>

- **Evidencia de los logs circuito abierto**
  <img width="1423" height="405" alt="image" src="https://github.com/user-attachments/assets/38f28808-3605-4f05-97dc-818559aebf7b" />

### 4. Recuperación del servicio
Finalmente, el microservicio fue iniciado nuevamente para verificar el comportamiento del estado *HALF-OPEN*.

Después del tiempo de espera configurado:
- El gateway realizó una solicitud de prueba.
- El servicio respondió correctamente.
- El circuito volvió automáticamente al estado cerrado.

Esto permitió restaurar el funcionamiento normal del sistema sin reiniciar manualmente el gateway.
>

<img width="1414" height="580" alt="image" src="https://github.com/user-attachments/assets/f3baa2e7-fe8c-4507-89ca-fae5daac0a75" />

>

#### Evidencia de estado HALF-OPEN, además se puede evidenciar que debido al fallo se vuelve a reabrir el circuito
<img width="1064" height="743" alt="image" src="https://github.com/user-attachments/assets/9224c7d7-39ea-4b3c-ae52-4217fe920372" />


### Conclusiones de las pruebas

Las validaciones realizadas demostraron que:
- El Circuit Breaker detecta fallos correctamente.
- El circuito se abre después de múltiples errores.
- El gateway evita solicitudes innecesarias cuando un servicio falla.
- El estado HALF-OPEN permite verificar la recuperación del servicio.
- El sistema puede volver automáticamente a un estado normal de funcionamiento.


