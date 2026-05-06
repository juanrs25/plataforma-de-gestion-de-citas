# Fase 1
**1. ¿Qué hace el sistema actualmente?**

Actualmente, el sistema intenta conectarse al servicio de mascotas cada vez que se realiza una petición al endpoint /mascotas. Como el servicio de mascotas está apagado, las solicitudes fallan y el API gateway registra cada error aumentando el contador de fallos

Después de tres fallos, el Circuit Breaker abre el circuito y el sistema deja de intentar conectarse al backend. A partir de ese momento, las nuevas peticiones ya no se envían al servicio de mascotas y el gateway responde directamente con un mensaje de error indicando "Servicio mascotas temporalmente caido".

2.**¿Se protege o insiste?**

Al principio insiste intentando conectarse al servicio mascotas mientras ocurren los primeros fallos. Despues, el Circuit braker abre el circuito y el sistema se protege dejando de enviar solicitudes al backend.


Respuesta del Gateway al detener el contendor:

![Respuesta del Gateway durante las primeras solicitudes](evidencias/Fase1_RGT.png)

Logs despues despues de los fallos con el circuit braker abierto

![logs con fallos y circuito abierto](evidencias/Fase1_Logs.png)

Mensaja de cirtucito abierto

![Circuito abierto](evidencias/Fase1_RCB.png)