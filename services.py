from typing import List, Dict, Optional
from database import get_db_connection
from models import Producto, Pedido, PedidoItem, Descuento
from datetime import datetime
import random

def get_products(active_only: bool = True) -> List[Dict]:
    """Obtiene todos los productos"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        if active_only:
            cursor.execute("SELECT * FROM productos WHERE activo = 1 ORDER BY categoria, nombre")
        else:
            cursor.execute("SELECT * FROM productos ORDER BY categoria, nombre")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def get_product_by_id(product_id: int) -> Optional[Dict]:
    """Obtiene un producto por ID"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM productos WHERE id = %s", (product_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

def calculate_cart_total(cart: List[int]) -> float:
    """Calcula el total del carrito"""
    total = 0.0
    for item_id in cart:
        product = get_product_by_id(item_id)
        if product:
            total += float(product['precio'])
    return total

def apply_discount(total: float, discount_code: Optional[str] = None) -> Dict:
    """Aplica un descuento si existe el código"""
    if not discount_code:
        return {'total': total, 'discount': 0, 'discount_info': None}
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute(
            "SELECT * FROM descuentos WHERE codigo = %s AND activo = 1",
            (discount_code.upper(),)
        )
        discount = cursor.fetchone()
        
        if not discount:
            return {'total': total, 'discount': 0, 'discount_info': None}
        
        discount_amount = 0.0
        if discount['tipo'] == 'porcentaje':
            discount_amount = total * (float(discount['valor']) / 100)
        else:
            discount_amount = float(discount['valor'])
        
        discount_amount = min(discount_amount, total)
        
        return {
            'total': total - discount_amount,
            'discount': discount_amount,
            'discount_info': discount
        }
    finally:
        cursor.close()
        conn.close()

def get_grouped_cart(cart: List[int]) -> Dict:
    """Agrupa los items del carrito por producto"""
    grouped = {}
    for item_id in cart:
        product = get_product_by_id(item_id)
        if product:
            name = product['nombre']
            if name not in grouped:
                grouped[name] = {'product': product, 'quantity': 0}
            grouped[name]['quantity'] += 1
    return grouped

def create_order(cart: List[int], subtotal: float, discount_code: Optional[str] = None) -> int:
    """Crea un nuevo pedido"""
    discount_info = apply_discount(subtotal, discount_code)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Generar número de pedido
        numero_pedido = f"P{datetime.now().strftime('%Y%m%d')}-{str(random.randint(1, 9999)).zfill(4)}"
        
        # Crear pedido
        cursor.execute(
            "INSERT INTO pedidos (numero_pedido, total, descuento, total_final) VALUES (%s, %s, %s, %s)",
            (numero_pedido, subtotal, discount_info['discount'], discount_info['total'])
        )
        pedido_id = cursor.lastrowid
        
        # Guardar items
        grouped = get_grouped_cart(cart)
        for name, data in grouped.items():
            product = data['product']
            cursor.execute(
                "INSERT INTO pedido_items (pedido_id, producto_id, producto_nombre, precio, cantidad) VALUES (%s, %s, %s, %s, %s)",
                (pedido_id, product['id'], product['nombre'], product['precio'], data['quantity'])
            )
        
        conn.commit()
        return pedido_id
    finally:
        cursor.close()
        conn.close()

def get_order_by_id(order_id: int) -> Optional[Dict]:
    """Obtiene un pedido por ID"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM pedidos WHERE id = %s", (order_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

def get_order_items(order_id: int) -> List[Dict]:
    """Obtiene los items de un pedido"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM pedido_items WHERE pedido_id = %s", (order_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def update_order_status(order_id: int, new_status: str):
    """Actualiza el estado de un pedido"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if new_status == 'ready':
            # Obtener fecha del pedido
            cursor.execute("SELECT fecha_hora FROM pedidos WHERE id = %s", (order_id,))
            order_row = cursor.fetchone()
            if order_row and order_row[0]:
                tiempo = int((datetime.now() - order_row[0]).total_seconds())
                cursor.execute(
                    "UPDATE pedidos SET estado = %s, tiempo_preparacion = %s WHERE id = %s",
                    (new_status, tiempo, order_id)
                )
            else:
                cursor.execute(
                    "UPDATE pedidos SET estado = %s WHERE id = %s",
                    (new_status, order_id)
                )
        else:
            cursor.execute(
                "UPDATE pedidos SET estado = %s WHERE id = %s",
                (new_status, order_id)
            )
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def get_active_orders() -> List[Dict]:
    """Obtiene pedidos activos (no entregados)"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM pedidos WHERE estado != 'delivered' ORDER BY fecha_hora ASC")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def get_admin_stats() -> Dict:
    """Obtiene estadísticas para el panel de administración"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT
                COUNT(*) as total_pedidos,
                COALESCE(SUM(total_final), 0) as ventas_totales,
                COALESCE(AVG(tiempo_preparacion), 0) as tiempo_promedio,
                SUM(CASE WHEN estado = 'preparing' THEN 1 ELSE 0 END) as en_preparacion
            FROM pedidos
            WHERE DATE(fecha_hora) = CURDATE()
        """)
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

def get_recent_orders(limit: int = 10) -> List[Dict]:
    """Obtiene pedidos recientes"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM pedidos ORDER BY fecha_hora DESC LIMIT %s", (limit,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

