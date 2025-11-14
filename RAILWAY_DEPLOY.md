# 🚂 Guía de Despliegue en Railway

Esta guía te ayudará a desplegar el Sistema de Pedidos en Railway.

## 📋 Checklist de Preparación

Antes de desplegar, asegúrate de tener:

- ✅ Cuenta en [Railway](https://railway.app/)
- ✅ Proyecto configurado con `Procfile`, `runtime.txt`, y `requirements.txt`
- ✅ Variables de entorno configuradas en `.env.example`

## 🚀 Pasos de Despliegue

### 1. Preparar el Repositorio

1. **Asegúrate de que `.env` esté en `.gitignore`**
   ```bash
   # Verifica que .gitignore incluya:
   .env
   .env.local
   .env.*.local
   ```

2. **Crea un repositorio Git (si aún no lo tienes)**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

3. **Sube a GitHub/GitLab/Bitbucket (opcional pero recomendado)**
   ```bash
   git remote add origin tu-repositorio-url
   git push -u origin main
   ```

### 2. Crear Proyecto en Railway

1. **Inicia sesión en Railway**
   - Ve a [railway.app](https://railway.app/)
   - Inicia sesión con GitHub/GitLab/Email

2. **Crear nuevo proyecto**
   - Haz clic en "New Project"
   - Selecciona "Deploy from GitHub repo" (si tienes el proyecto en GitHub)
   - O selecciona "Empty Project" y luego "Deploy from GitHub repo"

3. **Conectar repositorio**
   - Autoriza Railway a acceder a tu repositorio
   - Selecciona el repositorio del proyecto
   - Railway detectará automáticamente que es un proyecto Python

### 3. Agregar Servicio MySQL

1. **En tu proyecto de Railway**
   - Haz clic en "New"
   - Selecciona "Database"
   - Elige "Add MySQL"

2. **Railway creará automáticamente:**
   - Instancia MySQL
   - Variables de entorno:
     - `MYSQL_HOST` o `MYSQLHOST`
     - `MYSQL_PORT` o `MYSQLPORT`
     - `MYSQL_USER` o `MYSQLUSER`
     - `MYSQL_PASSWORD` o `MYSQLPASSWORD`
     - `MYSQL_DATABASE` o `MYSQLDATABASE`

### 4. Configurar Variables de Entorno

El archivo `config.py` detecta automáticamente las variables de Railway, pero puedes configurarlas manualmente:

1. **Ve a tu servicio web en Railway**
   - Haz clic en tu servicio (no el de MySQL)
   - Ve a la pestaña "Variables"

2. **Agrega estas variables (si no están automáticamente):**

   ```env
   # Mapear variables de MySQL (opcional, la app las detecta automáticamente)
   DB_HOST=${{MySQL.MYSQLHOST}}
   DB_PORT=${{MySQL.MYSQLPORT}}
   DB_USER=${{MySQL.MYSQLUSER}}
   DB_PASS=${{MySQL.MYSQLPASSWORD}}
   DB_NAME=${{MySQL.MYSQLDATABASE}}
   
   # IMPORTANTE: Genera una SECRET_KEY segura
   SECRET_KEY=genera-una-clave-secreta-muy-segura-aqui
   ALGORITHM=HS256
   DEBUG=False
   ENVIRONMENT=production
   ```

3. **Generar SECRET_KEY segura:**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   
   Copia el resultado y úsalo como `SECRET_KEY` en Railway.

### 5. Inicializar Base de Datos

**Opción A: Usando Railway CLI (Recomendado)**

1. **Instalar Railway CLI:**
   ```bash
   npm i -g @railway/cli
   ```

2. **Iniciar sesión:**
   ```bash
   railway login
   ```

3. **Vincular proyecto:**
   ```bash
   railway link
   ```

4. **Ejecutar script de inicialización:**
   ```bash
   railway run python init_db.py
   ```

**Opción B: Desde Railway Dashboard**

1. Ve a tu servicio web en Railway
2. Haz clic en "Deployments"
3. Selecciona el último deployment
4. Haz clic en "View Logs"
5. Luego haz clic en "Shell" (si está disponible)
6. Ejecuta:
   ```bash
   python init_db.py
   ```

### 6. Configurar Dominio

1. **Ve a tu servicio web en Railway**
2. Haz clic en "Settings"
3. En la sección "Domains", haz clic en "Generate Domain"
4. Railway asignará un dominio como: `tu-proyecto.up.railway.app`

### 7. Verificar Despliegue

1. **Abre tu dominio de Railway**
2. Deberías ver la página de login
3. **Inicia sesión con:**
   - Usuario: `admin`
   - Contraseña: `admin123`

## 🔄 Actualizar la Aplicación

Cada vez que hagas cambios:

1. **Haz commit y push a tu repositorio:**
   ```bash
   git add .
   git commit -m "Descripción de cambios"
   git push
   ```

2. **Railway automáticamente:**
   - Detecta los cambios
   - Reconstruye la aplicación
   - Reinstala dependencias
   - Reinicia el servicio

## 🐛 Solución de Problemas

### Error: No se puede conectar a MySQL

**Verificar:**
1. Que el servicio MySQL esté corriendo (status verde)
2. Las variables de entorno estén configuradas
3. Que ambos servicios estén en el mismo proyecto de Railway

**Solución:**
- Ve a Variables del servicio web
- Verifica que las variables de MySQL estén disponibles
- Si no están, agrégalas manualmente como se muestra arriba

### Error: Application failed to respond

**Verificar:**
1. Los logs en Railway: "View Logs"
2. Que el `Procfile` esté correcto
3. Que el puerto sea `$PORT` (Railway lo proporciona)

**Solución:**
- Revisa los logs para ver el error específico
- Verifica que `Procfile` contenga: `web: uvicorn main:app --host 0.0.0.0 --port $PORT`

### Error: Database initialization failed

**Verificar:**
1. Que las credenciales de MySQL sean correctas
2. Que tengas permisos para crear bases de datos
3. Los logs de error en Railway

**Solución:**
- Ejecuta `python init_db.py` manualmente desde Railway Shell
- Verifica las variables de entorno de MySQL
- Asegúrate de que MySQL esté completamente iniciado antes de ejecutar el script

### Error: Module not found

**Verificar:**
1. Que `requirements.txt` tenga todas las dependencias
2. Los logs de build en Railway

**Solución:**
- Verifica que todas las dependencias estén en `requirements.txt`
- Revisa los logs de build para ver qué dependencia falta

## 📝 Notas Importantes

1. **SECRET_KEY**: Es crítico que uses una SECRET_KEY segura y única en producción
2. **Base de datos**: Asegúrate de ejecutar `init_db.py` después del primer despliegue
3. **Variables de entorno**: Railway proporciona automáticamente las variables de MySQL, pero puedes mapearlas manualmente si es necesario
4. **Puerto**: Railway usa la variable `PORT` automáticamente, no la definas manualmente
5. **Logs**: Revisa siempre los logs en Railway para diagnosticar problemas

## 🔒 Seguridad en Producción

Antes de usar en producción:

1. ✅ Cambia la SECRET_KEY por una generada aleatoriamente
2. ✅ Cambia las contraseñas de los usuarios por defecto
3. ✅ Configura DEBUG=False
4. ✅ Configura ENVIRONMENT=production
5. ✅ Usa HTTPS (Railway lo proporciona automáticamente)

## 📚 Recursos

- [Documentación de Railway](https://docs.railway.app/)
- [Railway Discord](https://discord.gg/railway)
- [Railway Status](https://status.railway.app/)

---

¡Listo para desplegar! 🚀

