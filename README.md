# Arquitectura del Sistema:  Plataforma de Gestión de Citas Médicas
## Problema que resuelve
Uno de los problemas que consideramos resuelve el sistema es la dificultad que existe para agendar una cita médica ya que permite hacerlo sin fila, ni turnos, ni llamadas.
## Roles entro del equipo

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

El sistema contará con un módulo independiente de notificaciones implementado mediante una API

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
