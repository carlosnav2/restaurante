from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from auth import get_current_user
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services import get_order_by_id, get_order_items

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/print", response_class=HTMLResponse)
async def print_ticket(request: Request, order_id: int = Query(...)):
    """Genera el ticket para imprimir"""
    user = get_current_user(request)
    if not user:
        return HTMLResponse("<html><body><h1>No autorizado</h1></body></html>")
    
    order = get_order_by_id(order_id)
    if not order:
        return HTMLResponse("<html><body><h1>Pedido no encontrado</h1></body></html>")
    
    items = get_order_items(order_id)
    
    return templates.TemplateResponse("ticket.html", {
        "request": request,
        "order": order,
        "items": items
    })

