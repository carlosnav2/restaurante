-- ====================================================================
-- Script de Inicialización de Base de Datos
-- Sistema de Pedidos - Restaurante Sazón Mexicano
-- ====================================================================
-- 
-- Este script crea la base de datos, tablas y datos iniciales
-- Ejecutar: mysql -u root -p < init_database.sql
-- O desde MySQL: SOURCE init_database.sql;
-- ====================================================================

-- ====================================================================
-- IMPORTANTE: Antes de ejecutar este script, asegúrate de que el
-- nombre de la base de datos coincida con tu configuración en .env
-- Por defecto se usa: restaurante_db
-- Si usas otro nombre, cambia "restaurante_db" en las siguientes líneas
-- ====================================================================

-- Crear base de datos si no existe
-- NOTA: Cambia "restaurante_db" por el nombre de tu base de datos si es diferente
CREATE DATABASE IF NOT EXISTS restaurante_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Usar la base de datos
USE restaurante_db;

-- ====================================================================
-- CREAR TABLAS
-- ====================================================================

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    rol ENUM('admin', 'mesero') NOT NULL,
    activo TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabla de productos
CREATE TABLE IF NOT EXISTS productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    activo TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabla de pedidos
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

-- Tabla de items de pedidos
CREATE TABLE IF NOT EXISTS pedido_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pedido_id INT NOT NULL,
    producto_id INT NOT NULL,
    producto_nombre VARCHAR(100) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    cantidad INT NOT NULL,
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabla de descuentos
CREATE TABLE IF NOT EXISTS descuentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    tipo ENUM('porcentaje', 'fijo') NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    activo TINYINT(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ====================================================================
-- INSERTAR USUARIOS
-- ====================================================================
-- Contraseñas hasheadas con sha256_crypt
-- Admin: admin123
-- Mesero: mesero123

DELETE FROM usuarios WHERE username IN ('admin', 'mesero');

INSERT INTO usuarios (username, password, nombre, rol, activo) VALUES
('admin', '$5$rounds=535000$RDH6CEb2c65wuZjk$MWv92OaL8XT5e4xIIaqFEL32G5e6tat70ovpQWBa0wA', 'Administrador', 'admin', 1),
('mesero', '$5$rounds=535000$VV/xQCqA5xl60UN1$xNUjBVmubDIOq81kZuJ7EYeJdK4KxrPrGaKV5MQdRTC', 'Mesero Principal', 'mesero', 1);

-- ====================================================================
-- INSERTAR PRODUCTOS
-- ====================================================================

DELETE FROM productos;

INSERT INTO productos (nombre, precio, categoria, activo) VALUES
-- Hamburguesas
('Hamburguesa Clásica', 45.00, 'Hamburguesas', 1),
('Hamburguesa Doble', 65.00, 'Hamburguesas', 1),
('Hamburguesa BBQ', 70.00, 'Hamburguesas', 1),
('Hamburguesa con Queso', 55.00, 'Hamburguesas', 1),
('Hamburguesa Especial', 75.00, 'Hamburguesas', 1),
('Hamburguesa Vegetariana', 50.00, 'Hamburguesas', 1),

-- Hot Dogs
('Hot Dog Simple', 30.00, 'Hot Dogs', 1),
('Hot Dog Especial', 40.00, 'Hot Dogs', 1),
('Hot Dog Mexicano', 45.00, 'Hot Dogs', 1),
('Hot Dog con Queso', 35.00, 'Hot Dogs', 1),

-- Bebidas
('Coca Cola', 15.00, 'Bebidas', 1),
('Pepsi', 15.00, 'Bebidas', 1),
('Agua', 10.00, 'Bebidas', 1),
('Jugo Natural', 20.00, 'Bebidas', 1),
('Horchata', 18.00, 'Bebidas', 1),
('Agua Fresca', 20.00, 'Bebidas', 1),
('Limonada', 18.00, 'Bebidas', 1),
('Refresco de Frutas', 16.00, 'Bebidas', 1),

-- Acompañamientos
('Papas Fritas', 20.00, 'Acompañamientos', 1),
('Aros de Cebolla', 25.00, 'Acompañamientos', 1),
('Nachos', 30.00, 'Acompañamientos', 1),
('Papas a la Francesa', 22.00, 'Acompañamientos', 1),
('Ensalada', 25.00, 'Acompañamientos', 1),

-- Tacos
('Tacos al Pastor', 35.00, 'Tacos', 1),
('Tacos de Carnitas', 40.00, 'Tacos', 1),
('Tacos de Asada', 38.00, 'Tacos', 1),
('Tacos de Pollo', 35.00, 'Tacos', 1),
('Tacos de Pescado', 42.00, 'Tacos', 1),

-- Mexicanos
('Quesadilla', 45.00, 'Mexicanos', 1),
('Burrito', 50.00, 'Mexicanos', 1),
('Enchiladas', 48.00, 'Mexicanos', 1),
('Chiles Rellenos', 52.00, 'Mexicanos', 1),
('Mole', 55.00, 'Mexicanos', 1),
('Pozole', 60.00, 'Mexicanos', 1),

-- Postres
('Flan', 25.00, 'Postres', 1),
('Churros', 20.00, 'Postres', 1),
('Pastel de Chocolate', 30.00, 'Postres', 1),
('Helado', 18.00, 'Postres', 1),
('Tres Leches', 28.00, 'Postres', 1),

-- Ensaladas
('Ensalada César', 35.00, 'Ensaladas', 1),
('Ensalada de la Casa', 30.00, 'Ensaladas', 1),
('Ensalada de Pollo', 40.00, 'Ensaladas', 1);

-- ====================================================================
-- INSERTAR DESCUENTOS
-- ====================================================================

DELETE FROM descuentos;

INSERT INTO descuentos (codigo, tipo, valor, activo) VALUES
('DESC10', 'porcentaje', 10, 1),
('DESC20', 'porcentaje', 20, 1),
('DESC30', 'porcentaje', 30, 1),
('FIJO15', 'fijo', 15, 1),
('FIJO25', 'fijo', 25, 1),
('FIJO50', 'fijo', 50, 1);

-- ====================================================================
-- VERIFICACIÓN
-- ====================================================================

-- Verificar usuarios
SELECT 'Usuarios creados:' AS info;
SELECT id, username, nombre, rol, activo FROM usuarios;

-- Verificar productos
SELECT 'Total de productos:' AS info, COUNT(*) AS total FROM productos;
SELECT categoria, COUNT(*) AS cantidad FROM productos GROUP BY categoria;

-- Verificar descuentos
SELECT 'Descuentos creados:' AS info;
SELECT id, codigo, tipo, valor, activo FROM descuentos;

-- ====================================================================
-- FIN DEL SCRIPT
-- ====================================================================
-- 
-- Credenciales para iniciar sesión:
--   👨‍💼 Admin: admin / admin123
--   👨‍🍳 Mesero: mesero / mesero123
-- 
-- Códigos de descuento disponibles:
--   - DESC10 (10% de descuento)
--   - DESC20 (20% de descuento)
--   - DESC30 (30% de descuento)
--   - FIJO15 (Q15 de descuento fijo)
--   - FIJO25 (Q25 de descuento fijo)
--   - FIJO50 (Q50 de descuento fijo)
-- ====================================================================

