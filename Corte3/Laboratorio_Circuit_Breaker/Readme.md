FASE 1 – OBSERVAR
Qué hace el sistema actualmente?
Actualmente el sistema funciona con un mecanismo de protección implementado en el API Gateway. Cada vez que un usuario realiza una solicitud al servicio de mascotas, el gateway intenta comunicarse con el backend.
Si el backend responde correctamente, la información se entrega normalmente y el contador de errores se reinicia. Sin embargo, cuando el backend empieza a fallar o no responde, el sistema registra cada fallo consecutivo.
Al llegar a 3 fallos seguidos, el gateway interpreta que el servicio presenta problemas y activa el circuito abierto. Desde ese momento deja de enviar solicitudes al backend y responde directamente al usuario con un mensaje de error indicando que el servicio no está disponible temporalmente.
