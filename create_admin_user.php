<?php
/**
 * Script para crear/actualizar el usuario administrador
 * Ejecuta este script UNA VEZ después de crear las tablas
 * 
 * Uso: php create_admin_user.php
 */

// Cargar variables de entorno (igual que index.php)
$db_host = getenv('MYSQLHOST') ?: getenv('DB_HOST') ?: 'localhost';
$db_user = getenv('MYSQLUSER') ?: getenv('DB_USER') ?: 'root';
$db_pass = getenv('MYSQLPASSWORD') ?: getenv('DB_PASS') ?: '';
$db_name = getenv('MYSQLDATABASE') ?: getenv('DB_NAME') ?: 'restaurante_db';
$db_port = getenv('MYSQLPORT') ?: getenv('DB_PORT') ?: 3306;

// Conectar a la base de datos
$conn = new mysqli($db_host, $db_user, $db_pass, $db_name, $db_port);

if ($conn->connect_error) {
    die("❌ Error de conexión: " . $conn->connect_error . "\n");
}

echo "✅ Conectado a la base de datos: $db_name\n\n";

// Verificar que la tabla usuarios existe
$check_table = $conn->query("SHOW TABLES LIKE 'usuarios'");
if ($check_table->num_rows == 0) {
    die("❌ Error: La tabla 'usuarios' no existe. Ejecuta primero el script database.sql\n");
}

// Credenciales del administrador
$username = 'admin';
$password = 'Admin123!';
$nombre = 'Administrador';
$rol = 'admin';

// Generar hash de contraseña
$password_hash = password_hash($password, PASSWORD_DEFAULT);

// Verificar si el usuario ya existe
$check_user = $conn->prepare("SELECT id FROM usuarios WHERE username = ?");
$check_user->bind_param("s", $username);
$check_user->execute();
$result = $check_user->get_result();

if ($result->num_rows > 0) {
    // Actualizar usuario existente
    $stmt = $conn->prepare("UPDATE usuarios SET password = ?, nombre = ?, rol = ?, activo = 1 WHERE username = ?");
    $stmt->bind_param("ssss", $password_hash, $nombre, $rol, $username);
    
    if ($stmt->execute()) {
        echo "✅ Usuario 'admin' actualizado exitosamente\n\n";
    } else {
        die("❌ Error al actualizar usuario: " . $stmt->error . "\n");
    }
    $stmt->close();
} else {
    // Crear nuevo usuario
    $stmt = $conn->prepare("INSERT INTO usuarios (username, password, nombre, rol) VALUES (?, ?, ?, ?)");
    $stmt->bind_param("ssss", $username, $password_hash, $nombre, $rol);
    
    if ($stmt->execute()) {
        echo "✅ Usuario 'admin' creado exitosamente\n\n";
    } else {
        die("❌ Error al crear usuario: " . $stmt->error . "\n");
    }
    $stmt->close();
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n";
echo "👤 CREDENCIALES DE ACCESO\n";
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n";
echo "Usuario: $username\n";
echo "Contraseña: $password\n";
echo "Rol: $rol\n\n";
echo "⚠️  IMPORTANTE: Cambia esta contraseña después del primer login.\n";
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n";

$conn->close();

