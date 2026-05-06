# Laboratorio: Sistema que aprende a fallar 

## Fase 1 - Observación

- ¿Qué hace el sistema actualmente?


El sistema actualmente implementa un Circuit Breaker parcial, aplicado únicamente sobre el endpoint /mascotas. Su comportamiento se divide en dos escenarios:
Cuando el servicio está activo, el gateway recibe la petición, la redirige al microservicio backend en http://backend:5000/mascotas, obtiene la respuesta y la retorna al cliente con normalidad. En este caso el contador de fallos permanece en cero y el circuito se mantiene cerrado.
Cuando el servicio se detiene, el sistema entra en un modo de conteo de fallos. Cada petición que no logra conectarse con el backend incrementa el contador en 1, y el gateway responde con un error 503. Al momento en que ese contador supera los 3 fallos, el circuito se abre automáticamente. A partir de ese punto, el sistema deja de intentar conectarse al backend y responde directamente con el mensaje "servicio temporalmente no disponible", evitando así esperas innecesarias sobre un servicio que ya se sabe que está caído.
Adicionalmente, el endpoint /usuarios no tiene ningún tipo de protección: si ese servicio falla, el gateway no maneja el error y simplemente colapsa la petición sin control.


- ¿Se protege o insiste?

El sistema realizaambas cosas, dependiendo del momento, tiene un comportamiento en dos etapas:

Primero insiste (fallos 1, 2 y 3)
Cuando el servicio backend cae, el gateway no se rinde de inmediato. En cada petición que llega intenta conectarse de todas formas, espera hasta 2 segundos (el timeout), falla, y recién ahí incrementa el contador. Esto significa que durante los primeros 3 fallos el sistema sigue golpeando un servicio que ya está caído.

Y luego se protege a partir del fallo 3 una vez que el contador llega a 3, el circuito se abre y el comportamiento cambia completamente. El gateway ya no intenta conectarse al backend, sino que responde de forma inmediata con "servicio temporalmente no disponible". Esto es la protección: respuesta rápida, sin esperas, sin intentos inútiles.

## Fase 2 

- ¿Cada servicio debe tener su propio contador de fallos?

Sí, porque si comparten un solo contador, los fallos de mascotas afectarían el circuito de usuarios y viceversa. Son servicios independientes y deben fallar de forma independiente.

- ¿El circuito debe abrirse de forma independiente por servicio?

Sí, si backend cae pero usuarios sigue funcionando, el gateway debe seguir respondiendo /usuarios con normalidad. Si hubiera un solo circuito global, un servicio caído bloquearía a todos los demás.

- ¿Qué pasa si falla un servicio pero el otro sigue funcionando?

El usuario aún puede usar los endpoints del servicio que funciona. El gateway responde con error solo en el endpoint afectado, mientras los demás operan con normalidad.

## Fase 3 invesrigar "Half-open"

- ¿Qué significa "half-open"?

Es un estado intermedio del Circuit Breaker. El circuito estaba completamente abierto rechazando todas las peticiones, pero después de un tiempo de espera definido, permite pasar una única petición de prueba para verificar si el servicio caído ya se recuperó, sin comprometer la estabilidad del sistema.

- ¿Cuándo se vuelve a intentar una llamada?

El sistema vuelve a intentar una llamada cuando se cumplen dos condiciones simultáneamente: 

1. Que haya transcurrido el tiempo de espera definido desde que el circuito se abrió, Lo único que hace es guardar la hora exacta en que el circuito se abrió, y cada vez que llega una petición realiza una simple comparación matemática: si la diferencia entre la hora actual y la hora de apertura es mayor o igual al tiempo definido, el circuito entra en estado Half-Open y deja pasar una única petición de prueba; si no ha pasado suficiente tiempo, simplemente rechaza la petición de forma inmediata.

2. Que llegue una nueva petición que "despierte" al sistema.Si nadie hace peticiones durante horas, el sistema no hará absolutamente nada por sí solo, no importa cuánto tiempo haya pasado siempre necesita que llegue una petición para que se dé cuenta de que ya puede intentar recuperarse.

- ¿Qué pasa si el servicio vuelve a fallar?

El circuito regresa al estado abierto inmediatamente y reinicia el contador de tiempo de espera. El sistema volverá a intentar pasado ese tiempo nuevamente.
