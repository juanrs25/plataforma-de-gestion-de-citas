# GUÍA DE ACTIVIDAD 2

## Arquitectura del Sistema en GitHub
**Unidad 1 – Introducción a los Sistemas distribuidos**  

---

## Información del Proyecto

### Nombre del proyecto
Plataforma de gestión de citas médicas

### Problema que resuelve el sistema
El sistema aborda la dificultad que enfrentan las personas al momento de agendar una cita médica de manera rápida y eficiente. Actualmente, muchos usuarios deben acudir presencialmente para obtener un turno o realizar llamadas telefónicas, lo que implica tiempos de espera prolongados, limitaciones de horario en atención, procesos poco prácticos.
La solución propuesta permite gestionar citas médicas en línea, de forma ágil y segura, con disponibilidad 24/7, eliminando la necesidad de filas presenciales y reduciendo la dependencia de llamadas telefónicas.

### Roles dentro del equipo
- Líder del proyecto: Ricardo Hoyos Lopez  
- Encargado de documentación: John Alexander Pantoja Jiménez  
- Encargado Técnico: Juan Manuel Rodriguez  
- Encargado de presentación: Heidy Gabriela Jalvin Avirama  

### Acceso al repositorio en GitHub
ok

---

# PARTE 1 — ENTENDER EL PROBLEMA

## Paso 1: Responder juntos

### ¿Qué problema resuelve el sistema?
Consideramos que el problema que resuelve el sistema es la dificultad que existe para agendar una cita médica de forma rápida y sin necesidad de filas, turnos presenciales ni llamadas telefónicas, con un servicio 24/7 en línea.

### ¿Quién lo usará?
- Pacientes  
- Doctores  

### ¿Qué pasaría si no existiera?
Los usuarios tendrán que seguir desplazándose a los centros de atención, perder tiempo en largas colas o salas de espera, gastar dinero en transportes y en caso de hacerlo por vía telefónica enfrentarse a esperas prolongadas.

---

# PARTE 2 – IDENTIFICAR LOS SERVICIOS

## Paso 2: Dividir el sistema
Un sistema distribuido se divide en servicios.

### ¿Qué funciones principales tiene el sistema?
- Autenticación  
- Gestión de citas (Buscar disponibilidad, reservar, reprogramar, cancelar)  
- Historial de citas (Registro de eventos: agendada, reprogramada, cancelada, asistida)  
- Notificaciones (Envío de correo electrónico)  

### ¿Qué partes pueden trabajar por separado?
Por el momento ninguna de las funciones, a excepción de las notificaciones, pueden trabajar de forma independiente, debido a que todas acceden a una única base de datos local.

### ¿Qué procesos son independientes?
El sistema cuenta con un módulo independiente de notificaciones implementado mediante una API.

---

# PARTE 3 – ¿CÓMO SE COMUNICAN?

## Paso 3: Conexión entre servicios

### ¿Qué servicio necesita información de otro?
- El servicio de autenticación necesita consultar a la base de datos.  
- El servicio de gestión de citas requiere que el usuario esté autenticado.  
- El servicio de historial de citas muestra el registro de eventos asociados a citas previas. No requiere cita activa para mostrar registros históricos.  
- El servicio de notificaciones consume eventos de la gestión de citas para mandar las notificaciones al correo.  

---

# PARTE 4 – ELEGIR LA ARQUITECTURA

## Paso 4: Tipo de arquitectura

### Arquitectura seleccionada
X Cliente–Servidor  
- Arquitectura en capas  
- Microservicios  
- Basados en eventos  
- Híbrida  

### ¿Cuántos usuarios tendrá el sistema?
El sistema contará con 60 pacientes y 6 profesionales en el área de medicina general. Se prevé escalabilidad con el aumento de usuarios.

### ¿Necesita escalar?
Sí, debido al aumento previsto de usuarios y profesionales.

### ¿Es un sistema pequeño o grande?
El sistema es pequeño en la fase inicial.

### Justificación
Elegimos la arquitectura cliente-servidor para un desarrollo inicial ya que se puede hacer rápido y controlado, manteniendo una arquitectura modular que facilite la migración futura a microservicios cuando los requisitos lo demanden.

---

# PARTE 5 – BASE DE DATOS

## Paso 5: Datos del sistema

### ¿Qué información debe guardarse?
- Información de los usuarios (Datos personales y roles)  
- Citas (estado, fecha, hora, doctor, paciente)  
- Historial de citas (creadas, reprogramadas, canceladas, asistidas)  
- Horarios disponibles de los doctores  
- Notificaciones enviadas  

### ¿Qué datos son críticos?
- Datos personales de los usuarios  
- Información de las citas  
- Historial de citas  

### ¿Qué pasaría si se pierden?
La pérdida de estos datos provocaría que el sistema dejará de funcionar correctamente, ya que se eliminaría información esencial, como la de usuarios y sus citas. Esto generaría desorganización en la atención, afectando tanto a pacientes como a doctores. Además, los usuarios perderían confianza en la plataforma al percibir que su información personal y médica no está protegida. También se pueden derivar consecuencias legales para la plataforma debido al manejo inadecuado de datos personales.

### ¿Todos los servicios usan la misma base de datos o cada uno tiene la suya?
En esta fase inicial, sí. Cada uno de los servicios del sistema utilizan la misma base de datos.

---

# PARTE 6 – FALLAS Y RIESGOS

## Paso 6: Identificar usuarios

### ¿Quién usará el sistema?
- Doctores  
- Pacientes  

### ¿Todos pueden hacer lo mismo?
No, cada usuario contará con un rol y permisos distintos dentro de la plataforma. De esta manera, se garantiza un control adecuado sobre las funciones disponibles y la seguridad de la información.

- Doctor: Revisa su agenda, confirma o cancela citas.  
- Paciente: Busca disponibilidad, agenda, cancela, reprograma y consulta historial de citas, recibe notificaciones.  

---



