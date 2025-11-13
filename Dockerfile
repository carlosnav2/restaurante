FROM php:8.2-apache

# Instalar extensiones PHP necesarias
RUN docker-php-ext-install mysqli pdo pdo_mysql && \
    docker-php-ext-enable mysqli

# Habilitar mod_rewrite de Apache
RUN a2enmod rewrite

# Configurar Apache para usar puerto dinámico (Railway)
RUN echo 'Listen ${PORT:-80}' > /etc/apache2/ports.conf && \
    echo '<VirtualHost *:${PORT:-80}>' > /etc/apache2/sites-available/000-default.conf && \
    echo '  ServerAdmin webmaster@localhost' >> /etc/apache2/sites-available/000-default.conf && \
    echo '  DocumentRoot /var/www/html' >> /etc/apache2/sites-available/000-default.conf && \
    echo '  <Directory /var/www/html>' >> /etc/apache2/sites-available/000-default.conf && \
    echo '    Options Indexes FollowSymLinks' >> /etc/apache2/sites-available/000-default.conf && \
    echo '    AllowOverride All' >> /etc/apache2/sites-available/000-default.conf && \
    echo '    Require all granted' >> /etc/apache2/sites-available/000-default.conf && \
    echo '  </Directory>' >> /etc/apache2/sites-available/000-default.conf && \
    echo '  ErrorLog ${APACHE_LOG_DIR}/error.log' >> /etc/apache2/sites-available/000-default.conf && \
    echo '  CustomLog ${APACHE_LOG_DIR}/access.log combined' >> /etc/apache2/sites-available/000-default.conf && \
    echo '</VirtualHost>' >> /etc/apache2/sites-available/000-default.conf

# Script de inicio para usar puerto dinámico
RUN echo '#!/bin/bash' > /start.sh && \
    echo 'export PORT=${PORT:-80}' >> /start.sh && \
    echo 'sed -i "s/\${PORT:-80}/$PORT/g" /etc/apache2/ports.conf' >> /start.sh && \
    echo 'sed -i "s/\${PORT:-80}/$PORT/g" /etc/apache2/sites-available/000-default.conf' >> /start.sh && \
    echo 'apache2-foreground' >> /start.sh && \
    chmod +x /start.sh

# Configurar directorio de trabajo
WORKDIR /var/www/html

# Copiar archivos del proyecto
COPY index.php /var/www/html/

# Configurar permisos
RUN chown -R www-data:www-data /var/www/html && \
    chmod -R 755 /var/www/html

# Exponer puerto (Railway usa variable PORT)
EXPOSE 80

# Usar script de inicio personalizado
CMD ["/start.sh"]

