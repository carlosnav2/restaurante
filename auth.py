from passlib.context import CryptContext
from fastapi import Request
from database import get_db_connection
import warnings
import os

# Desactivar detección automática de bugs en bcrypt que causa problemas con versiones nuevas
# Esta variable debe estar antes de importar passlib
os.environ.setdefault('PASSLIB_DISABLE_WRAP_BUG_DETECTION', '1')

# Suprimir warnings de bcrypt durante la inicialización
warnings.filterwarnings("ignore", category=UserWarning, module="passlib")

# Inicializar contexto de contraseñas
# Usar sha256_crypt como esquema principal ya que es el que funciona correctamente
# y es compatible con los hashes existentes en la base de datos
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"Error verificando contraseña: {e}")
        return False

def get_password_hash(password: str) -> str:
    """Genera un hash de la contraseña usando sha256_crypt"""
    try:
        return pwd_context.hash(password)
    except Exception as e:
        print(f"Error hasheando contraseña: {e}")
        raise

def authenticate_user(username: str, password: str) -> dict:
    """Autentica un usuario y retorna sus datos"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute(
            "SELECT id, password, nombre, rol FROM usuarios WHERE username = %s AND activo = 1",
            (username,)
        )
        user = cursor.fetchone()
        
        if user and verify_password(password, user['password']):
            return {
                'id': user['id'],
                'username': username,
                'nombre': user['nombre'],
                'rol': user['rol']
            }
        return None
    except Exception as e:
        print(f"Error en autenticación: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def get_current_user(request: Request) -> dict:
    """Obtiene el usuario actual de la sesión"""
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute(
            "SELECT id, username, nombre, rol FROM usuarios WHERE id = %s AND activo = 1",
            (user_id,)
        )
        user = cursor.fetchone()
        return user
    finally:
        cursor.close()
        conn.close()

def require_role(required_role: str = None):
    """Decorador para requerir autenticación y rol específico"""
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            user = get_current_user(request)
            if not user:
                from fastapi.responses import RedirectResponse
                return RedirectResponse(url="/login", status_code=302)
            
            if required_role and user['rol'] != required_role:
                from fastapi.responses import RedirectResponse
                return RedirectResponse(url="/pos", status_code=302)
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator
