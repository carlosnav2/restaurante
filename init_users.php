<?php
/**
 * Script de inicialización de usuarios
 * Ejecuta este script UNA VEZ después de crear las tablas con database.sql
 * 
 * Uso: php init_users.php
 */

// Cargar variables de entorno
$db_host = getenv('MYSQLHOST') ?: getenv('DB_HOST') ?: 'localhost';
$db_user = getenv('MYSQLUSER') ?: getenv('DB_USER') ?: 'root';
$db_pass = getenv('MYSQLPASSWORD') ?: getenv('DB_PASS') ?: '';
$db_name = getenv('MYSQLDATABASE') ?: getenv('DB_NAME') ?: 'restaurante_db';
$db_port = getenv('MYSQLPORT') ?: getenv('DB_PORT') ?: 3306;

// Conectar a la base de datos
$conn = new mysqli($db_host, $db_user, $db_pass, $db_name, $db_port);

if ($conn->connect_error) {
    die("Error de conexión: " . $conn->connect_error . "\n");
}

echo "✅ Conectado a la base de datos: $db_name\n\n";

// Verificar si ya existen usuarios
$check = $conn->query("SELECT COUNT(*) as count FROM usuarios");
$row = $check->fetch_assoc();

if ($row['count'] > 0) {
    echo "⚠️  Ya existen usuarios en la base de datos.\n";
    echo "¿Deseas continuar y actualizar las contraseñas? (s/n): ";
    $handle = fopen("php://stdin", "r");
    $line = fgets($handle);
    if (trim($line) !== 's') {
        echo "Operación cancelada.\n";
        exit;
    }
    fclose($handle);
}

// Generar hashes de contraseñas
$admin_hash = password_hash('admin123', PASSWORD_DEFAULT);
$mesero_hash = password_hash('mesero123', PASSWORD_DEFAULT);

// Insertar o actualizar usuarios
$stmt = $conn->prepare("INSERT INTO usuarios (username, password, nombre, rol) VALUES (?, ?, ?, ?) ON DUPLICATE KEY UPDATE password = VALUES(password), nombre = VALUES(nombre), rol = VALUES(rol)");

// Admin
$username = 'admin';
$nombre = 'Administrador';
$rol = 'admin';
$stmt->bind_param("ssss", $username, $admin_hash, $nombre, $rol);
$stmt->execute();

// Mesero
$username = 'mesero';
$nombre = 'Mesero Principal';
$rol = 'mesero';
$stmt->bind_param("ssss", $username, $mesero_hash, $nombre, $rol);
$stmt->execute();

$stmt->close();

echo "\n✅ Usuarios creados/actualizados exitosamente:\n\n";
echo "👨‍💼 Administrador:\n";
echo "   Usuario: admin\n";
echo "   Contraseña: admin123\n\n";
echo "👨‍🍳 Mesero:\n";
echo "   Usuario: mesero\n";
echo "   Contraseña: mesero123\n\n";
echo "⚠️  IMPORTANTE: Cambia estas contraseñas después del primer inicio.\n";

$conn->close();

