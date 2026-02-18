GUÍA DE ACTIVIDAD 2
Arquitectura del Sistema en GitHub


Roles dentro del equipo asignados
Líder del proyecto: Ricardo Hoyos Lopez
Encargado de documentación: John Alexander Pantoja Jiménez
Encargado Técnico: Juan Manuel Rodriguez 
Encargado de presentación: Heidy Gabriela Jalvin Avirama
Acceso al repositorio en GitHub: ok

PARTE 1 — ENTENDER EL PROBLEMA
Paso 1: Responder juntos
¿Qué problema resuelve el sistema?

Uno de los problemas que consideramos resuelve el sistema es la dificultad que existe para agendar una cita médica ya que permite hacerlo sin fila, ni turnos, ni llamadas.


¿Quién lo usará?

Doctores y pacientes 

¿Qué pasaría si no existiera?

Los usuarios tendrían que gastar tiempo y dinero en transporte  para desplazarse al lugar en donde recibirá el servicio, además si quisieran hacerlo por llamada, seguirán sufriendo tiempos de espera excesivos. 


PARTE 2 – IDENTIFICAR LOS SERVICIOS
Paso 2: Dividir el sistema
Un sistema distribuido se divide en servicios.
Preguntas guía:
¿Qué funciones principales tiene el sistema?
 
Autenticación
Citas
Historial
Notificaciones

¿Qué partes pueden trabajar por separado?

De momento ninguna  de las funciones principales pueden trabajar por separado, debido a que todos tienen acceso a una única base de datos local.

¿Qué procesos son independientes?

El sistema contará con un módulo independiente de notificaciones implementado mediante una API


PARTE 3 – ¿CÓMO SE COMUNICAN?
Paso 3: Conexión entre servicios
Respondan:
¿Qué servicio necesita información de otro?
El servicio de autenticación necesita consultar a la base de datos. Para poder agendar una cita se necesita estar autenticado. Para obtener un historial se requiere de una cita, y para las notificaciones se requiere tener programada una cita.



PARTE 4 – ELEGIR LA ARQUITECTURA
Paso 4: Tipo de arquitectura
Decidan cuál usarán:
X Cliente–Servidor
☐ Arquitectura en capas
☐ Microservicios
☐ Basados en eventos
☐ Híbrida
Preguntas guía:
¿Cuántos usuarios tendrá el sistema?
El sistema contará con 60 pacientes y 6 profesionales en la área de medicina general, posteriormente el sistema será escalable  con el aumento de usuarios

¿Necesita escalar?

Si,  debido al aumento de usuarios y profesionales

¿Es un sistema pequeño o grande?
el sistema es pequeño

Justifiquen su elección:
Elegimos esta arquitectura (cliente-servidor) porque es un sistema pequeño con pocos usuarios iniciales, lo que permite una estructura simple y fácil de implementar. Además, permite escalar el sistema en el futuro si se aumenta el número de usuarios o se agregan nuevas funcionalidades.

PARTE 5 – BASE DE DATOS
Paso 5: Datos del sistema
Respondan:
¿Qué información debe guardarse?
Información de los usuarios
citas agendadas, reprogramadas, canceladas
historial de citas
historial de paciente
Horarios de citas
Horarios disponibles de los doctores
Notificaciones enviadas

¿Qué datos son críticos?
Datos personales de los usuarios
información de las citas
Historial médico

¿Qué pasaría si se pierden?
Si se pierden los datos, el sistema dejaría de funcionar correctamente, ya que no habría  información de usuarios, citas ni historial médico. Esto causaría desorganización en la atención, afectaría a pacientes y doctores y se perdería la confianza de los usuarios en la plataforma al ver que su información personal y médica no está segura dentro del sistema, aparte de eso la plataforma podría tener problemas legales

Pregunta clave:
¿Todos los servicios usan la misma base de datos o cada uno tiene la suya?

Si. Cada uno de los servicios del sistema utilizan la misma base de datos 

PARTE 6 – FALLAS Y RIESGOS
Paso 6: Identificar usuarios
¿Quién usará el sistema?

Doctores y pacientes.
Pregunta clave:
¿Todos pueden hacer lo mismo?
No, cada uno tendrá roles diferentes 

Doctor: Revisa su agenda, historial de pacientes y confirma citas 
Paciente: Agenda, cancela, reprograma y consulta citas.

PARTE 7 — FALLAS Y RIESGOS
Paso 7: Pensar como ingenieros reales
¿Qué pasaría si falla:
base de datos: No se podrán consultar las citas de los usuarios y el sistema quedará inoperativo
Posibles soluciones:
Copias de seguridad
base de datos secundaria
Información en varios servidores(SD)

servidor principal: El sistema no estaría disponibles para los usuarios
	Posibles soluciones:
Servidor de respaldo
Monitoreo del sistema

Autenticación: Los usuarios no podrán iniciar sesión ni registrarse en el sistema.
Posible soluciones: 
Permitir un acceso limitado sin autenticación para funciones básicas, como consultar información general o soporte.
tener un segundo método de inicio de sesión como por ejemplo autenticación con google u otro servicio externo.
mantener activas sesiones de usuarios que ya estaban logueados, para que no se pierda acceso inmediato 


Citas: Los usuarios no podrán agendar las citas.
Posibles soluciones:
Validación previa de disponibilidad antes de confirmar cita.
Implementar caché temporal para disponibilidad.

Notificaciones:  Los usuarios no recibirán confirmaciones a su correo acerca de sus citas 
	Posibles solucion:
 Implementar proveedor de respaldo, Si el proveedor principal no responde automáticamente usa el secundario.


