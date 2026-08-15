CREATE DATABASE IF NOT EXISTS historial_db;
USE historial_db;

CREATE TABLE IF NOT EXISTS RegistroHistorial (
    id_historial INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_cita INT NOT NULL,
    accion VARCHAR(50) NOT NULL, -- 'CITA_CREADA', 'CITA_REPROGRAMADA', 'CITA_ELIMINADA'
    detalles TEXT,               -- Ej: "Cita programada para el 15 de Octubre"
    fecha_evento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);