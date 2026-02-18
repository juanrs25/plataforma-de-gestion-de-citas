# Arquitectura del Sistema:  Plataforma de Gestión de Citas Médicas
## Problema que resuelve.
Uno de los problemas que consideramos resuelve el sistema es la dificultad que existe para agendar una cita médica ya que permite hacerlo sin fila, ni turnos, ni llamadas.
## Roles Dentro del equipo

- Líder del proyecto: Ricardo Hoyos Lopez
- Encargado de documentación: John Alexander Pantoja Jiménez
- Encargado Técnico: Juan Manuel Rodriguez 
- Encargado de presentación: Heidy Gabriela Jalvin Avirama

## ¿Quien lo usará?
Doctores y pacientes

## ¿Qué pasaria si no existiera?
Los usuarios tendrían que gastar tiempo y dinero en transporte  para desplazarse al lugar en donde recibirá el servicio, además si quisieran hacerlo por llamada, seguirán sufriendo tiempos de espera excesivos. 

# Servicios del Sistema

- Autenticación
- Citas
- Historial
- Notificaciones

## ¿Qué partes pueden trabajar por separado?

De momento ninguna  de las funciones principales pueden trabajar por separado, debido a que todos tienen acceso a una única base de datos local.

## ¿Qué procesos son independientes?

El sistema contará con un módulo independiente de notificaciones implementado mediante una APi

# ¿Cómo se comunican?
## ¿Qué servicio necesita información de otro?
El servicio de autenticación necesita consultar a la base de datos. Para poder agendar una cita se necesita estar autenticado. Para obtener un historial se requiere de una cita, y para las notificaciones se requiere tener programada una cita.

# Tipo de arquitectura
Cliente servidor

## ¿Cuánto usuarios tendrá el sistema?
El sistema contará con 60 pacientes y 6 profesionales en el área de medicina general, posteriormente el sistema será escalable con el aumento de usuarios.

## ¿Necesita escalar?
Si debido al aumento de pacientes y profesionales.

## ¿Es un sistema pequeño o grande?
Es un sistema pequeño con poco usuarios iniciales, por lo cual hemos elegido la arquitectura de Cliente servidor, lo que permite una estructura simple y facil de implementar.

# Base de datos
## ¿Qué información debe guardarse?
- Información de los usuarios
- Citas agendadas, reprogramadas y canceladas
- Historial de citas
- Historial de pacientes
- Horarios de citas
- Horarios disponibles de los doctores
- Notificaciones enviadas
  
## ¿Qué datos son críticos?
- Datos personales de los usuarios
- Información de las citas

## ¿Qué pasaría si se pierden?
La pérdida de datos provocaría que el sistema dejará de funcionar correctamente, ya que se eliminaría información esencial como la de usuarios y sus citas. Esto generaría desorganización en la atención, afectando tanto a pacientes como a doctores. Además, los usuarios perderían confianza en la plataforma al percibir que su información personal y médica no está protegida. A esto se suman posibles consecuencias legales para la plataforma debido a la falta de privacidad e integridad en el manejo de los datos.

## ¿Todos los servicios usan la misma base de datos?
Sí, cada uno de los servicios del sistema utilizan la misma base de datos.

# Usuarios del Sistema
Pacientes y Doctores

# Riesgos y fallas 
## Identifaciar usuarios
## ¿Quién usará el sistema?
Doctores y Pacientes
## ¿Todos pueden hacer lo mismo?
No, cada usuario contará con un rol específico dentro de la plataforma, el cual determinará los permisos y acciones que puede realizar.  De esta manera, se puede garantizar un control adecuado sobre las funciones disponibles y la seguridad de la información manejada.

- Doctor: Revisa su agenda, historial de pacientes y confirma asistencia de citas.
- Paciente: Agenda, cancela, reprograma y consulta citas.

# Fallas y riesgos
## ¿Que pasaria si falla... ?
### Base de datos:
No se podrian consultar las citas de los usuarios y el sistema quedará inoperativo.
- Posibles soluciones:
1. Copias de seguridad
2. Base de datos secundaria
3. Información en varios servidores
### Servidor principal:
El sistema  no estaría disponible para los usuarios.
- Posibles soluciones:
1. Servidor de respaldo
2. Monitoreo del sistema
### Autenticación:
Lo ususario no podran iniciar sesion ni registrarse en el sistema.
- Posibles soluciones:
1. Permitir un acceso limitado sin autenticación para funciones básicas, como consultar información general o soporte.
2. Tener un segundo método de inicio de sesión como por ejemplo autenticación con google u otro servicio externo.
3. Mantener activas sesiones de usuarios que ya estaban logueados, para que no se pierda acceso inmediato.

### Citas:
Los usuarios no podrán agendar citas
- Posibles soluciones:
1. Validación previa de disponibilidad antes de confirmar la cita.
2. Implementar cache temporal para disponibilidad.

## Notificaciones:
Los usuarios no recibiran confirmaciones a su correo acerca de las citas.
- Posible solucion:
1. Implementar proveedor de respaldo, si el principal servidor no responde usar automaticamente el secundario.
