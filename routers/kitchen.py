from fastapi import APIRouter, Request, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from auth import get_current_user
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services import get_active_orders, get_order_items, update_order_status

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/kitchen", response_class=HTMLResponse)
async def kitchen_view(request: Request):
    """Vista de cocina"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    orders = get_active_orders()
    
    # Agregar items a cada pedido
    for order in orders:
        order['items'] = get_order_items(order['id'])
    
    return templates.TemplateResponse("kitchen.html", {
        "request": request,
        "user": user,
        "orders": orders
    })

@router.get("/kitchen/status")
async def change_status(request: Request, order_id: int = Query(...), new_status: str = Query(...)):
    """Cambia el estado de un pedido"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    update_order_status(order_id, new_status)
    return RedirectResponse(url="/kitchen", status_code=302)

