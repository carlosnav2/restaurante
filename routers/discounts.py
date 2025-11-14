from fastapi import APIRouter, Request, Form, Query, HTTPException
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

def require_admin_api(request: Request):
    """Verifica que el usuario sea admin"""
    user = get_current_user(request)
    if not user or user['rol'] != 'admin':
        raise HTTPException(status_code=403, detail="No autorizado")
    return user

def get_all_discounts(search: str = None, active: str = None):
    """Obtiene todos los descuentos con filtros opcionales"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = "SELECT * FROM descuentos WHERE 1=1"
    params = []
    
    if search:
        query += " AND codigo LIKE %s"
        params.append(f"%{search}%")
    
    if active is not None:
        if active == 'true':
            query += " AND activo = 1"
        elif active == 'false':
            query += " AND activo = 0"
    
    query += " ORDER BY codigo"
    
    cursor.execute(query, params)
    discounts = cursor.fetchall()
    cursor.close()
    conn.close()
    
    discounts = convert_decimals(discounts)
    return discounts

def get_discount_by_id(discount_id: int):
    """Obtiene un descuento por ID"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM descuentos WHERE id = %s", (discount_id,))
    discount = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if discount:
        discount = convert_decimals(discount)
    return discount

def codigo_exists(codigo: str, exclude_id: int = None):
    """Verifica si un código de descuento ya existe"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if exclude_id:
        cursor.execute("SELECT COUNT(*) FROM descuentos WHERE codigo = %s AND id != %s", (codigo.upper(), exclude_id))
    else:
        cursor.execute("SELECT COUNT(*) FROM descuentos WHERE codigo = %s", (codigo.upper(),))
    
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    
    return count > 0

@router.get("/api/discounts", response_class=JSONResponse)
async def get_discounts_api(request: Request, search: str = None, active: str = None):
    """API para obtener todos los descuentos"""
    require_admin_api(request)
    discounts = get_all_discounts(search, active)
    return {"success": True, "discounts": discounts}

@router.get("/api/discounts/{discount_id}", response_class=JSONResponse)
async def get_discount_api(request: Request, discount_id: int):
    """API para obtener un descuento específico"""
    require_admin_api(request)
    discount = get_discount_by_id(discount_id)
    if not discount:
        raise HTTPException(status_code=404, detail="Descuento no encontrado")
    return {"success": True, "discount": discount}

@router.post("/api/discounts", response_class=JSONResponse)
async def add_discount_api(request: Request, codigo: str = Form(...), tipo: str = Form(...),
                           valor: float = Form(...)):
    """API para crear un nuevo descuento"""
    require_admin_api(request)
    
    # Validaciones
    if codigo_exists(codigo):
        return JSONResponse({"success": False, "error": "El código de descuento ya existe"}, status_code=400)
    
    if tipo not in ['porcentaje', 'fijo']:
        return JSONResponse({"success": False, "error": "El tipo debe ser 'porcentaje' o 'fijo'"}, status_code=400)
    
    if valor <= 0:
        return JSONResponse({"success": False, "error": "El valor debe ser mayor a 0"}, status_code=400)
    
    if tipo == 'porcentaje' and valor > 100:
        return JSONResponse({"success": False, "error": "El porcentaje no puede ser mayor a 100"}, status_code=400)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO descuentos (codigo, tipo, valor, activo) VALUES (%s, %s, %s, 1)",
            (codigo.upper().strip(), tipo, valor)
        )
        conn.commit()
        discount_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        # Obtener el descuento creado
        new_discount = get_discount_by_id(discount_id)
        
        return JSONResponse({"success": True, "message": "Descuento creado exitosamente", "discount": new_discount})
    except Exception as e:
        return JSONResponse({"success": False, "error": f"Error al crear descuento: {str(e)}"}, status_code=500)

@router.put("/api/discounts/{discount_id}", response_class=JSONResponse)
async def edit_discount_api(request: Request, discount_id: int, codigo: str = Form(...),
                            tipo: str = Form(...), valor: float = Form(...)):
    """API para actualizar un descuento"""
    require_admin_api(request)
    
    # Verificar que existe
    discount = get_discount_by_id(discount_id)
    if not discount:
        raise HTTPException(status_code=404, detail="Descuento no encontrado")
    
    # Validaciones
    if codigo_exists(codigo, discount_id):
        return JSONResponse({"success": False, "error": "El código de descuento ya existe"}, status_code=400)
    
    if tipo not in ['porcentaje', 'fijo']:
        return JSONResponse({"success": False, "error": "El tipo debe ser 'porcentaje' o 'fijo'"}, status_code=400)
    
    if valor <= 0:
        return JSONResponse({"success": False, "error": "El valor debe ser mayor a 0"}, status_code=400)
    
    if tipo == 'porcentaje' and valor > 100:
        return JSONResponse({"success": False, "error": "El porcentaje no puede ser mayor a 100"}, status_code=400)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE descuentos SET codigo = %s, tipo = %s, valor = %s WHERE id = %s",
            (codigo.upper().strip(), tipo, valor, discount_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        # Obtener el descuento actualizado
        updated_discount = get_discount_by_id(discount_id)
        
        return JSONResponse({"success": True, "message": "Descuento actualizado exitosamente", "discount": updated_discount})
    except Exception as e:
        return JSONResponse({"success": False, "error": f"Error al actualizar descuento: {str(e)}"}, status_code=500)

@router.delete("/api/discounts/{discount_id}", response_class=JSONResponse)
async def delete_discount_api(request: Request, discount_id: int):
    """API para desactivar un descuento"""
    require_admin_api(request)
    
    # Verificar que existe
    discount = get_discount_by_id(discount_id)
    if not discount:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Descuento no encontrado")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE descuentos SET activo = 0 WHERE id = %s", (discount_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        return JSONResponse({"success": True, "message": "Descuento desactivado correctamente"})
    except Exception as e:
        return JSONResponse({"success": False, "error": f"Error al desactivar descuento: {str(e)}"}, status_code=500)

@router.post("/api/discounts/{discount_id}/activate", response_class=JSONResponse)
async def activate_discount_api(request: Request, discount_id: int):
    """API para activar un descuento"""
    require_admin_api(request)
    
    # Verificar que existe
    discount = get_discount_by_id(discount_id)
    if not discount:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Descuento no encontrado")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE descuentos SET activo = 1 WHERE id = %s", (discount_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        return JSONResponse({"success": True, "message": "Descuento activado correctamente"})
    except Exception as e:
        return JSONResponse({"success": False, "error": f"Error al activar descuento: {str(e)}"}, status_code=500)

