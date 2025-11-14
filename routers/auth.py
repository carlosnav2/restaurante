from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth import authenticate_user
from database import init_database

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Muestra la página de login"""
    # Si ya está autenticado, redirigir
    if request.session.get('user_id'):
        return RedirectResponse(url="/pos", status_code=302)
    
    error = request.session.pop('login_error', None)
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": error
    })

@router.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Procesa el login"""
    user = authenticate_user(username, password)
    
    if user:
        request.session['user_id'] = user['id']
        request.session['user_name'] = user['nombre']
        request.session['user_role'] = user['rol']
        return RedirectResponse(url="/pos", status_code=302)
    else:
        request.session['login_error'] = 'Usuario o contraseña incorrectos'
        return RedirectResponse(url="/login", status_code=302)

@router.get("/logout")
async def logout(request: Request):
    """Cierra sesión"""
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)

