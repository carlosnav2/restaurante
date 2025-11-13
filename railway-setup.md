# 🚂 Guía de Despliegue en Railway

Esta guía te ayudará a desplegar el Sistema de Pedidos en Railway.

## 📋 Requisitos Previos

1. Cuenta en [Railway](https://railway.app)
2. Git instalado
3. Repositorio Git (GitHub, GitLab, o Bitbucket)

## 🚀 Pasos para Desplegar

### Opción 1: Desde GitHub/GitLab (Recomendado)

1. **Sube tu código a un repositorio Git:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <tu-repositorio-url>
   git push -u origin main
   ```

2. **Conecta Railway con tu repositorio:**
   - Ve a [Railway Dashboard](https://railway.app/dashboard)
   - Haz clic en "New Project"
   - Selecciona "Deploy from GitHub repo"
   - Autoriza Railway y selecciona tu repositorio
   - Railway detectará automáticamente el Dockerfile

3. **Configura la Base de Datos MySQL:**
   - En el proyecto de Railway, haz clic en "+ New"
   - Selecciona "Database" → "Add MySQL"
   - Railway creará automáticamente una base de datos MySQL

4. **Configura las Variables de Entorno:**
   - En tu servicio web, ve a "Variables"
   - Agrega las siguientes variables:
     ```
     DB_HOST=<MYSQLHOST> (Railway lo proporciona automáticamente)
     DB_USER=<MYSQLUSER> (Railway lo proporciona automáticamente)
     DB_PASS=<MYSQLPASSWORD> (Railway lo proporciona automáticamente)
     DB_NAME=<MYSQLDATABASE> (Railway lo proporciona automáticamente)
     PORT=80
     ```
   - **Importante:** Railway proporciona estas variables automáticamente cuando agregas MySQL. Solo necesitas referenciarlas.

5. **Conecta la Base de Datos al Servicio Web:**
   - En el servicio web, ve a "Settings"
   - En "Service Settings", conecta el servicio MySQL que creaste
   - Railway inyectará automáticamente las variables `MYSQLHOST`, `MYSQLUSER`, `MYSQLPASSWORD`, `MYSQLDATABASE`

6. **Configura las Variables de Entorno Correctamente:**
   - Agrega estas variables en tu servicio web:
     ```
     DB_HOST=${{MySQL.MYSQLHOST}}
     DB_USER=${{MySQL.MYSQLUSER}}
     DB_PASS=${{MySQL.MYSQLPASSWORD}}
     DB_NAME=${{MySQL.MYSQLDATABASE}}
     ```
   - O usa los nombres directos que Railway proporciona

### Opción 2: Desde CLI de Railway

1. **Instala Railway CLI:**
   ```bash
   npm i -g @railway/cli
   ```

2. **Inicia sesión:**
   ```bash
   railway login
   ```

3. **Inicializa el proyecto:**
   ```bash
   railway init
   ```

4. **Agrega MySQL:**
   ```bash
   railway add mysql
   ```

5. **Despliega:**
   ```bash
   railway up
   ```

## 🔧 Configuración de Variables de Entorno en Railway

Railway proporciona variables automáticas para MySQL. Configura estas en tu servicio web:

### Método 1: Usando Referencias de Servicio (Recomendado)
```
DB_HOST=${{MySQL.MYSQLHOST}}
DB_USER=${{MySQL.MYSQLUSER}}
DB_PASS=${{MySQL.MYSQLPASSWORD}}
DB_NAME=${{MySQL.MYSQLDATABASE}}
```

### Método 2: Usando Variables Directas
Si Railway no inyecta automáticamente, busca en el servicio MySQL las variables:
- `MYSQLHOST`
- `MYSQLUSER`
- `MYSQLPASSWORD`
- `MYSQLDATABASE`

Y cópialas manualmente a tu servicio web.

## 🌐 Obtener la URL de tu Aplicación

1. En Railway Dashboard, ve a tu servicio web
2. Haz clic en "Settings"
3. En "Networking", verás "Generate Domain"
4. Haz clic para generar un dominio público
5. Tu aplicación estará disponible en: `https://tu-proyecto.railway.app`

## ✅ Verificar el Despliegue

1. Visita la URL de tu aplicación
2. Deberías ver la pantalla de login
3. Usa las credenciales:
   - **Admin:** `admin` / `admin123`
   - **Mesero:** `mesero` / `mesero123`

## 🔍 Solución de Problemas

### Error: "Connection refused" a la base de datos
- Verifica que las variables de entorno estén correctamente configuradas
- Asegúrate de que el servicio MySQL esté conectado al servicio web
- Espera unos minutos después de crear MySQL para que se inicialice

### Error: Puerto no disponible
- Railway maneja los puertos automáticamente
- El Dockerfile ya está configurado para usar la variable `PORT`

### La aplicación no carga
- Revisa los logs en Railway Dashboard
- Verifica que el build se haya completado correctamente
- Asegúrate de que el Dockerfile esté en la raíz del proyecto

### Base de datos no se crea automáticamente
- El código PHP crea la base de datos si no existe
- Si hay problemas, verifica los permisos del usuario MySQL

## 📝 Notas Importantes

- Railway asigna puertos dinámicamente, el Dockerfile ya está configurado para esto
- Los datos de MySQL se persisten automáticamente en Railway
- Los cambios en el código se despliegan automáticamente si usas GitHub
- Railway ofrece un plan gratuito con límites generosos

## 🔄 Actualizar la Aplicación

Si usas GitHub:
- Haz `git push` y Railway desplegará automáticamente

Si usas CLI:
```bash
railway up
```

## 💰 Costos

Railway ofrece:
- **Plan Hobby:** Gratis con $5 de crédito mensual
- **Plan Pro:** $20/mes con más recursos

Para este proyecto, el plan gratuito debería ser suficiente.

