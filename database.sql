-- ============================================
-- SCRIPT DE CREACIÓN DE BASE DE DATOS
-- ============================================
-- Ejecuta este script en tu base de datos MySQL de Railway
-- antes de usar la aplicación
-- ============================================

-- Crear tablas
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    rol ENUM('admin', 'mesero') NOT NULL,
    activo TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS pedidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero_pedido VARCHAR(20) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    descuento DECIMAL(10,2) DEFAULT 0,
    total_final DECIMAL(10,2) NOT NULL,
    estado ENUM('pending', 'preparing', 'ready', 'delivered') DEFAULT 'pending',
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tiempo_preparacion INT DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    activo TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS pedido_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pedido_id INT NOT NULL,
    producto_id INT NOT NULL,
    producto_nombre VARCHAR(100) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    cantidad INT NOT NULL,
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS descuentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    tipo ENUM('porcentaje', 'fijo') NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    activo TINYINT(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ⚠️ IMPORTANTE: Este INSERT puede no funcionar porque el hash puede ser incorrecto
-- Mejor opción: Usa el botón en la pantalla de login o ejecuta create_admin_user.php
--
-- Si quieres usar SQL directamente, primero genera el hash ejecutando:
-- php -r "echo password_hash('Admin123!', PASSWORD_DEFAULT);"
-- Luego reemplaza el hash abajo con el generado

-- Crear usuario administrador por defecto
-- Usuario: admin
-- Contraseña: Admin123!
-- NOTA: Este hash puede no funcionar. Mejor usa el botón web o el script PHP
INSERT INTO usuarios (username, password, nombre, rol, activo) VALUES 
('admin', '$2y$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'Administrador', 'admin', 1)
ON DUPLICATE KEY UPDATE password = VALUES(password), activo = 1;

-- ⚠️ Si el hash no funciona, usa una de estas opciones:
-- 1. Ve a la pantalla de login y haz clic en "Crear Usuario Admin"
-- 2. Ejecuta: php create_admin_user.php
-- 3. O genera un nuevo hash y actualiza el INSERT arriba

-- NOTA: Los productos y descuentos se importan desde tu dump de base de datos
-- Si necesitas datos de ejemplo, puedes descomentar las siguientes líneas:

-- INSERT INTO productos (nombre, precio, categoria) VALUES 
-- ('Hamburguesa Clásica', 45.00, 'Hamburguesas'),
-- ('Hamburguesa Doble', 65.00, 'Hamburguesas'),
-- ... (más productos)
-- ON DUPLICATE KEY UPDATE nombre=nombre;

-- INSERT INTO descuentos (codigo, tipo, valor) VALUES 
-- ('DESC10', 'porcentaje', 10),
-- ('DESC20', 'porcentaje', 20),
-- ('FIJO15', 'fijo', 15)
-- ON DUPLICATE KEY UPDATE codigo=codigo;

