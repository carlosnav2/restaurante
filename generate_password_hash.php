<?php
/**
 * Script para generar hash de contraseña
 * Ejecuta: php generate_password_hash.php
 */

$password = 'Admin123!';
$hash = password_hash($password, PASSWORD_DEFAULT);

echo "Contraseña: $password\n";
echo "Hash generado: $hash\n\n";
echo "Copia este hash al archivo database.sql en la línea del INSERT de usuarios.\n";

