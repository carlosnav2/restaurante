from fastapi import APIRouter, Request, Query
from fastapi.responses import JSONResponse, HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from auth import get_current_user
from database import get_db_connection
from datetime import datetime, timedelta
from decimal import Decimal
from utils import get_guatemala_time
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import sys
import os
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

router = APIRouter()
templates = Jinja2Templates(directory="templates")

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

@router.get("/api/reports/sales-day")
async def sales_day_report(request: Request, date: str = Query(None)):
    """Reporte de ventas del día"""
    user = require_admin(request)
    if not user:
        return JSONResponse({"success": False, "error": "No autorizado"}, status_code=403)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if date:
            query_date = datetime.strptime(date, '%Y-%m-%d').date()
        else:
            query_date = get_guatemala_time().date()
        
        # Ventas del día
        cursor.execute("""
            SELECT 
                COUNT(*) as total_pedidos,
                COALESCE(SUM(total_final), 0) as ventas_totales,
                COALESCE(SUM(descuento), 0) as total_descuentos,
                COALESCE(SUM(total), 0) as subtotal,
                COALESCE(AVG(total_final), 0) as ticket_promedio,
                COALESCE(AVG(tiempo_preparacion), 0) as tiempo_promedio
            FROM pedidos
            WHERE DATE(fecha_hora) = %s
        """, (query_date,))
        stats = cursor.fetchone()
        
        # Pedidos del día por estado
        cursor.execute("""
            SELECT estado, COUNT(*) as cantidad
            FROM pedidos
            WHERE DATE(fecha_hora) = %s
            GROUP BY estado
        """, (query_date,))
        status_breakdown = cursor.fetchall()
        
        # Pedidos detallados del día
        cursor.execute("""
            SELECT * FROM pedidos
            WHERE DATE(fecha_hora) = %s
            ORDER BY fecha_hora DESC
        """, (query_date,))
        orders = cursor.fetchall()
        
        # Convertir datetime a string
        for order in orders:
            if order.get('fecha_hora'):
                order['fecha_hora'] = order['fecha_hora'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(order['fecha_hora'], 'strftime') else str(order['fecha_hora'])
        
        cursor.close()
        conn.close()
        
        # Convertir Decimal a float
        stats = convert_decimals(stats)
        status_breakdown = convert_decimals(status_breakdown)
        orders = convert_decimals(orders)
        
        return JSONResponse({
            "success": True,
            "date": str(query_date),
            "stats": stats,
            "status_breakdown": status_breakdown,
            "orders": orders
        })
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@router.get("/api/reports/top-products")
async def top_products_report(request: Request, 
                              start_date: str = Query(None),
                              end_date: str = Query(None),
                              limit: int = Query(10)):
    """Reporte de productos más vendidos"""
    user = require_admin(request)
    if not user:
        return JSONResponse({"success": False, "error": "No autorizado"}, status_code=403)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                pi.producto_nombre,
                pi.producto_id,
                SUM(pi.cantidad) as total_vendido,
                SUM(pi.precio * pi.cantidad) as ingresos_totales,
                COUNT(DISTINCT pi.pedido_id) as veces_pedido,
                AVG(pi.precio) as precio_promedio
            FROM pedido_items pi
            JOIN pedidos p ON pi.pedido_id = p.id
            WHERE 1=1
        """
        params = []
        
        if start_date:
            query += " AND DATE(p.fecha_hora) >= %s"
            params.append(datetime.strptime(start_date, '%Y-%m-%d').date())
        
        if end_date:
            query += " AND DATE(p.fecha_hora) <= %s"
            params.append(datetime.strptime(end_date, '%Y-%m-%d').date())
        
        query += """
            GROUP BY pi.producto_id, pi.producto_nombre
            ORDER BY total_vendido DESC
            LIMIT %s
        """
        params.append(limit)
        
        cursor.execute(query, params)
        products = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        products = convert_decimals(products)
        return JSONResponse({"success": True, "products": products})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@router.get("/api/reports/sales-range")
async def sales_range_report(request: Request,
                             start_date: str = Query(...),
                             end_date: str = Query(...)):
    """Reporte de ventas en un rango de fechas"""
    user = require_admin(request)
    if not user:
        return JSONResponse({"success": False, "error": "No autorizado"}, status_code=403)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Resumen general
        cursor.execute("""
            SELECT 
                COUNT(*) as total_pedidos,
                COALESCE(SUM(total_final), 0) as ventas_totales,
                COALESCE(SUM(descuento), 0) as total_descuentos,
                COALESCE(SUM(total), 0) as subtotal,
                COALESCE(AVG(total_final), 0) as ticket_promedio
            FROM pedidos
            WHERE DATE(fecha_hora) BETWEEN %s AND %s
        """, (start, end))
        summary = cursor.fetchone()
        
        # Ventas por día
        cursor.execute("""
            SELECT 
                DATE(fecha_hora) as fecha,
                COUNT(*) as pedidos,
                COALESCE(SUM(total_final), 0) as ventas
            FROM pedidos
            WHERE DATE(fecha_hora) BETWEEN %s AND %s
            GROUP BY DATE(fecha_hora)
            ORDER BY fecha ASC
        """, (start, end))
        daily_sales = cursor.fetchall()
        
        # Convertir fechas
        for day in daily_sales:
            if day.get('fecha'):
                day['fecha'] = day['fecha'].strftime('%Y-%m-%d') if hasattr(day['fecha'], 'strftime') else str(day['fecha'])
        
        cursor.close()
        conn.close()
        
        # Convertir Decimal a float
        summary = convert_decimals(summary)
        daily_sales = convert_decimals(daily_sales)
        
        return JSONResponse({
            "success": True,
            "start_date": str(start),
            "end_date": str(end),
            "summary": summary,
            "daily_sales": daily_sales
        })
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@router.get("/api/reports/categories")
async def categories_report(request: Request,
                           start_date: str = Query(None),
                           end_date: str = Query(None)):
    """Reporte por categorías"""
    user = require_admin(request)
    if not user:
        return JSONResponse({"success": False, "error": "No autorizado"}, status_code=403)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                p.categoria,
                COUNT(DISTINCT pi.pedido_id) as veces_pedida,
                SUM(pi.cantidad) as unidades_vendidas,
                SUM(pi.precio * pi.cantidad) as ingresos_totales
            FROM pedido_items pi
            JOIN pedidos pd ON pi.pedido_id = pd.id
            JOIN productos p ON pi.producto_id = p.id
            WHERE 1=1
        """
        params = []
        
        if start_date:
            query += " AND DATE(pd.fecha_hora) >= %s"
            params.append(datetime.strptime(start_date, '%Y-%m-%d').date())
        
        if end_date:
            query += " AND DATE(pd.fecha_hora) <= %s"
            params.append(datetime.strptime(end_date, '%Y-%m-%d').date())
        
        query += " GROUP BY p.categoria ORDER BY ingresos_totales DESC"
        
        cursor.execute(query, params)
        categories = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        categories = convert_decimals(categories)
        return JSONResponse({"success": True, "categories": categories})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

# ========================================
# FUNCIONES PARA GENERAR PDFs
# ========================================

def generate_pdf_sales_day(date_str: str, stats: dict, orders: list):
    """Genera un PDF del reporte de ventas del día"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#047857'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    story = []
    
    # Título
    story.append(Paragraph("🌮 SAZÓN MEXICANO", title_style))
    story.append(Paragraph("Reporte de Ventas del Día", styles['Heading2']))
    story.append(Paragraph(f"Fecha: {date_str}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Estadísticas
    stats_data = [
        ['Total Pedidos', f"{stats.get('total_pedidos', 0)}"],
        ['Ventas Totales', f"Q {float(stats.get('ventas_totales', 0)):.2f}"],
        ['Ticket Promedio', f"Q {float(stats.get('ticket_promedio', 0)):.2f}"],
        ['Total Descuentos', f"Q {float(stats.get('total_descuentos', 0)):.2f}"],
    ]
    
    stats_table = Table(stats_data, colWidths=[4*inch, 2*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Pedidos
    if orders:
        story.append(Paragraph("Pedidos del Día", styles['Heading3']))
        order_data = [['Nº Pedido', 'Fecha/Hora', 'Total', 'Estado']]
        for order in orders[:50]:  # Limitar a 50 pedidos por página
            # Convertir fecha_hora a string si es datetime
            fecha_hora = order.get('fecha_hora', '')
            if fecha_hora:
                if hasattr(fecha_hora, 'strftime'):
                    fecha = fecha_hora.strftime('%Y-%m-%d %H:%M')[:16]
                else:
                    fecha = str(fecha_hora)[:16]
            else:
                fecha = ''
            order_data.append([
                order.get('numero_pedido', ''),
                fecha,
                f"Q {float(order.get('total_final', 0)):.2f}",
                order.get('estado', '')
            ])
        
        order_table = Table(order_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 1*inch])
        order_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#047857')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        story.append(order_table)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_pdf_sales_range(start_date: str, end_date: str, summary: dict, daily_sales: list):
    """Genera un PDF del reporte de ventas por rango de fechas"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#047857'),
        spaceAfter=30,
        alignment=1
    )
    
    story = []
    
    # Título
    story.append(Paragraph("🌮 SAZÓN MEXICANO", title_style))
    story.append(Paragraph("Reporte de Ventas por Rango de Fechas", styles['Heading2']))
    story.append(Paragraph(f"Del {start_date} al {end_date}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Resumen
    summary_data = [
        ['Total Pedidos', f"{summary.get('total_pedidos', 0)}"],
        ['Ventas Totales', f"Q {float(summary.get('ventas_totales', 0)):.2f}"],
        ['Ticket Promedio', f"Q {float(summary.get('ticket_promedio', 0)):.2f}"],
        ['Total Descuentos', f"Q {float(summary.get('total_descuentos', 0)):.2f}"],
    ]
    
    summary_table = Table(summary_data, colWidths=[4*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Ventas por día
    if daily_sales:
        story.append(Paragraph("Ventas por Día", styles['Heading3']))
        daily_data = [['Fecha', 'Pedidos', 'Ventas']]
        for day in daily_sales:
            daily_data.append([
                day.get('fecha', ''),
                str(day.get('pedidos', 0)),
                f"Q {float(day.get('ventas', 0)):.2f}"
            ])
        
        daily_table = Table(daily_data, colWidths=[2*inch, 2*inch, 2*inch])
        daily_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#047857')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        story.append(daily_table)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_pdf_top_products(products: list, start_date: str = None, end_date: str = None):
    """Genera un PDF del reporte de productos más vendidos"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#047857'),
        spaceAfter=30,
        alignment=1
    )
    
    story = []
    
    # Título
    story.append(Paragraph("🌮 SAZÓN MEXICANO", title_style))
    story.append(Paragraph("Productos Más Vendidos", styles['Heading2']))
    if start_date and end_date:
        story.append(Paragraph(f"Del {start_date} al {end_date}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Tabla de productos
    if products:
        product_data = [['#', 'Producto', 'Cantidad', 'Ingresos']]
        for idx, prod in enumerate(products, 1):
            product_data.append([
                str(idx),
                prod.get('producto_nombre', ''),
                str(int(prod.get('total_vendido', 0))),
                f"Q {float(prod.get('ingresos_totales', 0)):.2f}"
            ])
        
        product_table = Table(product_data, colWidths=[0.5*inch, 3.5*inch, 1*inch, 1.5*inch])
        product_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#047857')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        story.append(product_table)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_pdf_categories(categories: list, start_date: str = None, end_date: str = None):
    """Genera un PDF del reporte por categorías"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#047857'),
        spaceAfter=30,
        alignment=1
    )
    
    story = []
    
    # Título
    story.append(Paragraph("🌮 SAZÓN MEXICANO", title_style))
    story.append(Paragraph("Reporte por Categorías", styles['Heading2']))
    if start_date and end_date:
        story.append(Paragraph(f"Del {start_date} al {end_date}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Tabla de categorías
    if categories:
        cat_data = [['Categoría', 'Unidades Vendidas', 'Veces Pedida', 'Ingresos Totales']]
        for cat in categories:
            cat_data.append([
                cat.get('categoria', ''),
                str(int(cat.get('unidades_vendidas', 0))),
                str(cat.get('veces_pedida', 0)),
                f"Q {float(cat.get('ingresos_totales', 0)):.2f}"
            ])
        
        cat_table = Table(cat_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        cat_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#047857')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        story.append(cat_table)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# ========================================
# ENDPOINTS PARA EXPORTAR PDFs
# ========================================

@router.get("/api/reports/pdf/sales-day")
async def export_sales_day_pdf(request: Request, date: str = Query(...)):
    """Exporta reporte de ventas del día a PDF"""
    user = require_admin(request)
    if not user:
        return Response(content="No autorizado", status_code=403)
    
    try:
        # Validar formato de fecha
        if not date or date.lower() in ['true', 'false', '']:
            return Response(
                content="Error: Se requiere una fecha válida en formato YYYY-MM-DD",
                status_code=400,
                media_type='text/plain'
            )
        
        # Validar que sea un string y tenga el formato correcto
        if not isinstance(date, str) or not date.strip():
            return Response(
                content="Error: Se requiere una fecha válida en formato YYYY-MM-DD",
                status_code=400,
                media_type='text/plain'
            )
        
        # Validar formato con regex antes de parsear
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', date.strip()):
            return Response(
                content="Error: Formato de fecha inválido. Debe ser YYYY-MM-DD (ejemplo: 2025-11-14)",
                status_code=400,
                media_type='text/plain'
            )
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query_date = datetime.strptime(date.strip(), '%Y-%m-%d').date()
        
        # Ventas del día
        cursor.execute("""
            SELECT 
                COUNT(*) as total_pedidos,
                COALESCE(SUM(total_final), 0) as ventas_totales,
                COALESCE(SUM(descuento), 0) as total_descuentos,
                COALESCE(SUM(total), 0) as subtotal,
                COALESCE(AVG(total_final), 0) as ticket_promedio
            FROM pedidos
            WHERE DATE(fecha_hora) = %s
        """, (query_date,))
        stats = cursor.fetchone()
        
        # Pedidos del día
        cursor.execute("""
            SELECT * FROM pedidos
            WHERE DATE(fecha_hora) = %s
            ORDER BY fecha_hora DESC
        """, (query_date,))
        orders = cursor.fetchall()
        
        # Convertir datetime a string para evitar errores de serialización
        for order in orders:
            if order.get('fecha_hora'):
                if hasattr(order['fecha_hora'], 'strftime'):
                    order['fecha_hora'] = order['fecha_hora'].strftime('%Y-%m-%d %H:%M:%S')
                else:
                    order['fecha_hora'] = str(order['fecha_hora'])
        
        cursor.close()
        conn.close()
        
        stats = convert_decimals(stats)
        orders = convert_decimals(orders)
        pdf_buffer = generate_pdf_sales_day(str(query_date), stats, orders)
        
        return Response(
            content=pdf_buffer.read(),
            media_type='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename=ventas_dia_{date}.pdf'
            }
        )
    except ValueError as e:
        return Response(
            content=f"Error: Fecha inválida. Debe estar en formato YYYY-MM-DD. Error: {str(e)}",
            status_code=400,
            media_type='text/plain'
        )
    except Exception as e:
        return Response(
            content=f"Error al generar PDF: {str(e)}",
            status_code=500,
            media_type='text/plain'
        )

@router.get("/api/reports/pdf/sales-range")
async def export_sales_range_pdf(request: Request, start_date: str = Query(...), end_date: str = Query(...)):
    """Exporta reporte de ventas por rango a PDF"""
    user = require_admin(request)
    if not user:
        return Response(content="No autorizado", status_code=403)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Resumen
        cursor.execute("""
            SELECT 
                COUNT(*) as total_pedidos,
                COALESCE(SUM(total_final), 0) as ventas_totales,
                COALESCE(SUM(descuento), 0) as total_descuentos,
                COALESCE(SUM(total), 0) as subtotal,
                COALESCE(AVG(total_final), 0) as ticket_promedio
            FROM pedidos
            WHERE DATE(fecha_hora) BETWEEN %s AND %s
        """, (start, end))
        summary = cursor.fetchone()
        
        # Ventas por día
        cursor.execute("""
            SELECT 
                DATE(fecha_hora) as fecha,
                COUNT(*) as pedidos,
                COALESCE(SUM(total_final), 0) as ventas
            FROM pedidos
            WHERE DATE(fecha_hora) BETWEEN %s AND %s
            GROUP BY DATE(fecha_hora)
            ORDER BY fecha ASC
        """, (start, end))
        daily_sales = cursor.fetchall()
        
        # Convertir fechas
        for day in daily_sales:
            if day.get('fecha'):
                day['fecha'] = day['fecha'].strftime('%Y-%m-%d') if hasattr(day['fecha'], 'strftime') else str(day['fecha'])
        
        cursor.close()
        conn.close()
        
        summary = convert_decimals(summary)
        daily_sales = convert_decimals(daily_sales)
        pdf_buffer = generate_pdf_sales_range(str(start), str(end), summary, daily_sales)
        
        return Response(
            content=pdf_buffer.read(),
            media_type='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename=ventas_rango_{start_date}_{end_date}.pdf'
            }
        )
    except Exception as e:
        return Response(content=f"Error: {str(e)}", status_code=500)

@router.get("/api/reports/pdf/top-products")
async def export_top_products_pdf(request: Request, start_date: str = Query(None), end_date: str = Query(None), limit: int = Query(10)):
    """Exporta reporte de productos más vendidos a PDF"""
    user = require_admin(request)
    if not user:
        return Response(content="No autorizado", status_code=403)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                pi.producto_nombre,
                pi.producto_id,
                SUM(pi.cantidad) as total_vendido,
                SUM(pi.precio * pi.cantidad) as ingresos_totales,
                COUNT(DISTINCT pi.pedido_id) as veces_pedido,
                AVG(pi.precio) as precio_promedio
            FROM pedido_items pi
            JOIN pedidos p ON pi.pedido_id = p.id
            WHERE 1=1
        """
        params = []
        
        if start_date:
            query += " AND DATE(p.fecha_hora) >= %s"
            params.append(datetime.strptime(start_date, '%Y-%m-%d').date())
        
        if end_date:
            query += " AND DATE(p.fecha_hora) <= %s"
            params.append(datetime.strptime(end_date, '%Y-%m-%d').date())
        
        query += """
            GROUP BY pi.producto_id, pi.producto_nombre
            ORDER BY total_vendido DESC
            LIMIT %s
        """
        params.append(limit)
        
        cursor.execute(query, params)
        products = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        products = convert_decimals(products)
        pdf_buffer = generate_pdf_top_products(products, start_date, end_date)
        
        filename = f"productos_vendidos_{start_date or 'all'}_{end_date or 'all'}.pdf"
        return Response(
            content=pdf_buffer.read(),
            media_type='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename={filename}'
            }
        )
    except Exception as e:
        return Response(content=f"Error: {str(e)}", status_code=500)

@router.get("/api/reports/pdf/categories")
async def export_categories_pdf(request: Request, start_date: str = Query(None), end_date: str = Query(None)):
    """Exporta reporte por categorías a PDF"""
    user = require_admin(request)
    if not user:
        return Response(content="No autorizado", status_code=403)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                p.categoria,
                COUNT(DISTINCT pi.pedido_id) as veces_pedida,
                SUM(pi.cantidad) as unidades_vendidas,
                SUM(pi.precio * pi.cantidad) as ingresos_totales
            FROM pedido_items pi
            JOIN pedidos pd ON pi.pedido_id = pd.id
            JOIN productos p ON pi.producto_id = p.id
            WHERE 1=1
        """
        params = []
        
        if start_date:
            query += " AND DATE(pd.fecha_hora) >= %s"
            params.append(datetime.strptime(start_date, '%Y-%m-%d').date())
        
        if end_date:
            query += " AND DATE(pd.fecha_hora) <= %s"
            params.append(datetime.strptime(end_date, '%Y-%m-%d').date())
        
        query += " GROUP BY p.categoria ORDER BY ingresos_totales DESC"
        
        cursor.execute(query, params)
        categories = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        categories = convert_decimals(categories)
        pdf_buffer = generate_pdf_categories(categories, start_date, end_date)
        
        filename = f"categorias_{start_date or 'all'}_{end_date or 'all'}.pdf"
        return Response(
            content=pdf_buffer.read(),
            media_type='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename={filename}'
            }
        )
    except Exception as e:
        return Response(content=f"Error: {str(e)}", status_code=500)

