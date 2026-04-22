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