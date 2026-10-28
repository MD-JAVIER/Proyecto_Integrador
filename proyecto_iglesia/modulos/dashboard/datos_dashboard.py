"""
datos_dashboard.py
------------------
ÚNICO archivo del dashboard que habla con los datos.

AHORA: devuelve datos de prueba, para ver el dashboard funcionando.
DESPUÉS: se reemplaza el cuerpo de cada función por su consulta SQL
(la consulta está en el comentario TODO de cada una).
Los nombres de las funciones y lo que devuelven NO deben cambiar.
"""
from datetime import date, timedelta

# ---------- DATOS DE PRUEBA ----------
_OFRENDAS_PRUEBA = {  # mes: total
    1: 1200.0, 2: 950.0, 3: 1500.0, 4: 1100.0, 5: 1750.0,
    6: 1300.0, 7: 1650.0, 8: 1400.0, 9: 1900.0, 10: 1250.0,
    11: 0.0, 12: 0.0,
}

_CULTOS = {2: "Culto Miércoles", 4: "Culto Viernes", 5: "Culto Sábado", 6: "Culto Domingo"}
# (los números son weekday(): lunes=0 ... domingo=6)

_MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
          "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def nombre_usuario(correo):
    """Devuelve el nombre completo de quien inició sesión.

    TODO: SELECT nombre FROM usuarios WHERE correo = %s;
    (si la tabla usuarios aún no tiene nombre, se puede agregar esa columna)
    """
    return "Pastor"


def resumen_miembros():
    """Devuelve dict: {"total": 60, "jovenes": 25, "damas": 20, "caballeros": 15}

    TODO: contar miembros activos por ministerio, por ejemplo:
        SELECT mi.nombre, COUNT(*)
        FROM miembro_ministerio mm
        JOIN ministerios mi ON mi.id_ministerio = mm.id_ministerio
        JOIN miembros m ON m.id_miembro = mm.id_miembro
        WHERE m.activo = 1
        GROUP BY mi.nombre;
      y el total:  SELECT COUNT(*) FROM miembros WHERE activo = 1;
    """
    return {"total": 60, "jovenes": 25, "damas": 20, "caballeros": 15}


def ofrendas_por_mes(anio):
    """Devuelve dict {mes: total} del año indicado. Los meses sin datos pueden faltar.

    TODO: SELECT mes, SUM(monto) FROM ofrendas WHERE anio = %s GROUP BY mes;
    (por ahora lee las mismas ofrendas de prueba del área de Finanzas)
    """
    from modulos.finanzas import datos_finanzas
    return datos_finanzas.ofrendas_por_mes(anio)


def miembros_activos_inactivos():
    """Devuelve la tupla (activos, inactivos).

    TODO: SELECT activo, COUNT(*) FROM miembros GROUP BY activo;
    """
    return 48, 12


def lideres():
    """Devuelve una lista de (cargo, nombre) por ministerio. El nombre va vacío si no hay líder.

    TODO: SELECT mi.nombre, GROUP_CONCAT(CONCAT(m.nombres, ' ', m.apellidos) SEPARATOR ', ')
          FROM ministerios mi
          LEFT JOIN lideres l ON l.id_ministerio = mi.id_ministerio
          LEFT JOIN miembros m ON m.id_miembro = l.id_miembro
          GROUP BY mi.id_ministerio, mi.nombre ORDER BY mi.nombre;
    (por ahora lee los mismos líderes de prueba del área de Líderes)
    """
    from modulos.lideres import controlador_lideres
    return [(f"Líder de {m['nombre']}", ", ".join(l["nombre"] for l in m["lideres"]))
            for m in controlador_lideres.cargar_ministerios()]


def actividades_proximas(limite=4):
    """Devuelve una lista de (nombre, fecha) con las próximas actividades.

    TODO: SELECT nombre, fecha FROM eventos
          WHERE fecha >= CURDATE() AND estado <> 'Cancelado'
          ORDER BY fecha, hora LIMIT %s;
    (por ahora lee las mismas actividades de prueba del área de Actividades)
    """
    from modulos.actividades import datos_actividades
    return datos_actividades.proximas(limite)


def nombre_mes(numero):
    """Utilidad: nombre del mes en español (1 = enero)."""
    return _MESES[numero - 1]
