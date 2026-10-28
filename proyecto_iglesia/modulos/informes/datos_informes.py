"""
datos_informes.py
-----------------
ÚNICO archivo del área de Informes que habla con los datos. Solo LEE: junta lo que necesitan
los informes que se generan en Word (Informe general de miembros e Informe general de ofrendas).

AHORA: lee los datos de prueba de las otras áreas.
DESPUÉS: se reemplaza el cuerpo de cada función por su consulta SQL (en el comentario TODO).
Los nombres de las funciones y lo que devuelven NO deben cambiar.
"""
from modulos.finanzas import datos_finanzas
from modulos.miembros import datos_miembros


def resumen_miembros(id_ministerio=None):
    """{"total", "activos", "inactivos", "nuevos_mes"} de los miembros (estado actual).
    Si se indica un ministerio, solo cuenta a los de ese ministerio.

    TODO: SELECT COUNT(*) AS total, SUM(m.activo = 1) AS activos, SUM(m.activo = 0) AS inactivos
          FROM miembros m
          WHERE (%s IS NULL OR EXISTS (SELECT 1 FROM miembro_ministerio x
                                        WHERE x.id_miembro = m.id_miembro AND x.id_ministerio = %s));
    """
    return datos_miembros.resumen_estados(id_ministerio)


def contar_por_ministerio():
    """Cantidad de miembros por ministerio: lista de (nombre_ministerio, cantidad).
    Como cada miembro pertenece a un solo ministerio, la suma no repite personas.

    TODO: SELECT mi.nombre, COUNT(*) FROM miembro_ministerio mm
          JOIN ministerios mi ON mi.id_ministerio = mm.id_ministerio
          GROUP BY mi.nombre ORDER BY mi.nombre;
    """
    return [(nombre, datos_miembros.contar_miembros(None, id_min, ""))
            for id_min, nombre in datos_miembros.listar_ministerios()]


def ingresos_en_periodo(desde, hasta, id_ministerio=None):
    """Miembros que ingresaron en el período: lista de (nombres, apellidos, fecha_ingreso)."""
    return datos_miembros.listar_ingresos(desde, hasta, id_ministerio)


def nombre_ministerio(id_ministerio):
    """Nombre de un ministerio.

    TODO: SELECT nombre FROM ministerios WHERE id_ministerio = %s;
    """
    return dict(datos_miembros.listar_ministerios()).get(id_ministerio, "")


def ofrendas_del_anio(anio):
    """Ofrendas registradas de un año: {mes: {"monto", "registrado_por"}}.

    TODO: SELECT o.mes, o.monto, u.nombre FROM ofrendas o
          JOIN usuarios u ON u.id_usuario = o.id_usuario WHERE o.anio = %s ORDER BY o.mes;
    """
    return {o["mes"]: {"monto": o["monto"], "registrado_por": o["registrado_por"]}
            for o in datos_finanzas.listar_ofrendas(anio)}


def anios_con_ofrendas():
    """Años que tienen ofrendas (de mayor a menor)."""
    return datos_finanzas.listar_anios()
