from datetime import datetime

# Conversión de cadena de fecha a tipo datetime
def parse_date(date_str):
    for fmt in ('%d/%m/%Y', '%Y', '%m/%Y'):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None  # Si no se puede convertir, devolver None
