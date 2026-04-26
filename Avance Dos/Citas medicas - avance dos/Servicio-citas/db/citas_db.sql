-- Estructura de la tabla de Citas
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

(2, 1, 'Agendado', '2026-04-28', '08:30:00'),
(3, 1, 'Agendado', '2026-04-29', '09:30:00'),
(6, 1, 'Agendado', '2026-04-29', '08:00:00'),
(2, 1, 'Cancelado', '2026-04-30', '14:00:00'),


(7, 4, 'Agendado', '2026-04-28', '08:00:00'),
(8, 4, 'Reprogramado', '2026-04-30', '11:00:00'),
(2, 4, 'Agendado', '2026-04-30', '14:30:00'),


(3, 5, 'Agendado', '2026-04-30', '08:00:00'),
(6, 5, 'Agendado', '2026-04-28', '09:00:00'),
(7, 5, 'Cancelado', '2026-04-28', '10:00:00'), 
(8, 5, 'Agendado', '2026-04-29', '15:00:00');