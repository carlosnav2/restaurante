FROM php:8.2-apache

# Instalar extensiones PHP necesarias
RUN docker-php-ext-install mysqli pdo pdo_mysql && \
    docker-php-ext-enable mysqli

# Habilitar mod_rewrite de Apache
RUN a2enmod rewrite

# Configurar directorio de trabajo
WORKDIR /var/www/html

# Copiar archivos del proyecto
COPY index.php /var/www/html/

# Copiar script de inicio
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Configurar permisos
RUN chown -R www-data:www-data /var/www/html && \
    chmod -R 755 /var/www/html

# Exponer puerto (Railway usa variable PORT)
EXPOSE 80

# Usar script de inicio personalizado
CMD ["/start.sh"]

