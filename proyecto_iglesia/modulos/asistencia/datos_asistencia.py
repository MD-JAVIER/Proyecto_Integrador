"""
datos_asistencia.py
-------------------
ÚNICO archivo del área de Asistencia que habla con los datos.

AHORA: guarda las marcas de asistencia en memoria (se pierden al cerrar el programa).
DESPUÉS: se reemplaza el cuerpo de cada función por su consulta SQL
(el SQL está en el comentario TODO de cada una). Tabla: `asistencia`
(id_evento, id_miembro, presente) con UNIQUE (id_evento, id_miembro).

La asistencia es la que mueve el estado de los miembros:
    - quien asiste, queda ACTIVO (si estaba inactivo, se reactiva);
    - quien pasa 15 días sin asistir, pasa a INACTIVO (regla en datos_miembros.aplicar_regla_inactividad).
"""
from modulos.actividades import datos_actividades
from modulos.miembros import datos_miembros

_ASISTENCIAS = {}      # {(id_evento, id_miembro): True/False}   (datos de prueba)


def listar_cultos(id_ministerio, desde, hasta):
    """Cultos no cancelados entre dos fechas que ese ministerio puede registrar
    (los generales y los suyos). Devuelve lista de diccionarios de actividad.

    TODO: SELECT id_evento, nombre, fecha, hora, id_ministerio
          FROM eventos
          WHERE tipo = 'Culto' AND estado <> 'Cancelado'
            AND fecha BETWEEN %s AND %s
            AND (id_ministerio IS NULL OR id_ministerio = %s)
          ORDER BY fecha DESC, hora DESC;
    """
    return [a for a in datos_actividades.actividades_entre(desde, hasta, id_ministerio)
            if a["tipo"] == "Culto" and a["estado"] != "Cancelado"][::-1]


def listar_miembros(id_ministerio):
    """TODOS los miembros del ministerio (activos e inactivos, porque un inactivo que vuelve
    a asistir se reactiva). Cada uno: id_miembro, nombres, apellidos, activo, ultima_asistencia.

    TODO: SELECT m.id_miembro, m.nombres, m.apellidos, m.activo,
                 (SELECT MAX(e.fecha) FROM asistencia a JOIN eventos e ON e.id_evento = a.id_evento
                   WHERE a.id_miembro = m.id_miembro AND a.presente = 1
                     AND e.tipo = 'Culto' AND e.estado <> 'Cancelado') AS ultima_asistencia
          FROM miembros m
          JOIN miembro_ministerio mm ON mm.id_miembro = m.id_miembro
          WHERE mm.id_ministerio = %s
          ORDER BY m.apellidos, m.nombres;
    """
    return datos_miembros.listar_miembros(None, id_ministerio, "", 1, 100000)


def obtener_marcas(id_evento):
    """Asistencia ya guardada de un culto: {id_miembro: True/False}.

    TODO: SELECT id_miembro, presente FROM asistencia WHERE id_evento = %s;
    """
    return {m: p for (e, m), p in _ASISTENCIAS.items() if e == id_evento}


def guardar_asistencia(id_evento, marcas):
    """Guarda la asistencia de un culto. `marcas` = {id_miembro: True (asistió) / False (faltó)}.
    Quien asistió queda ACTIVO. Devuelve cuántos estaban inactivos y se reactivaron.

    TODO (en UNA transacción):
        INSERT INTO asistencia (id_evento, id_miembro, presente) VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE presente = VALUES(presente);      -- una fila por cada miembro de la lista
        UPDATE miembros SET activo = 1 WHERE id_miembro IN (<los que asistieron>);
        conexion.commit()
    """
    fecha = datos_actividades.obtener_actividad(id_evento)["fecha"]
    reactivados = 0
    for id_miembro, presente in marcas.items():
        _ASISTENCIAS[(id_evento, id_miembro)] = bool(presente)
        if presente and datos_miembros.registrar_asistencia_prueba(id_miembro, fecha):
            reactivados += 1
    return reactivados
