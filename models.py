from typing import Optional, List
from datetime import datetime
from dataclasses import dataclass

@dataclass
class Usuario:
    id: Optional[int] = None
    username: str = ""
    password: str = ""
    nombre: str = ""
    rol: str = ""
    activo: bool = True
    created_at: Optional[datetime] = None

@dataclass
class Producto:
    id: Optional[int] = None
    nombre: str = ""
    precio: float = 0.0
    categoria: str = ""
    activo: bool = True
    created_at: Optional[datetime] = None

@dataclass
class Pedido:
    id: Optional[int] = None
    numero_pedido: str = ""
    total: float = 0.0
    descuento: float = 0.0
    total_final: float = 0.0
    estado: str = "pending"
    fecha_hora: Optional[datetime] = None
    tiempo_preparacion: Optional[int] = None

@dataclass
class PedidoItem:
    id: Optional[int] = None
    pedido_id: int = 0
    producto_id: int = 0
    producto_nombre: str = ""
    precio: float = 0.0
    cantidad: int = 0

@dataclass
class Descuento:
    id: Optional[int] = None
    codigo: str = ""
    tipo: str = ""
    valor: float = 0.0
    activo: bool = True

