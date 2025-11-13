#!/bin/bash

# Obtener puerto de Railway o usar 80 por defecto
PORT=${PORT:-80}

echo "========================================="
echo "Starting Apache on port: $PORT"
echo "PORT environment variable: $PORT"
echo "========================================="

# Backup de archivos originales
cp /etc/apache2/ports.conf /etc/apache2/ports.conf.bak 2>/dev/null || true
cp /etc/apache2/sites-available/000-default.conf /etc/apache2/sites-available/000-default.conf.bak 2>/dev/null || true

# Configurar ports.conf - reemplazar cualquier línea Listen
echo "Configuring /etc/apache2/ports.conf..."
sed -i.bak "s/^Listen .*/Listen $PORT/" /etc/apache2/ports.conf
if ! grep -q "^Listen $PORT" /etc/apache2/ports.conf; then
    echo "Listen $PORT" > /etc/apache2/ports.conf
    echo "Listen 443" >> /etc/apache2/ports.conf
fi

# Configurar VirtualHost - reemplazar cualquier puerto
echo "Configuring /etc/apache2/sites-available/000-default.conf..."
sed -i.bak "s/<VirtualHost \*:[0-9]*>/<VirtualHost *:$PORT>/" /etc/apache2/sites-available/000-default.conf

# Verificar configuración
echo "========================================="
echo "Apache Configuration Check:"
echo "========================================="
echo "ports.conf:"
cat /etc/apache2/ports.conf | grep -E "^Listen" || echo "No Listen directive found"
echo ""
echo "VirtualHost:"
grep -E "<VirtualHost" /etc/apache2/sites-available/000-default.conf || echo "No VirtualHost found"
echo "========================================="

# Configurar ServerName para evitar warnings
echo "ServerName localhost" >> /etc/apache2/apache2.conf

# Verificar sintaxis de Apache
echo "Checking Apache configuration syntax..."
apache2ctl configtest || {
    echo "ERROR: Apache configuration test failed!"
    echo "Showing configuration files:"
    cat /etc/apache2/ports.conf
    echo "---"
    cat /etc/apache2/sites-available/000-default.conf
    exit 1
}

# Iniciar Apache en foreground
echo "========================================="
echo "Starting Apache in foreground mode on port $PORT"
echo "========================================="
exec apache2-foreground

