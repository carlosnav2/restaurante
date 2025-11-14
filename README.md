# Sistema de Pedidos - Restaurante Sazón Mexicano

Sistema completo de gestión de pedidos desarrollado con FastAPI, Python y MySQL.

## 🚀 Características

- **Sistema POS (Point of Sale)**: Interfaz para tomar pedidos y gestionar el carrito
- **Pantalla de Cocina**: Vista para cocineros con gestión de estados de pedidos
- **Panel de Administración**: Gestión completa de productos, usuarios y estadísticas
- **Sistema de Autenticación**: Login con roles (admin/mesero)
- **Descuentos**: Sistema de códigos de descuento (porcentaje o fijo)
- **Tickets Imprimibles**: Generación de tickets para impresión
- **Base de Datos MySQL**: Almacenamiento persistente de toda la información

## 📋 Requisitos

- Python 3.8 o superior
- MySQL 5.7 o superior
- pip (gestor de paquetes de Python)

## 🔧 Instalación

1. **Clonar o descargar el proyecto**

2. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno:**
   - Copia el archivo `.env.example` a `.env`
   - Edita `.env` con tus credenciales de MySQL:
   ```env
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASS=tu_contraseña
   DB_NAME=restaurante_db
   SECRET_KEY=tu-clave-secreta-muy-segura
   DEBUG=False
   ENVIRONMENT=development
   ```
   
   > **Importante:** El archivo `.env` contiene información sensible y no debe subirse al repositorio. Asegúrate de que esté en `.gitignore`.

4. **Inicializar la base de datos (IMPORTANTE):**
```bash
python init_db.py
```

Este script creará las tablas y datos iniciales. **Debe ejecutarse antes de iniciar la aplicación por primera vez.**

5. **Ejecutar la aplicación:**
```bash
python main.py
```

O usando uvicorn directamente:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

6. **Acceder a la aplicación:**
   - Abre tu navegador en: `http://localhost:8000`

## 👤 Usuarios por Defecto

El script `init_db.py` crea dos usuarios de prueba:

**Administrador:**
- Usuario: `admin`
- Contraseña: `admin123`

**Mesero:**
- Usuario: `mesero`
- Contraseña: `mesero123`

> **Nota:** Estos usuarios se crean cuando ejecutas `python init_db.py` por primera vez.

## 📁 Estructura del Proyecto

```
.
├── main.py                 # Aplicación principal FastAPI
├── init_db.py             # Script para inicializar la base de datos
├── config.py              # Configuración (BD, secretos) - Usa .env
├── database.py            # Configuración y creación de BD
├── models.py              # Modelos de datos
├── auth.py                # Autenticación y seguridad
├── services.py            # Lógica de negocio
├── requirements.txt       # Dependencias Python
├── Procfile               # Configuración para Railway/Heroku
├── runtime.txt            # Versión de Python
├── .env.example           # Ejemplo de configuración (.env)
├── .gitignore             # Archivos ignorados por Git
├── routers/               # Routers (controladores)
│   ├── auth.py           # Login/logout
│   ├── pos.py            # Sistema POS
│   ├── kitchen.py        # Pantalla de cocina
│   ├── admin.py          # Panel administrador
│   ├── users.py          # CRUD de usuarios
│   ├── products.py       # CRUD de productos
│   ├── discounts.py      # CRUD de descuentos
│   ├── reports.py        # Reportes y exportación PDF
│   └── ticket.py         # Tickets de impresión
└── templates/             # Plantillas Jinja2
    ├── base.html         # Plantilla base (Bootstrap 5)
    ├── login.html        # Página de login
    ├── pos.html          # Vista POS
    ├── kitchen.html      # Vista cocina
    ├── admin.html        # Vista administrador
    └── ticket.html       # Ticket imprimible
```

## 🎯 Funcionalidades Principales

### Sistema POS
- Visualización de productos por categoría
- Agregar productos al carrito
- Aplicar códigos de descuento
- Confirmar pedidos
- Limpiar carrito

### Pantalla de Cocina
- Ver pedidos activos
- Cambiar estado de pedidos (pendiente → en preparación → listo → entregado)
- Ver tiempo de preparación
- Imprimir tickets

### Panel de Administración
- **Gestión de Productos:**
  - Agregar, editar, eliminar productos
  - Organizar por categorías
  
- **Gestión de Usuarios:**
  - Crear, editar, activar/desactivar usuarios
  - Asignar roles (admin/mesero)
  - Búsqueda y filtrado de usuarios
  - Validación de usuarios duplicados
  - Vista dedicada en `/admin/users`
  
- **Estadísticas:**
  - Ventas del día
  - Total de pedidos
  - Tiempo promedio de preparación
  - Pedidos en preparación

- **Descuentos:**
  - Ver códigos activos
  - Códigos de ejemplo: DESC10 (10%), DESC20 (20%), FIJO15 (Q15)

## 🔐 Seguridad

- Contraseñas hasheadas con bcrypt
- Sesiones seguras con SessionMiddleware
- Verificación de roles para accesos restringidos
- Protección contra SQL injection mediante consultas parametrizadas

## 📊 Base de Datos

El sistema crea automáticamente las siguientes tablas:

- `usuarios`: Usuarios del sistema (admin/mesero)
- `productos`: Catálogo de productos del menú
- `pedidos`: Pedidos realizados
- `pedido_items`: Items de cada pedido
- `descuentos`: Códigos de descuento

## 🛠️ Tecnologías Utilizadas

- **FastAPI**: Framework web moderno y rápido
- **Jinja2**: Motor de plantillas
- **MySQL**: Base de datos relacional
- **mysql-connector-python**: Conector MySQL
- **passlib**: Hash de contraseñas
- **python-jose**: Manejo de tokens JWT (preparado para futuras mejoras)

## 📝 Notas

- El sistema inicializa automáticamente la base de datos y datos de ejemplo al iniciar
- Las contraseñas se almacenan hasheadas en la base de datos
- Los productos y usuarios se "eliminan" desactivándolos (soft delete) para mantener historial
- Los tickets son imprimibles directamente desde el navegador

## 🚂 Despliegue en Railway

### Requisitos Previos

1. Cuenta en [Railway](https://railway.app/)
2. Git instalado
3. Repositorio del proyecto en GitHub/GitLab/Bitbucket (opcional)

### Pasos para Desplegar

#### 1. Preparar el Proyecto

El proyecto ya está configurado para Railway:
- ✅ `Procfile` configurado
- ✅ `runtime.txt` especificando versión de Python
- ✅ `requirements.txt` con todas las dependencias
- ✅ `config.py` soporta variables de Railway automáticamente

#### 2. Crear Proyecto en Railway

1. Inicia sesión en [Railway](https://railway.app/)
2. Haz clic en "New Project"
3. Selecciona "Deploy from GitHub repo" (si tienes el proyecto en GitHub) o "Empty Project"

#### 3. Agregar Servicio MySQL

1. En tu proyecto de Railway, haz clic en "New"
2. Selecciona "Database" → "Add MySQL"
3. Railway creará automáticamente una instancia MySQL y configurará las variables de entorno:
   - `MYSQL_HOST` o `MYSQLHOST`
   - `MYSQL_PORT` o `MYSQLPORT`
   - `MYSQL_USER` o `MYSQLUSER`
   - `MYSQL_PASSWORD` o `MYSQLPASSWORD`
   - `MYSQL_DATABASE` o `MYSQLDATABASE`

#### 4. Configurar Variables de Entorno

1. Ve a tu servicio web en Railway
2. Haz clic en "Variables"
3. Agrega las siguientes variables (si no se configuraron automáticamente):

```env
# La aplicación detecta automáticamente las variables de MySQL de Railway
# Pero puedes mapearlas manualmente si es necesario:

DB_HOST=${{MySQL.MYSQLHOST}}
DB_PORT=${{MySQL.MYSQLPORT}}
DB_USER=${{MySQL.MYSQLUSER}}
DB_PASS=${{MySQL.MYSQLPASSWORD}}
DB_NAME=${{MySQL.MYSQLDATABASE}}

# O usar directamente las variables de Railway (la app las detecta automáticamente)

# SECRET_KEY es importante, genera una segura:
SECRET_KEY=tu-clave-secreta-muy-segura-generar-una-nueva
ALGORITHM=HS256
DEBUG=False
ENVIRONMENT=production
```

#### 5. Inicializar la Base de Datos

**Opción A: Usando Railway CLI**

1. Instala Railway CLI:
```bash
npm i -g @railway/cli
```

2. Inicia sesión:
```bash
railway login
```

3. Vincula tu proyecto:
```bash
railway link
```

4. Ejecuta el script de inicialización:
```bash
railway run python init_db.py
```

**Opción B: Desde la terminal de Railway**

1. En Railway, ve a tu servicio web
2. Haz clic en "Deployments" → selecciona el último deployment
3. Haz clic en "View Logs" y luego en "Shell"
4. Ejecuta:
```bash
python init_db.py
```

#### 6. Configurar Dominio (Opcional)

1. En Railway, ve a tu servicio web
2. Haz clic en "Settings" → "Generate Domain"
3. Railway asignará un dominio automático como `tu-proyecto.up.railway.app`

### Configuración Automática

El archivo `config.py` está configurado para detectar automáticamente las variables de entorno de Railway:
- Si detecta `MYSQL_HOST` o `MYSQLHOST`, las usa automáticamente
- Si no encuentra variables de Railway, usa las variables locales del `.env`

### Verificar Despliegue

1. Ve a tu dominio en Railway
2. Deberías ver la página de login
3. Inicia sesión con:
   - Usuario: `admin`
   - Contraseña: `admin123`

### Actualizar la Aplicación

Cada vez que hagas `git push` a tu repositorio, Railway automáticamente:
1. Detecta los cambios
2. Reconstruye la aplicación
3. Reinstala dependencias
4. Reinicia el servicio

### Solución de Problemas en Railway

**Error: No se puede conectar a la base de datos**
- Verifica que el servicio MySQL esté corriendo
- Revisa las variables de entorno en Railway
- Asegúrate de que los servicios estén en el mismo proyecto

**Error: Application failed to respond**
- Revisa los logs en Railway: "View Logs"
- Verifica que el `Procfile` esté correcto
- Asegúrate de que el puerto sea `$PORT` (Railway lo proporciona automáticamente)

**Error: Database initialization failed**
- Ejecuta `python init_db.py` manualmente desde Railway Shell
- Verifica que las credenciales de MySQL sean correctas
- Asegúrate de tener permisos para crear bases de datos

## 🐛 Solución de Problemas

**Error de conexión a MySQL:**
- Verifica que MySQL esté corriendo
- Revisa las credenciales en `.env`
- Asegúrate de tener permisos para crear bases de datos

**Error al importar módulos:**
- Verifica que todas las dependencias estén instaladas: `pip install -r requirements.txt`
- Asegúrate de estar en el directorio correcto del proyecto


## 📄 Licencia

Este proyecto es de uso interno para el Restaurante Sazón Mexicano.

---

Desarrollado con ❤️ usando FastAPI y Python

