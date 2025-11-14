import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de Base de Datos
# Todas las variables deben estar definidas en el archivo .env
# Soporta variables de Railway automáticamente (MYSQL_HOST, MYSQLHOST, etc.)
# Si no están definidas, la aplicación fallará con un error claro
db_host = os.getenv('DB_HOST') or os.getenv('MYSQL_HOST') or os.getenv('MYSQLHOST')
db_port = os.getenv('DB_PORT') or os.getenv('MYSQL_PORT') or os.getenv('MYSQLPORT')
db_user = os.getenv('DB_USER') or os.getenv('MYSQL_USER') or os.getenv('MYSQLUSER')
db_password = os.getenv('DB_PASS') or os.getenv('DB_PASSWORD') or os.getenv('MYSQL_PASSWORD') or os.getenv('MYSQLPASSWORD')
db_database = os.getenv('DB_NAME') or os.getenv('DB_DATABASE') or os.getenv('MYSQL_DATABASE') or os.getenv('MYSQLDATABASE')

# Validar que las variables críticas estén configuradas
if not db_host:
    raise ValueError("DB_HOST o MYSQL_HOST debe estar configurado en el archivo .env o variables de entorno")
if not db_user:
    raise ValueError("DB_USER o MYSQL_USER debe estar configurado en el archivo .env o variables de entorno")
if not db_database:
    raise ValueError("DB_NAME o MYSQL_DATABASE debe estar configurado en el archivo .env o variables de entorno")
if not db_port:
    raise ValueError("DB_PORT o MYSQL_PORT debe estar configurado en el archivo .env o variables de entorno")

DB_CONFIG = {
    'host': db_host,
    'port': int(db_port),
    'user': db_user,
    'password': db_password or '',
    'database': db_database,
    'autocommit': True
}

# Configuración de Seguridad
SECRET_KEY = os.getenv('SECRET_KEY') or os.getenv('SESSION_SECRET') 
ALGORITHM = os.getenv('ALGORITHM', 'HS256')

# Configuración de la aplicación
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
ENVIRONMENT = os.getenv('ENVIRONMENT') or os.getenv('RAILWAY_ENVIRONMENT', 'development')

