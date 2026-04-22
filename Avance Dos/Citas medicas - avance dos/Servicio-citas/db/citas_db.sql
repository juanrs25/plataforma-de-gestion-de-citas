

CREATE TABLE IF NOT EXISTS citas (
    id_citas INT AUTO_INCREMENT PRIMARY KEY,
    id_paciente_citas INT NOT NULL,
    id_doctor_citas INT NOT NULL,
    estado_citas ENUM('Agendado', 'Cancelado', 'Reprogramado') DEFAULT 'Agendado' NOT NULL,
    fecha_programacion_citas DATE NOT NULL,
    hora_programacion_citas TIME NOT NULL,
    fecha_creacion_citas TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


INSERT INTO citas (id_paciente_citas, id_doctor_citas, estado_citas, fecha_programacion_citas, hora_programacion_citas) 
VALUES 

(2, 1, 'Agendado', '2026-05-15', '08:30:00'),


(3, 1, 'Agendado', '2026-05-15', '09:30:00'),


(2, 1, 'Cancelado', '2026-04-20', '14:00:00'),


(3, 1, 'Reprogramado', '2026-05-16', '16:00:00');