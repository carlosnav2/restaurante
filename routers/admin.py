from fastapi import APIRouter, Request, Form, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from auth import get_current_user, get_password_hash
from database import get_db_connection
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services import (
    get_products, get_admin_stats, get_recent_orders,
    get_product_by_id
)

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def require_admin(request: Request):
    """Verifica que el usuario sea admin"""
    user = get_current_user(request)
    if not user or user['rol'] != 'admin':
        return None
    return user

@router.get("/admin", response_class=HTMLResponse)
async def admin_view(request: Request):
    """Vista de administración"""
    user = require_admin(request)
    if not user:
        return RedirectResponse(url="/pos", status_code=302)
    
    stats = get_admin_stats()
    recent_orders = get_recent_orders(10)
    products = get_products(active_only=False)
    stats['tiempo_promedio'] = int(stats['tiempo_promedio'] / 60) if stats['tiempo_promedio'] else 0
    
    # Obtener usuarios
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios ORDER BY nombre")
    usuarios = cursor.fetchall()
    
    # Obtener todos los descuentos
    cursor.execute("SELECT * FROM descuentos ORDER BY codigo")
    descuentos = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Agrupar productos por categoría
    categorias = {}
    for prod in products:
        cat = prod['categoria']
        if cat not in categorias:
            categorias[cat] = []
        categorias[cat].append(prod)
    
    # Manejar acciones de formularios
    action = request.query_params.get('action', '')
    editing_product = None
    editing_user = None
    
    if action == 'edit_product_form' and 'id' in request.query_params:
        editing_product = get_product_by_id(int(request.query_params['id']))
    
    if action == 'edit_user_form' and 'id' in request.query_params:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE id = %s", (int(request.query_params['id']),))
        editing_user = cursor.fetchone()
        cursor.close()
        conn.close()
    
    show_add_form = action == 'add_product_form'
    show_add_user_form = action == 'add_user_form'
    
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "user": user,
        "stats": stats,
        "recent_orders": recent_orders,
        "categorias": categorias,
        "products": products,
        "usuarios": usuarios,
        "descuentos": descuentos,
        "editing_product": editing_product,
        "editing_user": editing_user,
        "show_add_form": show_add_form,
        "show_add_user_form": show_add_user_form,
        "action": action
    })

@router.post("/admin/add_product")
async def add_product(request: Request, nombre: str = Form(...), precio: float = Form(...), categoria: str = Form(...)):
    """Agrega un producto"""
    user = require_admin(request)
    if not user:
        return RedirectResponse(url="/pos", status_code=302)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO productos (nombre, precio, categoria) VALUES (%s, %s, %s)",
        (nombre, precio, categoria)
    )
    conn.commit()
    cursor.close()
    conn.close()
    
    return RedirectResponse(url="/admin", status_code=302)

@router.post("/admin/edit_product")
async def edit_product(request: Request, id: int = Form(...), nombre: str = Form(...), 
                      precio: float = Form(...), categoria: str = Form(...)):
    """Edita un producto"""
    user = require_admin(request)
    if not user:
        return RedirectResponse(url="/pos", status_code=302)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE productos SET nombre = %s, precio = %s, categoria = %s WHERE id = %s",
        (nombre, precio, categoria, id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    
    return RedirectResponse(url="/admin", status_code=302)

@router.get("/admin/delete_product")
async def delete_product(request: Request, id: int = Query(...)):
    """Elimina (desactiva) un producto"""
    user = require_admin(request)
    if not user:
        return RedirectResponse(url="/pos", status_code=302)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE productos SET activo = 0 WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    return RedirectResponse(url="/admin", status_code=302)

@router.post("/admin/add_user")
async def add_user(request: Request, username: str = Form(...), password: str = Form(...),
                  nombre: str = Form(...), rol: str = Form(...)):
    """Agrega un usuario"""
    user = require_admin(request)
    if not user:
        return RedirectResponse(url="/pos", status_code=302)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_password = get_password_hash(password)
    cursor.execute(
        "INSERT INTO usuarios (username, password, nombre, rol) VALUES (%s, %s, %s, %s)",
        (username, hashed_password, nombre, rol)
    )
    conn.commit()
    cursor.close()
    conn.close()
    
    return RedirectResponse(url="/admin", status_code=302)

@router.post("/admin/edit_user")
async def edit_user(request: Request, id: int = Form(...), username: str = Form(...),
                   nombre: str = Form(...), rol: str = Form(...), password: str = Form(None)):
    """Edita un usuario"""
    user = require_admin(request)
    if not user:
        return RedirectResponse(url="/pos", status_code=302)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if password:
        hashed_password = get_password_hash(password)
        cursor.execute(
            "UPDATE usuarios SET username = %s, password = %s, nombre = %s, rol = %s WHERE id = %s",
            (username, hashed_password, nombre, rol, id)
        )
    else:
        cursor.execute(
            "UPDATE usuarios SET username = %s, nombre = %s, rol = %s WHERE id = %s",
            (username, nombre, rol, id)
        )
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return RedirectResponse(url="/admin", status_code=302)

@router.get("/admin/delete_user")
async def delete_user(request: Request, id: int = Query(...)):
    """Elimina (desactiva) un usuario"""
    user = require_admin(request)
    if not user:
        return RedirectResponse(url="/pos", status_code=302)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE usuarios SET activo = 0 WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    return RedirectResponse(url="/admin", status_code=302)

