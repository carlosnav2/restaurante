# 🔧 Solución de Problemas - Railway

## Problema: Healthcheck Failed

### Síntomas
```
Healthcheck failed!
1/1 replicas never became healthy!
```

### Soluciones

#### 1. Verificar que el puerto esté configurado correctamente

Railway asigna automáticamente la variable `PORT`. El script `start.sh` debería configurar Apache automáticamente.

**Verificar en Railway:**
- Ve a tu servicio → Variables
- Asegúrate de que `PORT` esté disponible (Railway la inyecta automáticamente)

#### 2. Revisar los logs

En Railway Dashboard:
1. Ve a tu servicio
2. Haz clic en "Deployments"
3. Selecciona el deployment más reciente
4. Revisa los logs para ver errores

**Busca mensajes como:**
- "Starting Apache on port: XXX"
- "Apache configured for port: XXX"
- Errores de conexión a la base de datos

#### 3. Verificar la conexión a MySQL

Si ves errores de conexión a la base de datos:

1. **Verifica que MySQL esté conectado:**
   - En tu servicio web → Settings
   - Verifica que el servicio MySQL esté en "Connected Services"

2. **Verifica las variables de entorno:**
   - Railway inyecta automáticamente: `MYSQLHOST`, `MYSQLUSER`, `MYSQLPASSWORD`, `MYSQLDATABASE`
   - El código PHP las detecta automáticamente

3. **Espera a que MySQL se inicialice:**
   - MySQL puede tardar 1-2 minutos en inicializarse
   - Revisa los logs del servicio MySQL

#### 4. Reconstruir el servicio

Si el problema persiste:

1. **En Railway Dashboard:**
   - Ve a tu servicio
   - Haz clic en "Settings"
   - Scroll down y haz clic en "Redeploy"

2. **O desde CLI:**
   ```bash
   railway up
   ```

#### 5. Verificar el Dockerfile

Asegúrate de que el Dockerfile esté en la raíz del proyecto y contenga:

```dockerfile
COPY start.sh /start.sh
RUN chmod +x /start.sh
```

#### 6. Verificar que start.sh esté en el repositorio

```bash
git add start.sh
git commit -m "Add start.sh"
git push
```

## Problema: Error de Conexión a Base de Datos

### Síntomas
- La aplicación carga pero muestra errores de conexión
- No se pueden crear pedidos

### Soluciones

1. **Verificar variables de entorno:**
   - En Railway → Tu servicio web → Variables
   - Deberías ver las variables MySQL automáticamente

2. **Conectar MySQL manualmente:**
   - Ve a tu servicio web → Settings
   - En "Connected Services", conecta el servicio MySQL

3. **Verificar que MySQL esté corriendo:**
   - Ve al servicio MySQL
   - Verifica que el estado sea "Active"

## Problema: La aplicación no carga

### Soluciones

1. **Verificar el dominio:**
   - Ve a Settings → Networking
   - Genera un dominio si no tienes uno

2. **Verificar los logs:**
   - Revisa los logs del servicio para errores de PHP

3. **Verificar permisos:**
   - El Dockerfile ya configura los permisos correctamente
   - Si hay problemas, verifica los logs

## Problema: Cambios no se reflejan

### Soluciones

1. **Verificar que el código esté en Git:**
   ```bash
   git status
   git add .
   git commit -m "Update"
   git push
   ```

2. **Railway despliega automáticamente:**
   - Si usas GitHub, Railway detecta los cambios automáticamente
   - Puede tardar 1-2 minutos en desplegar

3. **Forzar redeploy:**
   - En Railway → Settings → Redeploy

## Comandos Útiles

### Ver logs en tiempo real
```bash
railway logs
```

### Conectar a la base de datos
```bash
railway connect mysql
```

### Ver variables de entorno
```bash
railway variables
```

## Contacto y Soporte

Si el problema persiste:
1. Revisa los logs completos en Railway
2. Verifica que todos los archivos estén en el repositorio
3. Asegúrate de que MySQL esté conectado al servicio web

