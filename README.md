# Sistema de Pedidos - Restaurante Sazón Mexicano 🍽️

Sistema de pedidos completo con base de datos para restaurante, ejecutándose en Docker localmente o desplegado en Railway.

## 🚀 Inicio Rápido

### Requisitos
- Docker Desktop instalado
- Docker Compose instalado (incluido en Docker Desktop)

### Pasos para ejecutar

1. **Construir y levantar los contenedores:**
   ```bash
   docker-compose up -d
   ```

2. **Acceder a la aplicación:**
   - Abre tu navegador en: `http://localhost:8080`

3. **Credenciales de acceso:**
   - **Administrador:**
     - Usuario: `admin`
     - Contraseña: `admin123`
   - **Mesero:**
     - Usuario: `mesero`
     - Contraseña: `mesero123`

### Comandos útiles

**Ver logs:**
```bash
docker-compose logs -f
```

**Detener los contenedores:**
```bash
docker-compose down
```

**Detener y eliminar volúmenes (incluye base de datos):**
```bash
docker-compose down -v
```

**Reconstruir los contenedores:**
```bash
docker-compose up -d --build
```

**Acceder a la base de datos MySQL:**
```bash
docker exec -it sazon_db mysql -u root -proot123 restaurante_db
```

## 📋 Configuración

### Variables de Entorno

Las siguientes variables se pueden configurar en `docker-compose.yml`:

- `DB_HOST`: Host de la base de datos (default: `db`)
- `DB_USER`: Usuario de MySQL (default: `root`)
- `DB_PASS`: Contraseña de MySQL (default: `root123`)
- `DB_NAME`: Nombre de la base de datos (default: `restaurante_db`)

### Puertos

- **8080**: Aplicación web (PHP/Apache)
- **3306**: MySQL (acceso directo a la base de datos)

## 🏗️ Estructura

```
docker-sazon/
├── index.php          # Aplicación principal
├── Dockerfile         # Configuración de la imagen PHP
├── docker-compose.yml # Orquestación de servicios
└── README.md         # Este archivo
```

## 🐳 Servicios Docker

- **web**: Servidor PHP 8.2 con Apache
- **db**: Base de datos MySQL 8.0

## 📝 Notas

- La base de datos se crea automáticamente al iniciar
- Los datos de MySQL se persisten en un volumen Docker
- Los cambios en `index.php` se reflejan automáticamente gracias al volumen montado

## 🔧 Solución de Problemas

**Error de conexión a la base de datos:**
- Espera unos segundos después de `docker-compose up` para que MySQL termine de inicializarse
- Verifica que el contenedor `sazon_db` esté corriendo: `docker ps`

**Puerto 8080 ya en uso:**
- Cambia el puerto en `docker-compose.yml`: `"8081:80"` (o el que prefieras)

**Reiniciar desde cero:**
```bash
docker-compose down -v
docker-compose up -d --build
```

---

## 🚂 Desplegar en Railway

### Pasos Rápidos

1. **Sube tu código a GitHub/GitLab**
2. **Ve a [Railway](https://railway.app) y crea un nuevo proyecto**
3. **Conecta tu repositorio**
4. **Agrega un servicio MySQL:**
   - Haz clic en "+ New" → "Database" → "Add MySQL"
5. **Configura las variables de entorno en tu servicio web:**
   - Railway inyecta automáticamente las variables MySQL
   - El código ya está configurado para usarlas automáticamente
6. **Genera un dominio público en Settings → Networking**

### Documentación Completa

Para instrucciones detalladas, consulta: **[railway-setup.md](railway-setup.md)**

### Archivos de Configuración Railway

- `railway.toml` - Configuración de Railway
- `railway.json` - Configuración alternativa
- `.railwayignore` - Archivos a ignorar en el despliegue

### Variables de Entorno en Railway

Railway proporciona automáticamente estas variables cuando agregas MySQL:
- `MYSQLHOST`
- `MYSQLUSER`
- `MYSQLPASSWORD`
- `MYSQLDATABASE`

El código PHP ya está configurado para usar estas variables automáticamente.

