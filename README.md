# 🌮 Sistema de Pedidos - Restaurante Sazón Mexicano

Sistema completo de gestión de pedidos para restaurante desarrollado en PHP con MySQL.

## 🚀 Características

- **Sistema POS (Point of Sale)**: Interfaz intuitiva para tomar pedidos
- **Pantalla de Cocina**: Vista en tiempo real de pedidos pendientes
- **Panel de Administración**: Gestión de productos, usuarios y estadísticas
- **Sistema de Descuentos**: Aplicación de códigos de descuento
- **Tickets Imprimibles**: Generación de tickets para pedidos
- **Autenticación**: Sistema de login con roles (Admin/Mesero)

## 📋 Requisitos

- PHP >= 7.4
- MySQL >= 5.7 o MariaDB >= 10.2
- Extensiones PHP: mysqli, session

## 🛠️ Instalación Local

1. **Clonar el repositorio**
   ```bash
   git clone <tu-repositorio>
   cd restaurante
   ```

2. **Configurar base de datos**
   - Crea una base de datos MySQL
   - Copia `.env.example` a `.env` y configura las variables:
     ```env
     DB_HOST=localhost
     DB_USER=root
     DB_PASS=tu_contraseña
     DB_NAME=restaurante_db
     ```

3. **Ejecutar el servidor**
   ```bash
   php -S localhost:8000
   ```

4. **Acceder a la aplicación**
   - Abre tu navegador en `http://localhost:8000`
   - El sistema creará automáticamente las tablas necesarias

## 🚂 Despliegue en Railway

Railway es una plataforma que facilita el despliegue de aplicaciones. Sigue estos pasos:

### Paso 1: Preparar el Repositorio

1. Asegúrate de que todos los archivos estén en tu repositorio Git
2. Haz commit de todos los cambios:
   ```bash
   git add .
   git commit -m "Preparado para Railway"
   git push
   ```

### Paso 2: Crear Proyecto en Railway

1. Ve a [railway.app](https://railway.app) y crea una cuenta
2. Crea un nuevo proyecto
3. Conecta tu repositorio de GitHub/GitLab

### Paso 3: Agregar Base de Datos MySQL

1. En tu proyecto de Railway, haz clic en **"+ New"**
2. Selecciona **"Database"** → **"MySQL"**
3. Railway creará automáticamente una base de datos MySQL
4. Anota las credenciales que Railway proporciona

### Paso 4: Configurar Variables de Entorno

**¡Buenas noticias!** El código ya está configurado para usar automáticamente las variables de entorno que Railway proporciona cuando agregas un servicio MySQL.

Railway crea automáticamente estas variables:
- `MYSQLHOST`
- `MYSQLUSER`
- `MYSQLPASSWORD`
- `MYSQLDATABASE`

El código las detectará automáticamente. **No necesitas configurar nada manualmente** si usas el servicio MySQL de Railway.

Si por alguna razón necesitas usar nombres personalizados, puedes agregar estas variables en la sección **"Variables"**:
```
DB_HOST=tu_host
DB_USER=tu_usuario
DB_PASS=tu_contraseña
DB_NAME=tu_base_de_datos
```

### Paso 5: Desplegar

1. Railway detectará automáticamente que es un proyecto PHP
2. El despliegue comenzará automáticamente
3. Una vez completado, Railway te dará una URL pública

### Paso 6: Verificar Despliegue

1. Accede a la URL proporcionada por Railway
2. Deberías ver la pantalla de login
3. El sistema creará automáticamente las tablas en la base de datos

## 👤 Usuarios por Defecto

El sistema crea automáticamente estos usuarios al iniciar:

- **Administrador**
  - Usuario: `admin`
  - Contraseña: `admin123`

- **Mesero**
  - Usuario: `mesero`
  - Contraseña: `mesero123`

**⚠️ IMPORTANTE**: Cambia estas contraseñas después del primer inicio en producción.

## 📝 Códigos de Descuento

El sistema incluye códigos de descuento de ejemplo:
- `DESC10`: 10% de descuento
- `DESC20`: 20% de descuento
- `FIJO15`: Q15.00 de descuento fijo

## 🔧 Solución de Problemas

### Error de conexión a base de datos

- Verifica que las variables de entorno estén correctamente configuradas
- Asegúrate de que el servicio MySQL esté corriendo en Railway
- Verifica que el host de la base de datos sea accesible desde tu servicio PHP

### Las tablas no se crean

- Verifica los permisos del usuario de la base de datos
- Revisa los logs de Railway para ver errores específicos

### La aplicación no carga

- Verifica que el puerto esté correctamente configurado (Railway usa la variable `$PORT`)
- Revisa los logs de despliegue en Railway

## 📦 Estructura del Proyecto

```
restaurante/
├── index.php          # Archivo principal de la aplicación
├── composer.json      # Dependencias PHP
├── Procfile          # Comando de inicio para Railway
├── railway.json      # Configuración de Railway
├── .env.example      # Plantilla de variables de entorno
├── .gitignore        # Archivos a ignorar en Git
└── README.md         # Este archivo
```

## 🆘 Soporte

Para problemas o preguntas, revisa los logs de Railway o contacta al equipo de desarrollo.

## 📄 Licencia

Este proyecto es de uso interno del restaurante.

