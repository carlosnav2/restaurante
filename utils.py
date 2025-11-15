"""Utilidades comunes para el sistema"""
from datetime import datetime

# Importar timezone de Guatemala
try:
    from zoneinfo import ZoneInfo
    HAS_ZONEINFO = True
    GUATEMALA_TZ = ZoneInfo("America/Guatemala")
    UTC_TZ = ZoneInfo("UTC")
except ImportError:
    # Fallback para Python < 3.9
    import pytz
    HAS_ZONEINFO = False
    GUATEMALA_TZ = pytz.timezone("America/Guatemala")
    UTC_TZ = pytz.UTC

def get_guatemala_time():
    """Obtiene la hora actual en el timezone de Guatemala"""
    return datetime.now(GUATEMALA_TZ)

def format_datetime_to_string(dt):
    """Convierte datetime a string con formato ISO usando timezone de Guatemala"""
    if dt is None:
        return None
    if isinstance(dt, datetime):
        try:
            # Si el datetime no tiene timezone, asumimos que es UTC y lo convertimos
            if dt.tzinfo is None:
                # Convertir a timezone de Guatemala (asumimos UTC)
                if HAS_ZONEINFO:
                    dt = dt.replace(tzinfo=UTC_TZ).astimezone(GUATEMALA_TZ)
                else:
                    dt = UTC_TZ.localize(dt).astimezone(GUATEMALA_TZ)
            else:
                # Si tiene timezone, convertir a timezone de Guatemala
                dt = dt.astimezone(GUATEMALA_TZ)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except (AttributeError, ValueError, TypeError) as e:
            # Si falla la conversión, devolver el string sin conversión
            return dt.strftime('%Y-%m-%d %H:%M:%S') if hasattr(dt, 'strftime') else str(dt)
    return str(dt)

