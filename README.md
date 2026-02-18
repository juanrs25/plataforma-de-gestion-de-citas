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

