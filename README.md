# Plataforma de Gestión de Citas Médicas

## Descripción del Proyecto

La Plataforma de Gestión de Citas Médicas es un sistema diseñado para facilitar el agendamiento, gestión y seguimiento de citas médicas entre pacientes y doctores, eliminando la necesidad de filas presenciales y largas esperas telefónicas.

---

## Problema que Resuelve

El sistema resuelve la dificultad que existe para agendar una cita médica, permitiendo hacerlo de manera digital sin necesidad de:

- Hacer filas
- Tomar turnos presenciales
- Realizar llamadas con tiempos de espera excesivos

---

## Usuarios del Sistema

-  Doctores
-  Pacientes

---

##  ¿Qué pasaría si no existiera?

- Los usuarios gastarían tiempo y dinero en transporte.
- Se mantendrían los tiempos de espera por llamadas.
- Habría desorganización en la gestión de citas.
- Disminuiría la eficiencia del servicio médico.

---

#  Arquitectura del Sistema

## Servicios Principales

El sistema está dividido en los siguientes módulos:

- Autenticación
- Gestión de Citas
- Historial
- Notificaciones

Actualmente, todos los servicios utilizan una única base de datos local.

El módulo de notificaciones se implementará como un servicio independiente mediante una API.

---

# Comunicación entre Servicios

- El servicio de autenticación consulta la base de datos.
- Para agendar una cita, el usuario debe estar autenticado.
- Para consultar el historial, debe existir una cita registrada.
- Las notificaciones dependen de una cita previamente programada.

---

# Tipo de Arquitectura

 Cliente–Servidor

### Justificación

Se eligió esta arquitectura porque:

- Es un sistema pequeño.
- Tiene pocos usuarios iniciales (60 pacientes y 6 doctores).
- Es simple y fácil de implementar.
- Permite escalar en el futuro.

---

# Base de Datos

## Información almacenada

- Información de usuarios
- Citas (agendadas, reprogramadas, canceladas)
- Historial médico
- Horarios disponibles de doctores
- Notificaciones enviadas

## Datos Críticos

- Datos personales de los usuarios
- Información de citas
- Historial médico

## Riesgo si se pierden los datos

- El sistema quedaría inoperativo.
- Se perdería información médica.
- Habría desorganización en la atención.
- Se afectaría la confianza de los usuarios.
- Posibles problemas legales.

Todos los servicios utilizan la misma base de datos.

---

# Roles del Sistema

## Doctor
- Revisa agenda
- Consulta historial de pacientes
- Confirma citas

## Paciente
- Agenda citas
- Cancela citas
- Reprograma citas
- Consulta historial

---

# Fallas y Riesgos

## Falla en Base de Datos
**Impacto:** Sistema inoperativo.

**Soluciones:**
- Copias de seguridad automáticas.
- Base de datos secundaria.
- Información replicada en varios servidores.

---

## Falla en Servidor Principal
**Impacto:** Sistema no disponible.

**Soluciones:**
- Servidor de respaldo.
- Monitoreo continuo del sistema.

---

##  Falla en Autenticación
**Impacto:** Usuarios no pueden iniciar sesión.

**Soluciones:**
- Acceso limitado sin autenticación para funciones básicas.
- Segundo método de inicio de sesión (Google u otro servicio externo).
- Mantener sesiones activas previamente iniciadas.

---

##  Falla en Gestión de Citas
**Impacto:** No se pueden agendar citas.

**Soluciones:**
- Validación previa de disponibilidad.
- Implementación de caché temporal para horarios.

---

## Falla en Notificaciones
**Impacto:** Usuarios no reciben confirmaciones por correo.

**Soluciones:**
- Implementar proveedor de correo de respaldo.
- Cambio automático a proveedor secundario si el principal falla.

---

# Escalabilidad

El sistema iniciará con:

- 60 pacientes
- 6 profesionales en medicina general

Está diseñado para escalar conforme aumente el número de usuarios y funcionalidades.

---

En desarrollo.
