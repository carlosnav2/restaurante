import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

def get_db_connection():
    """Obtiene una conexión a la base de datos"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error conectando a MySQL: {e}")
        raise

def init_database():
    """Inicializa la base de datos y crea las tablas si no existen"""
    try:
        # Conectar sin especificar base de datos
        temp_config = DB_CONFIG.copy()
        temp_config.pop('database', None)
        conn = mysql.connector.connect(**temp_config)
        cursor = conn.cursor()
        
        # Crear base de datos si no existe
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.close()
        conn.close()
        
        # Conectar a la base de datos creada
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Crear tablas
        tables = [
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                nombre VARCHAR(100) NOT NULL,
                rol ENUM('admin', 'mesero') NOT NULL,
                activo TINYINT(1) DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,
            """
            CREATE TABLE IF NOT EXISTS pedidos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                numero_pedido VARCHAR(20) NOT NULL,
                total DECIMAL(10,2) NOT NULL,
                descuento DECIMAL(10,2) DEFAULT 0,
                total_final DECIMAL(10,2) NOT NULL,
                estado ENUM('pending', 'preparing', 'ready', 'delivered') DEFAULT 'pending',
                fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tiempo_preparacion INT DEFAULT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,
            """
            CREATE TABLE IF NOT EXISTS productos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                precio DECIMAL(10,2) NOT NULL,
                categoria VARCHAR(50) NOT NULL,
                activo TINYINT(1) DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,
            """
            CREATE TABLE IF NOT EXISTS pedido_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                pedido_id INT NOT NULL,
                producto_id INT NOT NULL,
                producto_nombre VARCHAR(100) NOT NULL,
                precio DECIMAL(10,2) NOT NULL,
                cantidad INT NOT NULL,
                FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,
            """
            CREATE TABLE IF NOT EXISTS descuentos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                codigo VARCHAR(20) UNIQUE NOT NULL,
                tipo ENUM('porcentaje', 'fijo') NOT NULL,
                valor DECIMAL(10,2) NOT NULL,
                activo TINYINT(1) DEFAULT 1
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        ]
        
        for table in tables:
            cursor.execute(table)
        
        # Insertar usuarios de ejemplo si no existen
        cursor.execute("SELECT COUNT(*) as count FROM usuarios")
        user_count = cursor.fetchone()[0]
        
        if user_count == 0:
            from passlib.context import CryptContext
            import os
            import warnings
            
            # Desactivar detección automática de bugs en bcrypt
            os.environ.setdefault('PASSLIB_DISABLE_WRAP_BUG_DETECTION', '1')
            warnings.filterwarnings("ignore", category=UserWarning, module="passlib")
            
            # Crear contexto de contraseñas igual que en auth.py
            # Usar sha256_crypt como esquema principal
            pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
            
            usuarios_iniciales = [
                ('admin', 'admin123', 'Administrador', 'admin'),
                ('mesero', 'mesero123', 'Mesero Principal', 'mesero')
            ]
            
            for username, password, nombre, rol in usuarios_iniciales:
                hashed_password = pwd_context.hash(password)
                cursor.execute(
                    "INSERT INTO usuarios (username, password, nombre, rol) VALUES (%s, %s, %s, %s)",
                    (username, hashed_password, nombre, rol)
                )
        
        # Insertar productos de ejemplo si no existen
        cursor.execute("SELECT COUNT(*) as count FROM productos")
        product_count = cursor.fetchone()[0]
        
        if product_count == 0:
            productos_iniciales = [
                ('Hamburguesa Clásica', 45.00, 'Hamburguesas'),
                ('Hamburguesa Doble', 65.00, 'Hamburguesas'),
                ('Hamburguesa BBQ', 70.00, 'Hamburguesas'),
                ('Hamburguesa con Queso', 55.00, 'Hamburguesas'),
                ('Hot Dog Simple', 30.00, 'Hot Dogs'),
                ('Hot Dog Especial', 40.00, 'Hot Dogs'),
                ('Hot Dog Mexicano', 45.00, 'Hot Dogs'),
                ('Coca Cola', 15.00, 'Bebidas'),
                ('Agua', 10.00, 'Bebidas'),
                ('Jugo Natural', 20.00, 'Bebidas'),
                ('Horchata', 18.00, 'Bebidas'),
                ('Agua Fresca', 20.00, 'Bebidas'),
                ('Papas Fritas', 20.00, 'Acompañamientos'),
                ('Aros de Cebolla', 25.00, 'Acompañamientos'),
                ('Nachos', 30.00, 'Acompañamientos'),
                ('Tacos al Pastor', 35.00, 'Tacos'),
                ('Tacos de Carnitas', 40.00, 'Tacos'),
                ('Quesadilla', 45.00, 'Mexicanos'),
                ('Burrito', 50.00, 'Mexicanos'),
                ('Enchiladas', 48.00, 'Mexicanos'),
                ('Flan', 25.00, 'Postres'),
                ('Churros', 20.00, 'Postres'),
            ]
            
            for nombre, precio, categoria in productos_iniciales:
                cursor.execute(
                    "INSERT INTO productos (nombre, precio, categoria) VALUES (%s, %s, %s)",
                    (nombre, precio, categoria)
                )
        
        # Insertar descuentos de ejemplo
        cursor.execute("SELECT COUNT(*) as count FROM descuentos")
        discount_count = cursor.fetchone()[0]
        
        if discount_count == 0:
            descuentos_iniciales = [
                ('DESC10', 'porcentaje', 10),
                ('DESC20', 'porcentaje', 20),
                ('FIJO15', 'fijo', 15)
            ]
            
            for codigo, tipo, valor in descuentos_iniciales:
                cursor.execute(
                    "INSERT INTO descuentos (codigo, tipo, valor) VALUES (%s, %s, %s)",
                    (codigo, tipo, valor)
                )
        
        conn.commit()
        cursor.close()
        conn.close()
        
    except Error as e:
        print(f"Error inicializando base de datos: {e}")
        raise

