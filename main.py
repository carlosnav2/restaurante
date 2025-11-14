from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
from config import SECRET_KEY
import os

# Importar routers
from routers import auth, pos, kitchen, admin, ticket, users, reports, products, discounts

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestiona el ciclo de vida de la aplicación"""
    # Startup
    print("🚀 Aplicación iniciada")
    print("📝 NOTA: La base de datos debe inicializarse manualmente usando: python init_db.py")
    yield
    # Shutdown (si es necesario)
    print("🛑 Aplicación cerrada")

# Crear aplicación con lifespan
app = FastAPI(title="Sistema de Pedidos - Restaurante Sazón Mexicano", lifespan=lifespan)

# Configurar sesiones
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Configurar templates
templates = Jinja2Templates(directory="templates")

# Incluir routers
app.include_router(auth.router)
app.include_router(pos.router)
app.include_router(kitchen.router)
app.include_router(admin.router)
app.include_router(ticket.router)
app.include_router(users.router)
app.include_router(reports.router)
app.include_router(products.router)
app.include_router(discounts.router)

@app.get("/")
async def root(request: Request):
    """Redirige a la vista apropiada"""
    if request.session.get('user_id'):
        return RedirectResponse(url="/pos", status_code=302)
    return RedirectResponse(url="/login", status_code=302)

if __name__ == "__main__":
    import uvicorn
    import os
    # Obtener puerto de variable de entorno (Railway usa PORT)
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
