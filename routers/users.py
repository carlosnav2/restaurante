from fastapi import APIRouter, Request, Form, Query
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from auth import get_current_user, get_password_hash
from database import get_db_connection
from decimal import Decimal
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def convert_decimals(obj):
    """Convierte objetos Decimal a float para JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    return obj

def require_admin(request: Request):
    """Verifica que el usuario sea admin"""
    user = get_current_user(request)
    if not user or user['rol'] != 'admin':
        return None
    return user

def get_all_users(search: str = None, role: str = None, active: str = None):
    """Obtiene todos los usuarios con filtros opcionales"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = "SELECT * FROM usuarios WHERE 1=1"
    params = []
    
    if search:
        query += " AND (nombre LIKE %s OR username LIKE %s)"
        search_param = f"%{search}%"
        params.extend([search_param, search_param])
    
    if role:
        query += " AND rol = %s"
        params.append(role)
    
    if active is not None:
        if active == 'true':
            query += " AND activo = 1"
        elif active == 'false':
            query += " AND activo = 0"
    
    query += " ORDER BY nombre"
    
    cursor.execute(query, params)
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Convertir datetime a string para JSON
    for user in users:
        if user.get('created_at'):
            user['created_at'] = user['created_at'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(user['created_at'], 'strftime') else str(user['created_at'])
    
    users = convert_decimals(users)
    return users

def get_user_by_id(user_id: int):
    """Obtiene un usuario por ID"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user:
        if user.get('created_at'):
            user['created_at'] = user['created_at'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(user['created_at'], 'strftime') else str(user['created_at'])
        user = convert_decimals(user)
    return user

def username_exists(username: str, exclude_id: int = None):
    """Verifica si un username ya existe"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if exclude_id:
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE username = %s AND id != %s", (username, exclude_id))
    else:
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE username = %s", (username,))
    
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count > 0

@router.get("/api/users")
async def get_users_api(request: Request, 
                       search: str = Query(None),
                       role: str = Query(None),
                       active: str = Query(None)):
    """API para obtener usuarios"""
    user = require_admin(request)
    if not user:
        return JSONResponse({"success": False, "error": "No autorizado"}, status_code=403)
    
    try:
        users = get_all_users(search, role, active)
        return JSONResponse({"success": True, "users": users})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@router.get("/api/users/{user_id}")
async def get_user_api(request: Request, user_id: int):
    """API para obtener un usuario específico"""
    user = require_admin(request)
    if not user:
        return JSONResponse({"success": False, "error": "No autorizado"}, status_code=403)
    
    try:
        user_data = get_user_by_id(user_id)
        if not user_data:
            return JSONResponse({"success": False, "error": "Usuario no encontrado"}, status_code=404)
        return JSONResponse({"success": True, "user": user_data})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@router.post("/api/users")
async def create_user_api(request: Request, 
                         username: str = Form(...), 
                         password: str = Form(...),
                         nombre: str = Form(...), 
                         rol: str = Form(...)):
    """API para crear un usuario"""
    user = require_admin(request)
    if not user:
        return JSONResponse({"success": False, "error": "No autorizado"}, status_code=403)
    
    # Validaciones
    if not username or not password or not nombre or not rol:
        return JSONResponse({"success": False, "error": "Faltan campos obligatorios"}, status_code=400)
    
    if len(password) < 6:
        return JSONResponse({"success": False, "error": "La contraseña debe tener al menos 6 caracteres"}, status_code=400)
    
    if rol not in ['admin', 'mesero']:
        return JSONResponse({"success": False, "error": "Rol inválido"}, status_code=400)
    
    if username_exists(username):
        return JSONResponse({"success": False, "error": "El usuario ya existe"}, status_code=400)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        hashed_password = get_password_hash(password)
        cursor.execute(
            "INSERT INTO usuarios (username, password, nombre, rol) VALUES (%s, %s, %s, %s)",
            (username, hashed_password, nombre, rol)
        )
        conn.commit()
        user_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        new_user = get_user_by_id(user_id)
        return JSONResponse({"success": True, "message": "Usuario creado exitosamente", "user": new_user})
    except Exception as e:
        return JSONResponse({"success": False, "error": f"Error al crear usuario: {str(e)}"}, status_code=500)

@router.put("/api/users/{user_id}")
async def update_user_api(request: Request, user_id: int,
                         username: str = Form(...),
                         nombre: str = Form(...), 
                         rol: str = Form(...), 
                         password: str = Form(None)):
    """API para actualizar un usuario"""
    user = require_admin(request)
    if not user:
        return JSONResponse({"success": False, "error": "No autorizado"}, status_code=403)
    
    # Validaciones
    if not username or not nombre or not rol:
        return JSONResponse({"success": False, "error": "Faltan campos obligatorios"}, status_code=400)
    
    if rol not in ['admin', 'mesero']:
        return JSONResponse({"success": False, "error": "Rol inválido"}, status_code=400)
    
    if password and len(password) < 6:
        return JSONResponse({"success": False, "error": "La contraseña debe tener al menos 6 caracteres"}, status_code=400)
    
    existing_user = get_user_by_id(user_id)
    if not existing_user:
        return JSONResponse({"success": False, "error": "Usuario no encontrado"}, status_code=404)
    
    if username_exists(username, exclude_id=user_id):
        return JSONResponse({"success": False, "error": "El usuario ya existe"}, status_code=400)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if password:
            hashed_password = get_password_hash(password)
            cursor.execute(
                "UPDATE usuarios SET username = %s, password = %s, nombre = %s, rol = %s WHERE id = %s",
                (username, hashed_password, nombre, rol, user_id)
            )
        else:
            cursor.execute(
                "UPDATE usuarios SET username = %s, nombre = %s, rol = %s WHERE id = %s",
                (username, nombre, rol, user_id)
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        updated_user = get_user_by_id(user_id)
        return JSONResponse({"success": True, "message": "Usuario actualizado exitosamente", "user": updated_user})
    except Exception as e:
        return JSONResponse({"success": False, "error": f"Error al actualizar usuario: {str(e)}"}, status_code=500)

@router.delete("/api/users/{user_id}")
async def delete_user_api(request: Request, user_id: int):
    """API para desactivar un usuario"""
    user = require_admin(request)
    if not user:
        return JSONResponse({"success": False, "error": "No autorizado"}, status_code=403)
    
    if user['id'] == user_id:
        return JSONResponse({"success": False, "error": "No puedes desactivar tu propio usuario"}, status_code=400)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET activo = 0 WHERE id = %s", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        return JSONResponse({"success": True, "message": "Usuario desactivado exitosamente"})
    except Exception as e:
        return JSONResponse({"success": False, "error": f"Error al desactivar usuario: {str(e)}"}, status_code=500)

@router.post("/api/users/{user_id}/activate")
async def activate_user_api(request: Request, user_id: int):
    """API para activar un usuario"""
    user = require_admin(request)
    if not user:
        return JSONResponse({"success": False, "error": "No autorizado"}, status_code=403)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET activo = 1 WHERE id = %s", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        return JSONResponse({"success": True, "message": "Usuario activado exitosamente"})
    except Exception as e:
        return JSONResponse({"success": False, "error": f"Error al activar usuario: {str(e)}"}, status_code=500)
