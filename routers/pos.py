from fastapi import APIRouter, Request, Form, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from auth import get_current_user
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services import (
    get_products, get_product_by_id, calculate_cart_total,
    apply_discount, get_grouped_cart, create_order
)

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_cart(request: Request) -> list:
    """Obtiene el carrito de la sesión"""
    if 'cart' not in request.session:
        request.session['cart'] = []
    return request.session['cart']

@router.get("/pos", response_class=HTMLResponse)
async def pos_view(request: Request):
    """Vista del sistema POS"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    cart = get_cart(request)
    products = get_products()
    subtotal = calculate_cart_total(cart)
    discount_code = request.session.get('discount_code')
    discount_info = apply_discount(subtotal, discount_code)
    show_success = 'success' in request.query_params
    
    # Agrupar productos por categoría
    categories = {}
    for product in products:
        cat = product['categoria']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(product)
    
    # Obtener items agrupados del carrito
    grouped_cart = get_grouped_cart(cart)
    cart_items_list = []
    for name, data in grouped_cart.items():
        cart_items_list.append({
            'name': name,
            'product': data['product'],
            'quantity': data['quantity']
        })
    
    return templates.TemplateResponse("pos.html", {
        "request": request,
        "user": user,
        "categories": categories,
        "cart": cart,
        "grouped_cart": grouped_cart,
        "cart_items_list": cart_items_list,
        "subtotal": subtotal,
        "discount_info": discount_info,
        "discount_code": discount_code,
        "show_success": show_success,
        "last_order_id": request.session.get('last_order_id')
    })

@router.get("/pos/add")
async def add_to_cart(request: Request, id: int = Query(...)):
    """Agrega un producto al carrito"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    cart = get_cart(request)
    product = get_product_by_id(id)
    
    if product:
        cart.append(id)
        request.session['cart'] = cart
    
    return RedirectResponse(url="/pos", status_code=302)

@router.get("/pos/remove")
async def remove_from_cart(request: Request, index: int = Query(...)):
    """Elimina un item del carrito"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    cart = get_cart(request)
    if 0 <= index < len(cart):
        cart.pop(index)
        request.session['cart'] = cart
    
    return RedirectResponse(url="/pos", status_code=302)

@router.get("/pos/clear")
async def clear_cart(request: Request):
    """Limpia el carrito"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    request.session['cart'] = []
    request.session['discount_code'] = None
    return RedirectResponse(url="/pos", status_code=302)

@router.post("/pos/apply_discount")
async def apply_discount_action(request: Request, discount_code: str = Form(...)):
    """Aplica un código de descuento"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    request.session['discount_code'] = discount_code.upper().strip()
    return RedirectResponse(url="/pos", status_code=302)

@router.get("/pos/remove_discount")
async def remove_discount(request: Request):
    """Quita el descuento aplicado"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    request.session['discount_code'] = None
    return RedirectResponse(url="/pos", status_code=302)

@router.get("/pos/confirm")
async def confirm_order(request: Request):
    """Confirma el pedido"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    cart = get_cart(request)
    if not cart:
        return RedirectResponse(url="/pos", status_code=302)
    
    subtotal = calculate_cart_total(cart)
    discount_code = request.session.get('discount_code')
    
    order_id = create_order(cart, subtotal, discount_code)
    
    # Limpiar carrito
    request.session['cart'] = []
    request.session['discount_code'] = None
    request.session['last_order_id'] = order_id
    
    return RedirectResponse(url="/pos?success=1", status_code=302)

