#!/usr/bin/env python3
"""
Script para inicializar la base de datos
Sistema de Pedidos - Restaurante Sazón Mexicano

Uso:
    python init_db.py

Este script debe ejecutarse una vez antes de iniciar la aplicación,
especialmente cuando se despliega en Railway u otros servicios en la nube.
"""

import sys
from database import init_database

def main():
    """Inicializa la base de datos"""
    print("=" * 60)
    print("Inicialización de Base de Datos")
    print("Restaurante Sazón Mexicano")
    print("=" * 60)
    print()
    
    try:
        print("🔄 Inicializando base de datos...")
        init_database()
        print()
        print("✅ Base de datos inicializada correctamente")
        print()
        print("📝 Datos iniciales creados:")
        print("   👨‍💼 Usuario Admin: admin / admin123")
        print("   👨‍🍳 Usuario Mesero: mesero / mesero123")
        print("   🍽️  Productos del menú")
        print("   🏷️  Códigos de descuento")
        print()
        print("🚀 Ahora puedes iniciar la aplicación con: python main.py")
        return True
    except Exception as e:
        print()
        print("❌ Error inicializando base de datos:")
        print(f"   {e}")
        print()
        print("🔍 Verifica:")
        print("   1. Que MySQL esté corriendo")
        print("   2. Las credenciales en .env o config.py")
        print("   3. Que tengas permisos para crear bases de datos")
        print()
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

