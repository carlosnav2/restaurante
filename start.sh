#!/bin/bash
set -e

# Obtener puerto de Railway o usar 80 por defecto
PORT=${PORT:-80}

echo "========================================="
echo "Starting Apache on port: $PORT"
echo "========================================="

# Configurar Apache para usar el puerto dinámico
# Modificar ports.conf
if [ -f /etc/apache2/ports.conf ]; then
    sed -i "s/^Listen .*/Listen $PORT/" /etc/apache2/ports.conf || \
    echo "Listen $PORT" > /etc/apache2/ports.conf
    echo "✓ Configured /etc/apache2/ports.conf"
fi

# Modificar configuración de VirtualHost
if [ -f /etc/apache2/sites-available/000-default.conf ]; then
    # Reemplazar cualquier puerto existente
    sed -i "s/<VirtualHost \*:.*>/<VirtualHost *:$PORT>/" /etc/apache2/sites-available/000-default.conf
    echo "✓ Configured /etc/apache2/sites-available/000-default.conf"
fi

# Verificar configuración
echo "========================================="
echo "Apache Configuration:"
echo "========================================="
grep -E "Listen|VirtualHost" /etc/apache2/ports.conf /etc/apache2/sites-available/000-default.conf 2>/dev/null || true
echo "========================================="

# Iniciar Apache en foreground
echo "Starting Apache..."
exec apache2-foreground

