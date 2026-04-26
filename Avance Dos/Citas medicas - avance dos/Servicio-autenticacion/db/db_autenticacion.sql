-- Estructura de la tabla de Usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre_usuario VARCHAR(100) NOT NULL,
    correo_usuario VARCHAR(150) NOT NULL UNIQUE,
    password_usuario VARCHAR(255) NOT NULL,
    telefono_usuario VARCHAR(20),
    direccion_usuario TEXT,
    rol_usuario ENUM('Paciente', 'Doctor') DEFAULT 'Paciente',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



-- Insertar Doctores y Pacientes
INSERT INTO usuarios (id_usuario, nombre_usuario, correo_usuario, password_usuario, telefono_usuario, direccion_usuario, rol_usuario) 
VALUES 
(1, 'Dr. Gregory House', 'dr.house@clinica.com', 'password123', '555-0101', 'Consultorio 101', 'Doctor'),
(2, 'Juan Perez', 'juan.perez@email.com', 'password123', '555-0202', 'Calle Principal 123', 'Paciente'),
(3, 'Ana Gomez', 'ana.gomez@email.com', 'password123', '555-0303', 'Avenida Central 456', 'Paciente'),
(4, 'Dra. Meredith Grey', 'meredith.grey@clinica.com', 'pass123', '555-0404', 'Consultorio 202', 'Doctor'),
(5, 'Dr. Shaun Murphy', 'shaun.murphy@clinica.com', 'pass123', '555-0505', 'Consultorio 303', 'Doctor'),
(6, 'Carlos Ruiz', 'carlos.ruiz@email.com', 'pass123', '555-0606', 'Calle Sur 789', 'Paciente'),
(7, 'Elena Torres', 'elena.torres@email.com', 'pass123', '555-0707', 'Barrio Norte 101', 'Paciente'),
(8, 'Roberto Gomez', 'roberto.g@email.com', 'pass123', '555-0808', 'Av. Occidente 202', 'Paciente');