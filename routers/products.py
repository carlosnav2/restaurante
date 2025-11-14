from fastapi import APIRouter, Request, Form, Query
from fastapi.responses import JSONResponse
from auth import get_current_user
from database import get_db_connection
from decimal import Decimal
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

router = APIRouter()

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

@router.get("/api/products")
async def get_products_api(request: Request, 
                           category: str = Query(None),
                           active: str = Query(None)):
    """API para obtener productos"""
    user = require_admin(request)
    if not user:
        return JSONResponse({"success": False, "error": "No autorizado"}, status_code=403)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM productos WHERE 1=1"
        params = []
        
        if category:
            query += " AND categoria = %s"
            params.append(category)
        
        if active is not None:
            if active == 'true':
                query += " AND activo = 1"
            elif active == 'false':
                query += " AND activo = 0"
        
        query += " ORDER BY categoria, nombre"
        
        cursor.execute(query, params)
        products = cursor.fetchall()
        
        # Convertir datetime y Decimal
        for product in products:
            if product.get('created_at'):
                product['created_at'] = product['created_at'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(product['created_at'], 'strftime') else str(product['created_at'])
            if product.get('precio'):
                product['precio'] = float(product['precio']) if isinstance(product['precio'], Decimal) else product['precio']
        
        products = convert_decimals(products)
        cursor.close()
        conn.close()
        
        return JSONResponse({"success": True, "products": products})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@router.get("/api/products/{product_id}")
async def get_product_api(request: Request, product_id: int):
    """API para obtener un producto específico"""
    user = require_admin(request)
    if not user:
        return JSONResponse({"success": False, "error": "No autorizado"}, status_code=403)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not product:
            return JSONResponse({"success": False, "error": "Producto no encontrado"}, status_code=404)
        
        # Convertir datetime y Decimal
        if product.get('created_at'):
            product['created_at'] = product['created_at'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(product['created_at'], 'strftime') else str(product['created_at'])
        if product.get('precio'):
            product['precio'] = float(product['precio']) if isinstance(product['precio'], Decimal) else product['precio']
        
        product = convert_decimals(product)
        
        return JSONResponse({"success": True, "product": product})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@router.post("/api/products")
async def create_product_api(request: Request, 
                            nombre: str = Form(...), 
                            precio: float = Form(...),
                            categoria: str = Form(...)):
    """API para crear un producto"""
    user = require_admin(request)
    if not user:
        return JSONResponse({"success": False, "error": "No autorizado"}, status_code=403)
    
    # Validaciones
    if not nombre or not categoria:
        return JSONResponse({"success": False, "error": "Faltan campos obligatorios"}, status_code=400)
    
    if precio <= 0:
        return JSONResponse({"success": False, "error": "El precio debe ser mayor a 0"}, status_code=400)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO productos (nombre, precio, categoria) VALUES (%s, %s, %s)",
            (nombre, precio, categoria)
        )
        conn.commit()
        product_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        # Obtener el producto creado
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos WHERE id = %s", (product_id,))
        new_product = cursor.fetchone()
        cursor.close()
        conn.close()
        
        # Convertir Decimal
        if new_product.get('precio'):
            new_product['precio'] = float(new_product['precio']) if isinstance(new_product['precio'], Decimal) else new_product['precio']
        new_product = convert_decimals(new_product)
        
        return JSONResponse({"success": True, "message": "Producto creado exitosamente", "product": new_product})
    except Exception as e:
        return JSONResponse({"success": False, "error": f"Error al crear producto: {str(e)}"}, status_code=500)

@router.put("/api/products/{product_id}")
async def update_product_api(request: Request, product_id: int,
                            nombre: str = Form(...), 
                            precio: float = Form(...),
                            categoria: str = Form(...)):
    """API para actualizar un producto"""
    user = require_admin(request)
    if not user:
        return JSONResponse({"success": False, "error": "No autorizado"}, status_code=403)
    
    # Validaciones
    if not nombre or not categoria:
        return JSONResponse({"success": False, "error": "Faltan campos obligatorios"}, status_code=400)
    
    if precio <= 0:
        return JSONResponse({"success": False, "error": "El precio debe ser mayor a 0"}, status_code=400)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE productos SET nombre = %s, precio = %s, categoria = %s WHERE id = %s",
            (nombre, precio, categoria, product_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        # Obtener el producto actualizado
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos WHERE id = %s", (product_id,))
        updated_product = cursor.fetchone()
        cursor.close()
        conn.close()
        
        # Convertir Decimal
        if updated_product.get('precio'):
            updated_product['precio'] = float(updated_product['precio']) if isinstance(updated_product['precio'], Decimal) else updated_product['precio']
        updated_product = convert_decimals(updated_product)
        
        return JSONResponse({"success": True, "message": "Producto actualizado exitosamente", "product": updated_product})
    except Exception as e:
        return JSONResponse({"success": False, "error": f"Error al actualizar producto: {str(e)}"}, status_code=500)

@router.delete("/api/products/{product_id}")
async def delete_product_api(request: Request, product_id: int):
    """API para desactivar un producto"""
    user = require_admin(request)
    if not user:
        return JSONResponse({"success": False, "error": "No autorizado"}, status_code=403)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE productos SET activo = 0 WHERE id = %s", (product_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        return JSONResponse({"success": True, "message": "Producto desactivado exitosamente"})
    except Exception as e:
        return JSONResponse({"success": False, "error": f"Error al desactivar producto: {str(e)}"}, status_code=500)

@router.post("/api/products/{product_id}/activate")
async def activate_product_api(request: Request, product_id: int):
    """API para activar un producto"""
    user = require_admin(request)
    if not user:
        return JSONResponse({"success": False, "error": "No autorizado"}, status_code=403)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE productos SET activo = 1 WHERE id = %s", (product_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        return JSONResponse({"success": True, "message": "Producto activado exitosamente"})
    except Exception as e:
        return JSONResponse({"success": False, "error": f"Error al activar producto: {str(e)}"}, status_code=500)

