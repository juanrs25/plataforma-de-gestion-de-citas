

CREATE TABLE IF NOT EXISTS citas (
    id_citas INT AUTO_INCREMENT PRIMARY KEY,
    id_paciente_citas INT NOT NULL,
    id_doctor_citas INT NOT NULL,
    estado_citas ENUM('Agendado', 'Cancelado', 'Reprogramado') DEFAULT 'Agendado' NOT NULL,
    fecha_programacion_citas DATE NOT NULL,
    hora_programacion_citas TIME NOT NULL,
    fecha_creacion_citas TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);