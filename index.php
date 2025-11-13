<?php
// ====================================================================
// SISTEMA DE PEDIDOS COMPLETO CON BASE DE DATOS
// ====================================================================
session_start();

// --- VERIFICAR SI ESTÁ LOGUEADO ---
$isLoggedIn = isset($_SESSION['user_id']);
$userRole = $_SESSION['user_role'] ?? null;
$userName = $_SESSION['user_name'] ?? null;

// --- CONFIGURACIÓN DE BASE DE DATOS ---
// Usar variables de entorno si están disponibles (Docker/Railway), sino usar valores por defecto
// Railway proporciona: MYSQLHOST, MYSQLUSER, MYSQLPASSWORD, MYSQLDATABASE
$db_host = getenv('DB_HOST') ?: getenv('MYSQLHOST') ?: 'localhost';
// Convertir 'localhost' a '127.0.0.1' para forzar TCP/IP en lugar de socket Unix
if ($db_host === 'localhost') {
    $db_host = '127.0.0.1';
}
define('DB_HOST', $db_host);
define('DB_USER', getenv('DB_USER') ?: getenv('MYSQLUSER') ?: 'root');
define('DB_PASS', getenv('DB_PASS') ?: getenv('MYSQLPASSWORD') ?: '');
define('DB_NAME', getenv('DB_NAME') ?: getenv('MYSQLDATABASE') ?: 'restaurante_db');
define('DB_PORT', getenv('DB_PORT') ?: getenv('MYSQLPORT') ?: 3306);

// Crear conexión con manejo de errores mejorado
$conn = @new mysqli(DB_HOST, DB_USER, DB_PASS, '', DB_PORT);
if ($conn->connect_error) {
    die("Error de conexión a la base de datos: " . $conn->connect_error . 
        " (Host: " . DB_HOST . ", Puerto: " . DB_PORT . ")");
}

// Crear base de datos si no existe
if (!$conn->query("CREATE DATABASE IF NOT EXISTS " . DB_NAME)) {
    die("Error creando base de datos: " . $conn->error);
}

// Seleccionar base de datos
$conn->select_db(DB_NAME);

// --- CREAR TABLAS SI NO EXISTEN ---
$sql_tables = "
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
";

if (!$conn->multi_query($sql_tables)) {
    die("Error creando tablas: " . $conn->error);
}

// Limpiar resultados múltiples
while ($conn->next_result()) {;}


// Insertar usuarios de ejemplo si no existen
$check_users = $conn->query("SELECT COUNT(*) as count FROM usuarios");
$row = $check_users->fetch_assoc();
if ($row['count'] == 0) {
    $stmt = $conn->prepare("INSERT INTO usuarios (username, password, nombre, rol) VALUES (?, ?, ?, ?)");
    
    // Admin: usuario "admin" / contraseña "admin123"
    $admin_pass = password_hash('admin123', PASSWORD_DEFAULT);
    $username = 'admin';
    $nombre = 'Administrador';
    $rol = 'admin';
    $stmt->bind_param("ssss", $username, $admin_pass, $nombre, $rol);
    $stmt->execute();
    
    // Mesero: usuario "mesero" / contraseña "mesero123"
    $mesero_pass = password_hash('mesero123', PASSWORD_DEFAULT);
    $username = 'mesero';
    $nombre = 'Mesero Principal';
    $rol = 'mesero';
    $stmt->bind_param("ssss", $username, $mesero_pass, $nombre, $rol);
    $stmt->execute();
    
    $stmt->close();
}

// Insertar productos de ejemplo si no existen
$check_products = $conn->query("SELECT COUNT(*) as count FROM productos");
$row = $check_products->fetch_assoc();
if ($row['count'] == 0) {
    $productos_iniciales = [
        ['Hamburguesa Clásica', 45.00, 'Hamburguesas'],
        ['Hamburguesa Doble', 65.00, 'Hamburguesas'],
        ['Hamburguesa BBQ', 70.00, 'Hamburguesas'],
        ['Hamburguesa con Queso', 55.00, 'Hamburguesas'],
        ['Hot Dog Simple', 30.00, 'Hot Dogs'],
        ['Hot Dog Especial', 40.00, 'Hot Dogs'],
        ['Hot Dog Mexicano', 45.00, 'Hot Dogs'],
        ['Coca Cola', 15.00, 'Bebidas'],
        ['Agua', 10.00, 'Bebidas'],
        ['Jugo Natural', 20.00, 'Bebidas'],
        ['Horchata', 18.00, 'Bebidas'],
        ['Agua Fresca', 20.00, 'Bebidas'],
        ['Papas Fritas', 20.00, 'Acompañamientos'],
        ['Aros de Cebolla', 25.00, 'Acompañamientos'],
        ['Nachos', 30.00, 'Acompañamientos'],
        ['Tacos al Pastor', 35.00, 'Tacos'],
        ['Tacos de Carnitas', 40.00, 'Tacos'],
        ['Quesadilla', 45.00, 'Mexicanos'],
        ['Burrito', 50.00, 'Mexicanos'],
        ['Enchiladas', 48.00, 'Mexicanos'],
        ['Flan', 25.00, 'Postres'],
        ['Churros', 20.00, 'Postres'],
    ];
    
    $stmt = $conn->prepare("INSERT INTO productos (nombre, precio, categoria) VALUES (?, ?, ?)");
    foreach ($productos_iniciales as $prod) {
        $stmt->bind_param("sds", $prod[0], $prod[1], $prod[2]);
        $stmt->execute();
    }
    $stmt->close();
}

// Insertar descuentos de ejemplo
$check_discounts = $conn->query("SELECT COUNT(*) as count FROM descuentos");
$row = $check_discounts->fetch_assoc();
if ($row['count'] == 0) {
    $conn->query("INSERT INTO descuentos (codigo, tipo, valor) VALUES 
        ('DESC10', 'porcentaje', 10),
        ('DESC20', 'porcentaje', 20),
        ('FIJO15', 'fijo', 15)");
}

// Inicializar carrito
if (!isset($_SESSION['cart'])) {
    $_SESSION['cart'] = [];
}
if (!isset($_SESSION['discount_code'])) {
    $_SESSION['discount_code'] = null;
}

// --- FUNCIONES AUXILIARES ---
function getProducts($conn) {
    $result = $conn->query("SELECT * FROM productos WHERE activo = 1 ORDER BY categoria, nombre");
    return $result->fetch_all(MYSQLI_ASSOC);
}

function getProductById($conn, $id) {
    $stmt = $conn->prepare("SELECT * FROM productos WHERE id = ?");
    $stmt->bind_param("i", $id);
    $stmt->execute();
    return $stmt->get_result()->fetch_assoc();
}

function getCartTotal($cart, $conn) {
    $total = 0;
    foreach ($cart as $itemId) {
        $product = getProductById($conn, $itemId);
        if ($product) {
            $total += $product['precio'];
        }
    }
    return $total;
}

function applyDiscount($total, $discount_code, $conn) {
    if (!$discount_code) return ['total' => $total, 'discount' => 0, 'discount_info' => null];
    
    $stmt = $conn->prepare("SELECT * FROM descuentos WHERE codigo = ? AND activo = 1");
    $stmt->bind_param("s", $discount_code);
    $stmt->execute();
    $discount = $stmt->get_result()->fetch_assoc();
    
    if (!$discount) return ['total' => $total, 'discount' => 0, 'discount_info' => null];
    
    $discount_amount = 0;
    if ($discount['tipo'] == 'porcentaje') {
        $discount_amount = $total * ($discount['valor'] / 100);
    } else {
        $discount_amount = $discount['valor'];
    }
    
    $discount_amount = min($discount_amount, $total);
    
    return [
        'total' => $total - $discount_amount,
        'discount' => $discount_amount,
        'discount_info' => $discount
    ];
}

function getGroupedCart($cart, $conn) {
    $grouped = [];
    foreach ($cart as $itemId) {
        $product = getProductById($conn, $itemId);
        if ($product) {
            $name = $product['nombre'];
            if (!isset($grouped[$name])) {
                $grouped[$name] = ['product' => $product, 'quantity' => 0];
            }
            $grouped[$name]['quantity']++;
        }
    }
    return $grouped;
}

function icon($name, $size = 20) {
    $icons = [
        'ShoppingCart' => '🛒', 'ChefHat' => '👨‍🍳', 'Settings' => '⚙️', 
        'Clock' => '🕒', 'CheckCircle' => '✅', 'AlertCircle' => '⚠️',
        'Monitor' => '💻', 'DollarSign' => '💰', 'Trash' => '🗑️',
        'Print' => '🖨️', 'Tag' => '🏷️', 'Plus' => '➕'
    ];
    return "<span style=\"font-size: {$size}px;\">{$icons[$name]}</span>";
}

// --- PROCESAMIENTO DE ACCIONES ---
$action = $_GET['action'] ?? '';
$view = $_GET['view'] ?? 'pos';

// LOGIN
if ($action === 'login' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = $_POST['username'] ?? '';
    $password = $_POST['password'] ?? '';
    
    $stmt = $conn->prepare("SELECT id, password, nombre, rol FROM usuarios WHERE username = ? AND activo = 1");
    $stmt->bind_param("s", $username);
    $stmt->execute();
    $result = $stmt->get_result();
    
    if ($user = $result->fetch_assoc()) {
        if (password_verify($password, $user['password'])) {
            $_SESSION['user_id'] = $user['id'];
            $_SESSION['user_name'] = $user['nombre'];
            $_SESSION['user_role'] = $user['rol'];
            $_SESSION['login_time'] = time();
            header("Location: ?view=pos");
            exit;
        }
    }
    
    $_SESSION['login_error'] = 'Usuario o contraseña incorrectos';
    header("Location: ?view=login");
    exit;
}

// LOGOUT
if ($action === 'logout') {
    session_destroy();
    header("Location: ?view=login");
    exit;
}

// REDIRIGIR A LOGIN SI NO ESTÁ AUTENTICADO
if (!$isLoggedIn && $view !== 'login') {
    header("Location: ?view=login");
    exit;
}

// AGREGAR AL CARRITO
if ($action === 'add' && isset($_GET['id'])) {
    $itemId = (int)$_GET['id'];
    $_SESSION['cart'][] = $itemId;
    header("Location: ?view=pos");
    exit;
}

// ELIMINAR DEL CARRITO
if ($action === 'remove' && isset($_GET['index'])) {
    $index = (int)$_GET['index'];
    if (isset($_SESSION['cart'][$index])) {
        unset($_SESSION['cart'][$index]);
        $_SESSION['cart'] = array_values($_SESSION['cart']);
    }
    header("Location: ?view=pos");
    exit;
}

// LIMPIAR CARRITO
if ($action === 'clear') {
    $_SESSION['cart'] = [];
    $_SESSION['discount_code'] = null;
    header("Location: ?view=pos");
    exit;
}

// APLICAR DESCUENTO
if ($action === 'apply_discount' && isset($_POST['discount_code'])) {
    $_SESSION['discount_code'] = strtoupper(trim($_POST['discount_code']));
    header("Location: ?view=pos");
    exit;
}

// QUITAR DESCUENTO
if ($action === 'remove_discount') {
    $_SESSION['discount_code'] = null;
    header("Location: ?view=pos");
    exit;
}

// AGREGAR PRODUCTO
if ($action === 'add_product' && $_SERVER['REQUEST_METHOD'] === 'POST' && $userRole === 'admin') {
    $nombre = trim($_POST['nombre'] ?? '');
    $precio = floatval($_POST['precio'] ?? 0);
    $categoria = trim($_POST['categoria'] ?? '');

    if (!empty($nombre) && $precio > 0 && !empty($categoria)) {
        $stmt = $conn->prepare("INSERT INTO productos (nombre, precio, categoria) VALUES (?, ?, ?)");
        $stmt->bind_param("sds", $nombre, $precio, $categoria);
        $stmt->execute();
        $stmt->close();
    }
    header("Location: ?view=admin");
    exit;
}

// EDITAR PRODUCTO
if ($action === 'edit_product' && $_SERVER['REQUEST_METHOD'] === 'POST' && $userRole === 'admin') {
    $id = intval($_POST['id'] ?? 0);
    $nombre = trim($_POST['nombre'] ?? '');
    $precio = floatval($_POST['precio'] ?? 0);
    $categoria = trim($_POST['categoria'] ?? '');

    if ($id > 0 && !empty($nombre) && $precio > 0 && !empty($categoria)) {
        $stmt = $conn->prepare("UPDATE productos SET nombre = ?, precio = ?, categoria = ? WHERE id = ?");
        $stmt->bind_param("sdsi", $nombre, $precio, $categoria, $id);
        $stmt->execute();
        $stmt->close();
    }
    header("Location: ?view=admin");
    exit;
}

// ELIMINAR PRODUCTO
if ($action === 'delete_product' && isset($_GET['id']) && $userRole === 'admin') {
    $id = intval($_GET['id']);
    $stmt = $conn->prepare("UPDATE productos SET activo = 0 WHERE id = ?");
    $stmt->bind_param("i", $id);
    $stmt->execute();
    $stmt->close();
    header("Location: ?view=admin");
    exit;
}

// CONFIRMAR PEDIDO
if ($action === 'confirm' && !empty($_SESSION['cart'])) {
    $subtotal = getCartTotal($_SESSION['cart'], $conn);
    $discount_info = applyDiscount($subtotal, $_SESSION['discount_code'], $conn);
    
    // Crear pedido
    $numero_pedido = 'P' . date('Ymd') . '-' . str_pad(rand(1, 9999), 4, '0', STR_PAD_LEFT);
    $stmt = $conn->prepare("INSERT INTO pedidos (numero_pedido, total, descuento, total_final) VALUES (?, ?, ?, ?)");
    $stmt->bind_param("sddd", $numero_pedido, $subtotal, $discount_info['discount'], $discount_info['total']);
    $stmt->execute();
    $pedido_id = $conn->insert_id;
    
    // Guardar items
    $grouped = getGroupedCart($_SESSION['cart'], $conn);
    $stmt = $conn->prepare("INSERT INTO pedido_items (pedido_id, producto_id, producto_nombre, precio, cantidad) VALUES (?, ?, ?, ?, ?)");
    foreach ($grouped as $data) {
        $product = $data['product'];
        $stmt->bind_param("iisdi", $pedido_id, $product['id'], $product['nombre'], $product['precio'], $data['quantity']);
        $stmt->execute();
    }
    
    $_SESSION['cart'] = [];
    $_SESSION['discount_code'] = null;
    $_SESSION['last_order_id'] = $pedido_id;
    header("Location: ?view=pos&success=1");
    exit;
}

// CAMBIAR ESTADO DE PEDIDO
if ($action === 'status' && isset($_GET['order_id'], $_GET['new_status'])) {
    $orderId = (int)$_GET['order_id'];
    $newStatus = $_GET['new_status'];
    
    // Si cambia a "ready", calcular tiempo de preparación
    if ($newStatus === 'ready') {
        $order = $conn->query("SELECT fecha_hora FROM pedidos WHERE id = $orderId")->fetch_assoc();
        $tiempo = time() - strtotime($order['fecha_hora']);
        $conn->query("UPDATE pedidos SET estado = '$newStatus', tiempo_preparacion = $tiempo WHERE id = $orderId");
    } else {
        $conn->query("UPDATE pedidos SET estado = '$newStatus' WHERE id = $orderId");
    }
    
    header("Location: ?view=kitchen");
    exit;
}

// AGREGAR PRODUCTO (ADMIN)
if ($action === 'add_product' && $_SERVER['REQUEST_METHOD'] === 'POST' && $userRole === 'admin') {
    $nombre = trim($_POST['nombre']);
    $precio = (float)$_POST['precio'];
    $categoria = trim($_POST['categoria']);
    
    if (!empty($nombre) && $precio > 0 && !empty($categoria)) {
        $stmt = $conn->prepare("INSERT INTO productos (nombre, precio, categoria) VALUES (?, ?, ?)");
        $stmt->bind_param("sds", $nombre, $precio, $categoria);
        if ($stmt->execute()) {
            $_SESSION['admin_success'] = 'Producto agregado exitosamente';
        } else {
            $_SESSION['admin_error'] = 'Error al agregar producto';
        }
        $stmt->close();
    } else {
        $_SESSION['admin_error'] = 'Todos los campos son obligatorios';
    }
    
    header("Location: ?view=admin");
    exit;
}

// EDITAR PRODUCTO (ADMIN)
if ($action === 'edit_product' && $_SERVER['REQUEST_METHOD'] === 'POST' && $userRole === 'admin') {
    $id = (int)$_POST['id'];
    $nombre = trim($_POST['nombre']);
    $precio = (float)$_POST['precio'];
    $categoria = trim($_POST['categoria']);
    
    if ($id > 0 && !empty($nombre) && $precio > 0 && !empty($categoria)) {
        $stmt = $conn->prepare("UPDATE productos SET nombre = ?, precio = ?, categoria = ? WHERE id = ?");
        $stmt->bind_param("sdsi", $nombre, $precio, $categoria, $id);
        if ($stmt->execute()) {
            $_SESSION['admin_success'] = 'Producto actualizado exitosamente';
        } else {
            $_SESSION['admin_error'] = 'Error al actualizar producto';
        }
        $stmt->close();
    }
    
    header("Location: ?view=admin");
    exit;
}

// ELIMINAR PRODUCTO (ADMIN)
if ($action === 'delete_product' && isset($_GET['id']) && $userRole === 'admin') {
    $id = (int)$_GET['id'];

    // Desactivar en lugar de eliminar para mantener historial
    $stmt = $conn->prepare("UPDATE productos SET activo = 0 WHERE id = ?");
    $stmt->bind_param("i", $id);
    if ($stmt->execute()) {
        $_SESSION['admin_success'] = 'Producto eliminado exitosamente';
    } else {
        $_SESSION['admin_error'] = 'Error al eliminar producto';
    }
    $stmt->close();

    header("Location: ?view=admin");
    exit;
}

// AGREGAR USUARIO
if ($action === 'add_user' && $_SERVER['REQUEST_METHOD'] === 'POST' && $userRole === 'admin') {
    $username = trim($_POST['username'] ?? '');
    $password = trim($_POST['password'] ?? '');
    $nombre = trim($_POST['nombre'] ?? '');
    $rol = $_POST['rol'] ?? '';

    if (!empty($username) && !empty($password) && !empty($nombre) && !empty($rol)) {
        $stmt = $conn->prepare("INSERT INTO usuarios (username, password, nombre, rol) VALUES (?, ?, ?, ?)");
        $hashed_password = password_hash($password, PASSWORD_DEFAULT);
        $stmt->bind_param("ssss", $username, $hashed_password, $nombre, $rol);
        if ($stmt->execute()) {
            $_SESSION['admin_success'] = 'Usuario agregado exitosamente';
        } else {
            $_SESSION['admin_error'] = 'Error al agregar usuario';
        }
        $stmt->close();
    } else {
        $_SESSION['admin_error'] = 'Todos los campos son obligatorios';
    }

    header("Location: ?view=admin");
    exit;
}

// EDITAR USUARIO
if ($action === 'edit_user' && $_SERVER['REQUEST_METHOD'] === 'POST' && $userRole === 'admin') {
    $id = (int)$_POST['id'];
    $username = trim($_POST['username'] ?? '');
    $password = trim($_POST['password'] ?? '');
    $nombre = trim($_POST['nombre'] ?? '');
    $rol = $_POST['rol'] ?? '';

    if ($id > 0 && !empty($username) && !empty($nombre) && !empty($rol)) {
        if (!empty($password)) {
            $stmt = $conn->prepare("UPDATE usuarios SET username = ?, password = ?, nombre = ?, rol = ? WHERE id = ?");
            $hashed_password = password_hash($password, PASSWORD_DEFAULT);
            $stmt->bind_param("ssssi", $username, $hashed_password, $nombre, $rol, $id);
        } else {
            $stmt = $conn->prepare("UPDATE usuarios SET username = ?, nombre = ?, rol = ? WHERE id = ?");
            $stmt->bind_param("sssi", $username, $nombre, $rol, $id);
        }
        if ($stmt->execute()) {
            $_SESSION['admin_success'] = 'Usuario actualizado exitosamente';
        } else {
            $_SESSION['admin_error'] = 'Error al actualizar usuario';
        }
        $stmt->close();
    }

    header("Location: ?view=admin");
    exit;
}

// ELIMINAR USUARIO
if ($action === 'delete_user' && isset($_GET['id']) && $userRole === 'admin') {
    $id = (int)$_GET['id'];

    $stmt = $conn->prepare("UPDATE usuarios SET activo = 0 WHERE id = ?");
    $stmt->bind_param("i", $id);
    if ($stmt->execute()) {
        $_SESSION['admin_success'] = 'Usuario eliminado exitosamente';
    } else {
        $_SESSION['admin_error'] = 'Error al eliminar usuario';
    }
    $stmt->close();

    header("Location: ?view=admin");
    exit;
}





// IMPRIMIR TICKET
if ($action === 'print' && isset($_GET['order_id'])) {
    $orderId = (int)$_GET['order_id'];
    
    $order = $conn->query("SELECT * FROM pedidos WHERE id = $orderId")->fetch_assoc();
    $items = $conn->query("SELECT * FROM pedido_items WHERE pedido_id = $orderId")->fetch_all(MYSQLI_ASSOC);
    
    ?>
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Ticket - <?= htmlspecialchars($order['numero_pedido']) ?></title>
        <style>
            @media print {
                body { margin: 0; }
                .no-print { display: none; }
            }
            body { font-family: 'Courier New', monospace; width: 300px; margin: 20px auto; }
            .ticket { border: 2px dashed #000; padding: 10px; }
            .header { text-align: center; border-bottom: 1px dashed #000; padding-bottom: 10px; margin-bottom: 10px; }
            .item { display: flex; justify-content: space-between; margin: 5px 0; }
            .total { border-top: 1px dashed #000; margin-top: 10px; padding-top: 10px; font-weight: bold; }
            .footer { text-align: center; margin-top: 10px; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="ticket">
            <div class="header">
                <h2>🌮RESTAURANTE SAZON MEXICANO 🌮</h2>
                <p>Sistema de Pedidos</p>
                <p><strong>Ticket: <?= htmlspecialchars($order['numero_pedido']) ?></strong></p>
                <p><?= date('d/m/Y H:i', strtotime($order['fecha_hora'])) ?></p>
            </div>
            
            <div class="items">
                <?php foreach ($items as $item): ?>
                    <div class="item">
                        <span><?= htmlspecialchars($item['producto_nombre']) ?> x<?= $item['cantidad'] ?></span>
                        <span>Q<?= number_format($item['precio'] * $item['cantidad'], 2) ?></span>
                    </div>
                <?php endforeach; ?>
            </div>
            
            <div class="total">
                <div class="item">
                    <span>Subtotal:</span>
                    <span>Q<?= number_format($order['total'], 2) ?></span>
                </div>
                <?php if ($order['descuento'] > 0): ?>
                    <div class="item" style="color: green;">
                        <span>Descuento:</span>
                        <span>-Q<?= number_format($order['descuento'], 2) ?></span>
                    </div>
                <?php endif; ?>
                <div class="item" style="font-size: 18px;">
                    <span>TOTAL:</span>
                    <span>Q<?= number_format($order['total_final'], 2) ?></span>
                </div>
            </div>
            
            <div class="footer">
                <p>¡Gracias por su compra!</p>
                <p>Estado: <?= strtoupper($order['estado']) ?></p>
            </div>
        </div>
        
        <div class="no-print" style="text-align: center; margin-top: 20px;">
            <button onclick="window.print()" style="padding: 10px 20px; font-size: 16px; cursor: pointer;">🖨️ Imprimir</button>
            <button onclick="window.close()" style="padding: 10px 20px; font-size: 16px; cursor: pointer; margin-left: 10px;">✕ Cerrar</button>
        </div>
    </body>
    </html>
    <?php
    exit;
}

// ====================================================================
// login
// ====================================================================

function renderLoginView() {
    $error = $_SESSION['login_error'] ?? null;
    unset($_SESSION['login_error']);
    ?>
    <div style="display: flex; justify-content: center; align-items: center; min-height: 100vh; background: linear-gradient(135deg, #047857 0%, #059669 100%);">
        <div style="background-color: white; border-radius: 1rem; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04); padding: 3rem; width: 100%; max-width: 400px;">
            <div style="text-align: center; margin-bottom: 2rem;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">🌮🌮</div>
                <h1 style="font-size: 1.875rem; font-weight: bold; color: #1f2937; margin-bottom: 0.5rem;">Sistema de Pedidos</h1>
                <p style="color: #6b7280;">Inicia sesión para continuar</p>
            </div>

            <?php if ($error): ?>
                <div style="background-color: #fee2e2; border: 1px solid #ef4444; color: #991b1b; padding: 0.75rem; border-radius: 0.5rem; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.5rem;">
                    <span style="font-size: 1.25rem;">⚠️</span>
                    <span style="font-size: 0.875rem;"><?= htmlspecialchars($error) ?></span>
                </div>
            <?php endif; ?>

            <form method="POST" action="?action=login" style="margin-bottom: 1.5rem;">
                <div style="margin-bottom: 1.5rem;">
                    <label style="display: block; color: #374151; font-weight: 600; margin-bottom: 0.5rem; font-size: 0.875rem;">
                        Usuario
                    </label>
                    <input type="text" name="username" required autofocus
                           style="width: 100%; padding: 0.75rem; border: 1px solid #d1d5db; border-radius: 0.5rem; font-size: 1rem; transition: all 0.2s;"
                           onfocus="this.style.borderColor='#10b981'; this.style.outline='none'; this.style.boxShadow='0 0 0 3px rgba(16, 185, 129, 0.1)';"
                           onblur="this.style.borderColor='#d1d5db'; this.style.boxShadow='none';">
                </div>

                <div style="margin-bottom: 1.5rem;">
                    <label style="display: block; color: #374151; font-weight: 600; margin-bottom: 0.5rem; font-size: 0.875rem;">
                        Contraseña
                    </label>
                    <input type="password" name="password" required
                           style="width: 100%; padding: 0.75rem; border: 1px solid #d1d5db; border-radius: 0.5rem; font-size: 1rem; transition: all 0.2s;"
                           onfocus="this.style.borderColor='#10b981'; this.style.outline='none'; this.style.boxShadow='0 0 0 3px rgba(16, 185, 129, 0.1)';"
                           onblur="this.style.borderColor='#d1d5db'; this.style.boxShadow='none';">
                </div>

                <button type="submit" 
                        style="width: 100%; background-color: #10b981; color: white; padding: 0.875rem; border: none; border-radius: 0.5rem; font-weight: 600; font-size: 1rem; cursor: pointer; transition: all 0.2s;"
                        onmouseover="this.style.backgroundColor='#059669'"
                        onmouseout="this.style.backgroundColor='#10b981'">
                    Iniciar Sesión
                </button>
            </form>

            <div style="background-color: #f9fafb; border-radius: 0.5rem; padding: 1rem; margin-top: 1.5rem;">
                <p style="color: #6b7280; font-size: 0.875rem; font-weight: 600; margin-bottom: 0.75rem; text-align: center;">Usuarios:</p>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
                    <div style="background-color: white; padding: 0.75rem; border-radius: 0.375rem; border: 1px solid #e5e7eb;">
                        <div style="font-weight: 600; color: #059669; font-size: 0.875rem; margin-bottom: 0.25rem;">👨‍💼 Administrador</div>
                        
                    </div>
                    <div style="background-color: white; padding: 0.75rem; border-radius: 0.375rem; border: 1px solid #e5e7eb;">
                        <div style="font-weight: 600; color: #3b82f6; font-size: 0.875rem; margin-bottom: 0.25rem;">👨‍🍳 Mesero</div>
                        
                    </div>
                </div>
            </div>
        </div>
    </div>
    <?php
}
// ====================================================================
// FUNCIONES DE RENDERIZADO
// ====================================================================

function renderPOSView($conn) {
    $products = getProducts($conn);
    $cart = $_SESSION['cart'];
    $subtotal = getCartTotal($cart, $conn);
    $discount_info = applyDiscount($subtotal, $_SESSION['discount_code'], $conn);
    $showSuccess = isset($_GET['success']);
    ?>
    <div style="display: flex; width: 100%; height: 100%;">
        <!-- MENÚ -->
        <div style="flex: 1; padding: 1.5rem; background-color: #f9fafb; overflow-y: auto;">
            <h2 style="font-size: 1.5rem; font-weight: bold; margin-bottom: 1.5rem; color: #1f2937;">Menú</h2>

            <?php if ($showSuccess):
                $last_order_id = $_SESSION['last_order_id'] ?? null;
            ?>
                <div style="background-color: #d1fae5; border: 1px solid #10b981; color: #065f46; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center;">
                    <span>✅ <strong>Pedido confirmado exitosamente</strong></span>
                    <?php if ($last_order_id): ?>
                        <a href="?action=print&order_id=<?= $last_order_id ?>" target="_blank" style="background-color: #059669; color: white; padding: 0.5rem 1rem; border-radius: 0.375rem; text-decoration: none; font-weight: 600;">
                            <?= icon('Print', 16) ?> Imprimir Ticket
                        </a>
                    <?php endif; ?>
                </div>
            <?php endif; ?>

            <?php
            $categories = array_unique(array_column($products, 'categoria'));
            foreach ($categories as $category):
                $categoryItems = array_filter($products, fn($p) => $p['categoria'] === $category);
            ?>
                <div style="margin-bottom: 1.5rem;">
                    <h3 style="font-size: 1.125rem; font-weight: 600; color: #4b5563; margin-bottom: 0.75rem; border-bottom: 2px solid #10b981; padding-bottom: 0.5rem;">
                        <?= htmlspecialchars($category) ?>
                    </h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 0.75rem;">
                        <?php foreach ($categoryItems as $item): ?>
                            <a href="?view=pos&action=add&id=<?= $item['id'] ?>"
                               style="text-decoration: none; background-color: white; padding: 1rem; border: 1px solid #e5e7eb; border-radius: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); transition: all 0.2s; display: block;"
                               onmouseover="this.style.boxShadow='0 4px 6px rgba(0,0,0,0.1)'; this.style.backgroundColor='#f0fdf4';"
                               onmouseout="this.style.boxShadow='0 1px 3px rgba(0,0,0,0.05)'; this.style.backgroundColor='white';">
                                <div style="font-weight: 600; color: #1f2937; font-size: 0.9rem;"><?= htmlspecialchars($item['nombre']) ?></div>
                                <div style="color: #059669; font-weight: bold; margin-top: 0.5rem; font-size: 1.1rem;">Q<?= number_format($item['precio'], 2) ?></div>
                            </a>
                        <?php endforeach; ?>
                    </div>
                </div>
            <?php endforeach; ?>
        </div>

        <!-- CARRITO -->
        <div style="width: 400px; background-color: white; border-left: 1px solid #e5e7eb; padding: 1.5rem; display: flex; flex-direction: column;">
            <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
                <?= icon('ShoppingCart', 24) ?>
                <h2 style="font-size: 1.25rem; font-weight: bold; color: #1f2937; margin: 0 0 0 0.5rem;">Pedido Actual</h2>
            </div>

            <div style="flex: 1; overflow-y: auto; margin-bottom: 1rem;">
                <?php if (empty($cart)): ?>
                    <div style="text-align: center; color: #9ca3af; margin-top: 3rem;">
                        <div style="font-size: 48px; opacity: 0.3;">🛒</div>
                        <p>Sin productos</p>
                    </div>
                <?php else: 
                    $index = 0;
                    foreach ($cart as $itemId):
                        $product = getProductById($conn, $itemId);
                        if (!$product) continue;
                ?>
                        <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem; background-color: #f9fafb; border-radius: 0.5rem; margin-bottom: 0.5rem;">
                            <div style="flex: 1;">
                                <div style="font-weight: 600; color: #1f2937; font-size: 0.875rem;"><?= htmlspecialchars($product['nombre']) ?></div>
                                <div style="color: #6b7280; font-size: 0.875rem;">Q<?= number_format($product['precio'], 2) ?></div>
                            </div>
                            <a href="?view=pos&action=remove&index=<?= $index ?>" 
                               style="color: #ef4444; text-decoration: none; font-weight: bold; padding: 0.25rem 0.5rem;">
                                ✕
                            </a>
                        </div>
                <?php 
                        $index++;
                    endforeach; 
                endif; ?>
            </div>

            <!-- DESCUENTO -->
            <div style="background-color: #fef3c7; border-radius: 0.5rem; padding: 1rem; margin-bottom: 1rem;">
                <?php if ($_SESSION['discount_code']): 
                    $discount_info_check = applyDiscount($subtotal, $_SESSION['discount_code'], $conn);
                    if ($discount_info_check['discount_info']):
                ?>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-weight: 600; color: #92400e;">
                                <?= icon('Tag', 16) ?> Código: <?= htmlspecialchars($_SESSION['discount_code']) ?>
                            </div>
                            <div style="color: #78350f; font-size: 0.875rem;">
                                -Q<?= number_format($discount_info_check['discount'], 2) ?>
                            </div>
                        </div>
                        <a href="?view=pos&action=remove_discount" style="color: #dc2626; text-decoration: none; font-weight: bold;">✕</a>
                    </div>
                <?php else: ?>
                    <div style="color: #dc2626; font-size: 0.875rem;">⚠️ Código inválido</div>
                    <a href="?view=pos&action=remove_discount" style="color: #2563eb; text-decoration: none; font-size: 0.875rem;">Remover</a>
                <?php endif; else: ?>
                    <form method="POST" action="?view=pos&action=apply_discount" style="display: flex; gap: 0.5rem;">
                        <input type="text" name="discount_code" placeholder="Código de descuento" 
                               style="flex: 1; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.375rem; font-size: 0.875rem;">
                        <button type="submit" style="background-color: #f59e0b; color: white; padding: 0.5rem 1rem; border: none; border-radius: 0.375rem; font-weight: 600; cursor: pointer;">
                            Aplicar
                        </button>
                    </form>
                    <div style="font-size: 0.75rem; color: #78350f; margin-top: 0.5rem;">
                        Códigos: DESC10, DESC20, FIJO15
                    </div>
                <?php endif; ?>
            </div>

            <!-- TOTAL -->
            <div style="border-top: 1px solid #e5e7eb; padding-top: 1rem;">
                <?php if ($discount_info['discount'] > 0): ?>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem; color: #6b7280;">
                        <span>Subtotal:</span>
                        <span>Q<?= number_format($subtotal, 2) ?></span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem; color: #059669;">
                        <span>Descuento:</span>
                        <span>-Q<?= number_format($discount_info['discount'], 2) ?></span>
                    </div>
                <?php endif; ?>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <span style="font-size: 1.125rem; font-weight: 600; color: #4b5563;">Total:</span>
                    <span style="font-size: 1.875rem; font-weight: bold; color: #10b981;">Q<?= number_format($discount_info['total'], 2) ?></span>
                </div>
                
                <a href="?view=pos&action=confirm" 
                   style="display: block; width: 100%; background-color: <?= empty($cart) ? '#d1d5db' : '#10b981' ?>; color: white; padding: 0.75rem; border-radius: 0.5rem; font-weight: 600; text-align: center; text-decoration: none; margin-bottom: 0.5rem; <?= empty($cart) ? 'pointer-events: none;' : '' ?>">
                    Confirmar Pedido
                </a>
                
                <a href="?view=pos&action=clear" 
                   style="display: block; width: 100%; background-color: #f3f4f6; color: #4b5563; padding: 0.5rem; border-radius: 0.5rem; font-weight: 600; text-align: center; text-decoration: none;">
                    Limpiar
                </a>
            </div>
        </div>
    </div>
    <?php
}

function renderKitchenView($conn) {
    $orders = $conn->query("SELECT * FROM pedidos WHERE estado != 'delivered' ORDER BY fecha_hora ASC")->fetch_all(MYSQLI_ASSOC);
    ?>
    <div style="padding: 1.5rem; background-color: #f9fafb; height: 100%; overflow-y: auto;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
            <h2 style="font-size: 1.5rem; font-weight: bold; color: #1f2937;"><?= icon('ChefHat', 28) ?> Pantalla de Cocina</h2>
            <div style="background-color: white; padding: 0.5rem 1rem; border-radius: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <strong><?= count($orders) ?></strong> pedidos activos
            </div>
        </div>

        <?php if (empty($orders)): ?>
            <div style="text-align: center; color: #9ca3af; margin-top: 3rem;">
                <div style="font-size: 64px; opacity: 0.3;">👨‍🍳</div>
                <p style="font-size: 1.25rem;">No hay pedidos pendientes</p>
            </div>
        <?php else: ?>
            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1rem;">
                <?php foreach ($orders as $order): 
                    $items = $conn->query("SELECT * FROM pedido_items WHERE pedido_id = {$order['id']}")->fetch_all(MYSQLI_ASSOC);
                    
                    $statusConfig = [
                        'pending' => ['color' => '#f59e0b', 'bg' => '#fffbeb', 'icon' => icon('AlertCircle', 24), 'btn' => 'Iniciar', 'next' => 'preparing', 'btn_color' => '#3b82f6'],
                        'preparing' => ['color' => '#3b82f6', 'bg' => '#eff6ff', 'icon' => icon('Monitor', 24), 'btn' => 'Listo', 'next' => 'ready', 'btn_color' => '#10b981'],
                        'ready' => ['color' => '#10b981', 'bg' => '#ecfdf5', 'icon' => icon('CheckCircle', 24), 'btn' => 'Entregar', 'next' => 'delivered', 'btn_color' => '#6b7280'],
                    ][$order['estado']];
                ?>
                    <div style="background-color: <?= $statusConfig['bg'] ?>; border-left: 4px solid <?= $statusConfig['color'] ?>; border-radius: 0.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); padding: 1.25rem;">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                            <div>
                                <div style="font-size: 1.5rem; font-weight: bold; color: #1f2937;"><?= htmlspecialchars($order['numero_pedido']) ?></div>
                                <div style="color: #6b7280; font-size: 0.875rem; margin-top: 0.25rem;">
                                    <?= icon('Clock', 14) ?> <?= date('h:i A', strtotime($order['fecha_hora'])) ?>
                                </div>
                            </div>
                            <?= $statusConfig['icon'] ?>
                        </div>

                        <div style="background-color: white; border-radius: 0.375rem; padding: 0.75rem; margin-bottom: 1rem;">
                            <?php foreach ($items as $item): ?>
                                <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #f3f4f6;">
                                    <span style="color: #374151; font-weight: 500;"><?= htmlspecialchars($item['producto_nombre']) ?></span>
                                    <span style="color: #6b7280; font-weight: bold;">x<?= $item['cantidad'] ?></span>
                                </div>
                            <?php endforeach; ?>
                            <div style="display: flex; justify-content: space-between; padding-top: 0.5rem; margin-top: 0.5rem; border-top: 2px solid #e5e7eb;">
                                <span style="font-weight: 600;">Total:</span>
                                <span style="font-weight: bold; color: #10b981;">Q<?= number_format($order['total_final'], 2) ?></span>
                            </div>
                        </div>

                        <div style="display: flex; gap: 0.5rem;">
                            <a href="?view=kitchen&action=status&order_id=<?= $order['id'] ?>&new_status=<?= $statusConfig['next'] ?>" 
                               style="flex: 1; display: block; background-color: <?= $statusConfig['btn_color'] ?>; color: white; padding: 0.75rem; border-radius: 0.5rem; font-weight: 600; text-align: center; text-decoration: none;">
                                <?= $statusConfig['btn'] ?>
                            </a>
                            <a href="?action=print&order_id=<?= $order['id'] ?>" target="_blank"
                               style="background-color: #6b7280; color: white; padding: 0.75rem; border-radius: 0.5rem; text-decoration: none; display: flex; align-items: center; justify-content: center;">
                                <?= icon('Print', 18) ?>
                            </a>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
        <?php endif; ?>
    </div>
    <?php
}

function renderAdminView($conn) {
    global $userRole;

    // Solo permitir acceso a administradores
    if ($userRole !== 'admin') {
        header("Location: ?view=pos");
        exit;
    }

    // Estadísticas
    $stats = $conn->query("SELECT
        COUNT(*) as total_pedidos,
        SUM(total_final) as ventas_totales,
        AVG(tiempo_preparacion) as tiempo_promedio,
        SUM(CASE WHEN estado = 'preparing' THEN 1 ELSE 0 END) as en_preparacion
        FROM pedidos
        WHERE DATE(fecha_hora) = CURDATE()")->fetch_assoc();

    $recent_orders = $conn->query("SELECT * FROM pedidos ORDER BY fecha_hora DESC LIMIT 10")->fetch_all(MYSQLI_ASSOC);
    $productos = getProducts($conn);
    $usuarios = $conn->query("SELECT * FROM usuarios ORDER BY nombre")->fetch_all(MYSQLI_ASSOC);

    // Manejar formularios de productos
    $product_action = $_GET['action'] ?? '';
    $editing_product = null;

    if ($product_action === 'edit_product_form' && isset($_GET['id'])) {
        $id = intval($_GET['id']);
        $editing_product = $conn->query("SELECT * FROM productos WHERE id = $id AND activo = 1")->fetch_assoc();
    }

    // Manejar formularios de usuarios
    $user_action = $_GET['action'] ?? '';
    $editing_user = null;

    if ($user_action === 'edit_user_form' && isset($_GET['id'])) {
        $id = intval($_GET['id']);
        $editing_user = $conn->query("SELECT * FROM usuarios WHERE id = $id")->fetch_assoc();
    }

    // Mostrar formulario si se solicita agregar producto
    $show_add_form = isset($_GET['action']) && $_GET['action'] === 'add_product_form';
    $show_add_user_form = isset($_GET['action']) && $_GET['action'] === 'add_user_form';
    ?>

<!-- GESTIÓN DE PRODUCTOS -->
        <div style="background-color: white; border-radius: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 1.5rem; margin-bottom: 1.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                <h3 style="font-size: 1.25rem; font-weight: 600; color: #1f2937;">
                    <?= $editing_product ? '✏️ Editar Producto' : '➕ Agregar Nuevo Producto' ?>
                </h3>
                <?php if ($editing_product): ?>
                    <a href="?view=admin" style="color: #6b7280; text-decoration: none; font-size: 0.875rem;">✕ Cancelar</a>
                <?php endif; ?>
            </div>

            <form method="POST" action="?action=<?= $editing_product ? 'edit_product' : 'add_product' ?>" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; align-items: end;">
                <?php if ($editing_product): ?>
                    <input type="hidden" name="id" value="<?= $editing_product['id'] ?>">
                <?php endif; ?>

                <div>
                    <label style="display: block; color: #374151; font-weight: 600; margin-bottom: 0.5rem; font-size: 0.875rem;">
                        Nombre del Producto *
                    </label>
                    <input type="text" name="nombre" required
                           value="<?= $editing_product ? htmlspecialchars($editing_product['nombre']) : '' ?>"
                           placeholder="Ej: Hamburguesa Especial"
                           style="width: 100%; padding: 0.75rem; border: 1px solid #d1d5db; border-radius: 0.5rem; font-size: 0.875rem;">
                </div>

                <div>
                    <label style="display: block; color: #374151; font-weight: 600; margin-bottom: 0.5rem; font-size: 0.875rem;">
                        Precio (Q) *
                    </label>
                    <input type="number" name="precio" required step="0.01" min="0.01"
                           value="<?= $editing_product ? $editing_product['precio'] : '' ?>"
                           placeholder="0.00"
                           style="width: 100%; padding: 0.75rem; border: 1px solid #d1d5db; border-radius: 0.5rem; font-size: 0.875rem;">
                </div>

                <div>
                    <label style="display: block; color: #374151; font-weight: 600; margin-bottom: 0.5rem; font-size: 0.875rem;">
                        Categoría *
                    </label>
                    <select name="categoria" required
                            style="width: 100%; padding: 0.75rem; border: 1px solid #d1d5db; border-radius: 0.5rem; font-size: 0.875rem; background-color: white;">
                        <option value="">Seleccionar...</option>
                        <option value="Hamburguesas" <?= $editing_product && $editing_product['categoria'] === 'Hamburguesas' ? 'selected' : '' ?>>🍔 Hamburguesas</option>
                        <option value="Hot Dogs" <?= $editing_product && $editing_product['categoria'] === 'Hot Dogs' ? 'selected' : '' ?>>🌭 Hot Dogs</option>
                        <option value="Bebidas" <?= $editing_product && $editing_product['categoria'] === 'Bebidas' ? 'selected' : '' ?>>🥤 Bebidas</option>
                        <option value="Acompañamientos" <?= $editing_product && $editing_product['categoria'] === 'Acompañamientos' ? 'selected' : '' ?>>🍟 Acompañamientos</option>
                        <option value="Postres" <?= $editing_product && $editing_product['categoria'] === 'Postres' ? 'selected' : '' ?>>🍰 Postres</option>
                        <option value="Ensaladas" <?= $editing_product && $editing_product['categoria'] === 'Ensaladas' ? 'selected' : '' ?>>🥗 Ensaladas</option>
                    </select>
                </div>

                <button type="submit"
                        style="padding: 0.75rem 1.5rem; background-color: <?= $editing_product ? '#f59e0b' : '#10b981' ?>; color: white; border: none; border-radius: 0.5rem; font-weight: 600; cursor: pointer; font-size: 0.875rem;">
                    <?= $editing_product ? '💾 Actualizar' : '➕ Agregar' ?>
                </button>
            </form>
        </div>

    
        <!-- ESTADÍSTICAS -->
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1.5rem;">
            <div style="text-align: center; padding: 1.5rem; background-color: #ecfdf5; border-radius: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <?= icon('DollarSign', 32) ?>
                <div style="font-size: 1.875rem; font-weight: bold; color: #1f2937; margin-top: 0.5rem;">
                    Q<?= number_format($stats['ventas_totales'] ?? 0, 2) ?>
                </div>
                <div style="font-size: 0.875rem; color: #6b7280; margin-top: 0.25rem;">Ventas del Día</div>
            </div>
            <div style="text-align: center; padding: 1.5rem; background-color: #eff6ff; border-radius: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <?= icon('ShoppingCart', 32) ?>
                <div style="font-size: 1.875rem; font-weight: bold; color: #1f2937; margin-top: 0.5rem;">
                    <?= $stats['total_pedidos'] ?? 0 ?>
                </div>
                <div style="font-size: 0.875rem; color: #6b7280; margin-top: 0.25rem;">Pedidos del Día</div>
            </div>
            <div style="text-align: center; padding: 1.5rem; background-color: #fef3c7; border-radius: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <?= icon('Clock', 32) ?>
                <div style="font-size: 1.875rem; font-weight: bold; color: #1f2937; margin-top: 0.5rem;">
                    <?= $stats['tiempo_promedio'] ? round($stats['tiempo_promedio'] / 60) : 0 ?> min
                </div>
                <div style="font-size: 0.875rem; color: #6b7280; margin-top: 0.25rem;">Tiempo Promedio</div>
            </div>
            <div style="text-align: center; padding: 1.5rem; background-color: #f3e8ff; border-radius: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <?= icon('ChefHat', 32) ?>
                <div style="font-size: 1.875rem; font-weight: bold; color: #1f2937; margin-top: 0.5rem;">
                    <?= $stats['en_preparacion'] ?? 0 ?>
                </div>
                <div style="font-size: 0.875rem; color: #6b7280; margin-top: 0.25rem;">En Preparación</div>
            </div>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 1.5rem;">
            <!-- PRODUCTOS -->
            <div style="background-color: white; border-radius: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 1.5rem;">
                <h3 style="font-size: 1.125rem; font-weight: 600; margin-bottom: 1rem; color: #1f2937;">Productos (<?= count($productos) ?>)</h3>
                <div style="max-height: 400px; overflow-y: auto;">
                    <?php 
                    $categorias = [];
                    foreach ($productos as $prod) {
                        $categorias[$prod['categoria']][] = $prod;
                    }
                    
                    foreach ($categorias as $cat => $items): 
                    ?>
                        <div style="margin-bottom: 1rem;">
                            <div style="font-weight: 600; color: #059669; font-size: 0.875rem; padding: 0.5rem; background-color: #ecfdf5; border-radius: 0.375rem; margin-bottom: 0.5rem;">
                                <?= htmlspecialchars($cat) ?>
                            </div>
                            <?php foreach ($items as $prod): ?>
                                <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem; border-bottom: 1px solid #f3f4f6;">
                                    <div style="flex: 1;">
                                        <div style="font-weight: 600; color: #1f2937; font-size: 0.875rem;"><?= htmlspecialchars($prod['nombre']) ?></div>
                                        <div style="color: #10b981; font-weight: bold; font-size: 0.875rem;">Q<?= number_format($prod['precio'], 2) ?></div>
                                    </div>
                                    <div style="display: flex; gap: 0.5rem;">
                                        <a href="?view=admin&action=edit_product_form&id=<?= $prod['id'] ?>"
                                           style="padding: 0.375rem 0.75rem; background-color: #3b82f6; color: white; border-radius: 0.375rem; text-decoration: none; font-size: 0.75rem; font-weight: 600;">
                                            ✏️
                                        </a>
                                        <a href="?view=admin&action=delete_product&id=<?= $prod['id'] ?>" 
                                           onclick="return confirm('¿Eliminar este producto?')"
                                           style="padding: 0.375rem 0.75rem; background-color: #ef4444; color: white; border-radius: 0.375rem; text-decoration: none; font-size: 0.75rem; font-weight: 600;">
                                            🗑️
                                        </a>
                                    </div>
                                </div>
                            <?php endforeach; ?>
                        </div>
                    <?php endforeach; ?>
                </div>
            </div>
            <!-- PEDIDOS RECIENTES -->
            <div style="background-color: white; border-radius: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 1.5rem;">
                <h3 style="font-size: 1.125rem; font-weight: 600; margin-bottom: 1rem; color: #1f2937;">Pedidos Recientes</h3>
                <div style="max-height: 300px; overflow-y: auto;">
                    <?php foreach ($recent_orders as $order): 
                        $status_colors = [
                            'pending' => '#f59e0b',
                            'preparing' => '#3b82f6',
                            'ready' => '#10b981',
                            'delivered' => '#6b7280'
                        ];
                    ?>
                        <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem; border-bottom: 1px solid #f3f4f6;">
                            <div style="flex: 1;">
                                <div style="font-weight: 600; color: #1f2937; font-size: 0.875rem;"><?= htmlspecialchars($order['numero_pedido']) ?></div>
                                <div style="color: #6b7280; font-size: 0.75rem;"><?= date('d/m/Y H:i', strtotime($order['fecha_hora'])) ?></div>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-weight: bold; color: #10b981; font-size: 0.875rem;">Q<?= number_format($order['total_final'], 2) ?></div>
                                <div style="display: inline-block; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem; font-weight: 600; background-color: <?= $status_colors[$order['estado']] ?>22; color: <?= $status_colors[$order['estado']] ?>;">
                                    <?= strtoupper($order['estado']) ?>
                                </div>
                            </div>
                        </div>
                    <?php endforeach; ?>
                </div>
            </div>
        </div>
        
        <!-- GESTIÓN DE USUARIOS -->
        <div style="background-color: white; border-radius: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 1.5rem; margin-bottom: 1.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                <h3 style="font-size: 1.25rem; font-weight: 600; color: #1f2937;">
                    👥 Gestión de Usuarios
                </h3>
                <a href="?view=admin&action=add_user_form" style="background-color: #10b981; color: white; padding: 0.5rem 1rem; border-radius: 0.375rem; text-decoration: none; font-weight: 600; font-size: 0.875rem;">
                    ➕ Agregar Usuario
                </a>
            </div>

            <div style="max-height: 300px; overflow-y: auto;">
                <?php foreach ($usuarios as $user): ?>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem; border-bottom: 1px solid #f3f4f6;">
                        <div style="flex: 1;">
                            <div style="font-weight: 600; color: #1f2937; font-size: 0.875rem;"><?= htmlspecialchars($user['nombre']) ?></div>
                            <div style="color: #6b7280; font-size: 0.75rem;">@<?= htmlspecialchars($user['username']) ?> • <?= $user['rol'] === 'admin' ? '👨‍💼 Administrador' : '👨‍🍳 Mesero' ?> • <?= $user['activo'] ? '✅ Activo' : '❌ Inactivo' ?></div>
                        </div>
                        <div style="display: flex; gap: 0.5rem;">
                            <a href="?view=admin&action=edit_user_form&id=<?= $user['id'] ?>"
                               style="padding: 0.375rem 0.75rem; background-color: #3b82f6; color: white; border-radius: 0.375rem; text-decoration: none; font-size: 0.75rem; font-weight: 600;">
                                ✏️
                            </a>
                            <a href="?view=admin&action=delete_user&id=<?= $user['id'] ?>"
                               onclick="return confirm('¿Eliminar este usuario?')"
                               style="padding: 0.375rem 0.75rem; background-color: #ef4444; color: white; border-radius: 0.375rem; text-decoration: none; font-size: 0.75rem; font-weight: 600;">
                                🗑️
                            </a>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
        </div>

        <!-- FORMULARIO DE USUARIO -->
        <?php if ($show_add_user_form || $user_action === 'edit_user_form'): ?>
            <div style="background-color: white; border-radius: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 1.5rem; margin-bottom: 1.5rem;">
                <h3 style="font-size: 1.125rem; font-weight: 600; margin-bottom: 1rem; color: #1f2937;">
                    <?= $editing_user ? 'Editar Usuario' : 'Agregar Nuevo Usuario' ?>
                </h3>
                <form method="POST" action="?view=admin&action=<?= $editing_user ? 'edit_user' : 'add_user' ?>">
                    <?php if ($editing_user): ?>
                        <input type="hidden" name="id" value="<?= $editing_user['id'] ?>">
                    <?php endif; ?>
                    <div style="margin-bottom: 1rem;">
                        <label style="display: block; color: #374151; font-weight: 600; margin-bottom: 0.5rem; font-size: 0.875rem;">
                            Nombre Completo
                        </label>
                        <input type="text" name="nombre" required
                               value="<?= htmlspecialchars($editing_user['nombre'] ?? '') ?>"
                               style="width: 100%; padding: 0.75rem; border: 1px solid #d1d5db; border-radius: 0.5rem; font-size: 1rem;">
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <label style="display: block; color: #374151; font-weight: 600; margin-bottom: 0.5rem; font-size: 0.875rem;">
                            Usuario
                        </label>
                        <input type="text" name="username" required
                               value="<?= htmlspecialchars($editing_user['username'] ?? '') ?>"
                               style="width: 100%; padding: 0.75rem; border: 1px solid #d1d5db; border-radius: 0.5rem; font-size: 1rem;">
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <label style="display: block; color: #374151; font-weight: 600; margin-bottom: 0.5rem; font-size: 0.875rem;">
                            Contraseña <?= $editing_user ? '(dejar vacío para mantener)' : '*' ?>
                        </label>
                        <input type="password" name="password" <?= !$editing_user ? 'required' : '' ?>
                               style="width: 100%; padding: 0.75rem; border: 1px solid #d1d5db; border-radius: 0.5rem; font-size: 1rem;">
                    </div>
                    <div style="margin-bottom: 1.5rem;">
                        <label style="display: block; color: #374151; font-weight: 600; margin-bottom: 0.5rem; font-size: 0.875rem;">
                            Rol
                        </label>
                        <select name="rol" required style="width: 100%; padding: 0.75rem; border: 1px solid #d1d5db; border-radius: 0.5rem; font-size: 1rem;">
                            <option value="">Seleccionar rol</option>
                            <option value="admin" <?= ($editing_user['rol'] ?? '') === 'admin' ? 'selected' : '' ?>>👨‍💼 Administrador</option>
                            <option value="mesero" <?= ($editing_user['rol'] ?? '') === 'mesero' ? 'selected' : '' ?>>👨‍🍳 Mesero</option>
                        </select>
                    </div>
                    <div style="display: flex; gap: 0.5rem;">
                        <button type="submit" style="flex: 1; background-color: #10b981; color: white; padding: 0.75rem; border: none; border-radius: 0.5rem; font-weight: 600; cursor: pointer;">
                            <?= $editing_user ? 'Actualizar' : 'Agregar' ?> Usuario
                        </button>
                        <a href="?view=admin" style="background-color: #6b7280; color: white; padding: 0.75rem; border-radius: 0.5rem; text-decoration: none; font-weight: 600; display: flex; align-items: center; justify-content: center;">
                            Cancelar
                        </a>
                    </div>
                </form>
            </div>
        <?php endif; ?>

        <!-- ACCIONES -->
        <!-- FORMULARIO DE PRODUCTO -->
        <?php if ($show_add_form || $product_action === 'edit_product_form'): ?>
            <div style="background-color: white; border-radius: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 1.5rem; margin-bottom: 1.5rem;">
                <h3 style="font-size: 1.125rem; font-weight: 600; margin-bottom: 1rem; color: #1f2937;">
                    <?= $editing_product ? 'Editar Producto' : 'Agregar Nuevo Producto' ?>
                </h3>
                <form method="POST" action="?view=admin&action=<?= $editing_product ? 'edit_product' : 'add_product' ?>">
                    <?php if ($editing_product): ?>
                        <input type="hidden" name="id" value="<?= $editing_product['id'] ?>">
                    <?php endif; ?>
                    <div style="margin-bottom: 1rem;">
                        <label style="display: block; color: #374151; font-weight: 600; margin-bottom: 0.5rem; font-size: 0.875rem;">
                            Nombre del Producto
                        </label>
                        <input type="text" name="nombre" required
                               value="<?= htmlspecialchars($editing_product['nombre'] ?? '') ?>"
                               style="width: 100%; padding: 0.75rem; border: 1px solid #d1d5db; border-radius: 0.5rem; font-size: 1rem;">
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <label style="display: block; color: #374151; font-weight: 600; margin-bottom: 0.5rem; font-size: 0.875rem;">
                            Precio (Q)
                        </label>
                        <input type="number" name="precio" step="0.01" min="0" required
                               value="<?= $editing_product['precio'] ?? '' ?>"
                               style="width: 100%; padding: 0.75rem; border: 1px solid #d1d5db; border-radius: 0.5rem; font-size: 1rem;">
                    </div>
                    <div style="margin-bottom: 1.5rem;">
                        <label style="display: block; color: #374151; font-weight: 600; margin-bottom: 0.5rem; font-size: 0.875rem;">
                            Categoría
                        </label>
                        <select name="categoria" required style="width: 100%; padding: 0.75rem; border: 1px solid #d1d5db; border-radius: 0.5rem; font-size: 1rem;">
                            <option value="">Seleccionar categoría</option>
                            <option value="Hamburguesas" <?= ($editing_product['categoria'] ?? '') === 'Hamburguesas' ? 'selected' : '' ?>>Hamburguesas</option>
                            <option value="Hot Dogs" <?= ($editing_product['categoria'] ?? '') === 'Hot Dogs' ? 'selected' : '' ?>>Hot Dogs</option>
                            <option value="Bebidas" <?= ($editing_product['categoria'] ?? '') === 'Bebidas' ? 'selected' : '' ?>>Bebidas</option>
                            <option value="Acompañamientos" <?= ($editing_product['categoria'] ?? '') === 'Acompañamientos' ? 'selected' : '' ?>>Acompañamientos</option>
                            <option value="Tacos" <?= ($editing_product['categoria'] ?? '') === 'Tacos' ? 'selected' : '' ?>>Tacos</option>
                            <option value="Mexicanos" <?= ($editing_product['categoria'] ?? '') === 'Mexicanos' ? 'selected' : '' ?>>Mexicanos</option>
                            <option value="Postres" <?= ($editing_product['categoria'] ?? '') === 'Postres' ? 'selected' : '' ?>>Postres</option>
                        </select>
                    </div>
                    <div style="display: flex; gap: 0.5rem;">
                        <button type="submit" style="flex: 1; background-color: #10b981; color: white; padding: 0.75rem; border: none; border-radius: 0.5rem; font-weight: 600; cursor: pointer;">
                            <?= $editing_product ? 'Actualizar' : 'Agregar' ?> Producto
                        </button>
                        <a href="?view=admin" style="background-color: #6b7280; color: white; padding: 0.75rem; border-radius: 0.5rem; text-decoration: none; font-weight: 600; display: flex; align-items: center; justify-content: center;">
                            Cancelar
                        </a>
                    </div>
                </form>
            </div>
        <?php endif; ?>

        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
            <div style="background-color: white; border-radius: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 1.5rem;">
                <h3 style="font-size: 1.125rem; font-weight: 600; margin-bottom: 1rem; color: #1f2937;">Base de Datos</h3>
                <p style="color: #6b7280; font-size: 0.875rem; margin-bottom: 1rem;">
                    Base de datos: <strong><?= DB_NAME ?></strong><br>
                    Host: <strong><?= DB_HOST ?></strong>
                </p>
                <button onclick="alert('Funcionalidad de respaldo en desarrollo')" style="width: 100%; background-color: #10b981; color: white; padding: 0.75rem; border: none; border-radius: 0.5rem; font-weight: 600; cursor: pointer; margin-bottom: 0.5rem;">
                    💾 Respaldar BD
                </button>
            </div>
            
            <div style="background-color: white; border-radius: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 1.5rem;">
                <h3 style="font-size: 1.125rem; font-weight: 600; margin-bottom: 1rem; color: #1f2937;">Reportes</h3>
                <button onclick="alert('Generando reporte...')" style="width: 100%; background-color: #8b5cf6; color: white; padding: 0.75rem; border: none; border-radius: 0.5rem; font-weight: 600; margin-bottom: 0.5rem; cursor: pointer;">
                    📊 Ventas del Día
                </button>
                <button onclick="alert('Generando reporte...')" style="width: 100%; background-color: #6366f1; color: white; padding: 0.75rem; border: none; border-radius: 0.5rem; font-weight: 600; cursor: pointer;">
                    📈 Más Vendidos
                </button>
            </div>
            
            <div style="background-color: white; border-radius: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 1.5rem;">
                <h3 style="font-size: 1.125rem; font-weight: 600; margin-bottom: 1rem; color: #1f2937;">Descuentos Activos</h3>
                <?php 
                $discounts = $conn->query("SELECT * FROM descuentos WHERE activo = 1")->fetch_all(MYSQLI_ASSOC);
                foreach ($discounts as $disc):
                ?>
                    <div style="background-color: #fef3c7; padding: 0.5rem; border-radius: 0.375rem; margin-bottom: 0.5rem;">
                        <div style="font-weight: 600; color: #92400e; font-size: 0.875rem;">
                            <?= htmlspecialchars($disc['codigo']) ?>
                        </div>
                        <div style="color: #78350f; font-size: 0.75rem;">
                            <?= $disc['tipo'] === 'porcentaje' ? $disc['valor'] . '%' : 'Q' . number_format($disc['valor'], 2) ?> off
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
        </div>
    </div>
    <?php
}

// ====================================================================
// HTML Y RENDERIZADO
// ====================================================================
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema de Pedidos - Restaurante</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; background-color: #f3f4f6; }
        .nav { background-color: #047857; color: white; padding: 1rem 1.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .nav-content { display: flex; justify-content: space-between; align-items: center; max-width: 1920px; margin: 0 auto; }
        .nav h1 { font-size: 1.5rem; font-weight: bold; }
        .nav-links { display: flex; gap: 0.5rem; }
        .nav a { color: white; text-decoration: none; padding: 0.625rem 1rem; border-radius: 0.5rem; transition: all 0.2s; display: flex; align-items: center; gap: 0.5rem; font-weight: 500; }
        .nav a:hover:not(.active) { background-color: #059669; }
        .nav a.active { background-color: white; color: #047857; font-weight: 600; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .content { height: calc(100vh - 68px); overflow: hidden; }
    </style>
</head>
<body>
<div class="nav">
        <div class="nav-content">
            <h1>🌮Sistema de Pedidos - Restaurante SAZON MEXICANO</h1>
            <div style="display: flex; align-items: center; gap: 1rem;">
                <?php if ($isLoggedIn): ?>
                    <div style="display: flex; align-items: center; gap: 0.5rem; background-color: rgba(255,255,255,0.1); padding: 0.5rem 1rem; border-radius: 0.5rem;">
                        <span style="font-size: 1.25rem;"><?= $userRole === 'admin' ? '👨‍💼' : '👨‍🍳' ?></span>
                        <div>
                            <div style="font-weight: 600; font-size: 0.875rem;"><?= htmlspecialchars($userName) ?></div>
                            <div style="font-size: 0.75rem; opacity: 0.8;"><?= $userRole === 'admin' ? 'Administrador' : 'Mesero' ?></div>
                        </div>
                    </div>
                    <div class="nav-links">
                        <a href="?view=pos" class="<?= $view === 'pos' ? 'active' : '' ?>">
                            <?= icon('ShoppingCart', 18) ?> Caja (POS)
                        </a>
                        <a href="?view=kitchen" class="<?= $view === 'kitchen' ? 'active' : '' ?>">
                            <?= icon('ChefHat', 18) ?> Cocina
                        </a>
                        <?php if ($userRole === 'admin'): ?>
                            <a href="?view=admin" class="<?= $view === 'admin' ? 'active' : '' ?>">
                                <?= icon('Settings', 18) ?> Administrador
                            </a>
                        <?php endif; ?>
                        <a href="?action=logout" style="background-color: rgba(220, 38, 38, 0.2); color: white;">
                            🚪 Salir
                        </a>
                    </div>
                <?php endif; ?>
            </div>
        </div>
    </div>

<div class="content">
        <?php 
        if ($view === 'login') {
            renderLoginView();
        } else {
            switch ($view) {
                case 'pos':
                    renderPOSView($conn);
                    break;
                case 'kitchen':
                    renderKitchenView($conn);
                    break;
                case 'admin':
                    renderAdminView($conn);
                    break;
                default:
                    renderPOSView($conn);
            }
        }
        ?>
    </div>
</body>
</html>