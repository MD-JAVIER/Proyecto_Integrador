"""
datos_actividades.py
--------------------
ÚNICO archivo del área de Actividades que habla con los datos.

AHORA: usa actividades de prueba guardadas en memoria (si se cierra el programa,
los cambios se pierden). Así el área funciona completa.
DESPUÉS: se reemplaza el cuerpo de cada función por su consulta SQL
(el SQL está en el comentario TODO de cada una).
Los nombres de las funciones, sus parámetros y lo que devuelven NO deben cambiar.

Tabla de la base de datos: `eventos`  (lleva la columna nueva `id_ministerio`).
Formato de una actividad (diccionario):
    id_evento, nombre, tipo ("Culto" o "Externo"), fecha (date), hora (time),
    lugar, descripcion, estado ("Programado" o "Cancelado"),
    id_ministerio (None = actividad GENERAL de la iglesia; un número = actividad de ese ministerio)

QUIÉN VE QUÉ (parámetro `para_ministerio`):
    None  -> vista del PASTOR: las actividades generales y SOLO LOS CULTOS de los ministerios
             (los convivios y otras actividades de un ministerio no le aparecen).
    número -> vista de un LÍDER: las actividades generales y las de su propio ministerio.
    En SQL, el filtro de visibilidad es:
        pastor:  AND (id_ministerio IS NULL OR tipo = 'Culto')
        líder:   AND (id_ministerio IS NULL OR id_ministerio = %s)
"""
from datetime import date, time, timedelta

from modulos.miembros import datos_miembros

# ======================= DATOS DE PRUEBA (borrar al conectar la base) =======================
_EVENTOS = []

# día de la semana: (nombre, hora, id_ministerio dueño)   2 = Damas, 1 = Jóvenes, None = general
_CULTOS = {2: ("Culto Miércoles", time(19, 0), 2), 4: ("Culto Viernes", time(19, 0), None),
           5: ("Culto Sábado", time(18, 0), 1), 6: ("Culto Domingo", time(9, 0), None)}


def _cargar_pruebas():
    hoy = date.today()
    lunes = hoy - timedelta(days=hoy.weekday())
    siguiente = 1
    canceladas = {(-3, 4), (-5, 2)}            # (semana, día): dos cultos cancelados
    for semana in range(-8, 3):                 # 8 semanas atrás hasta 2 adelante
        for dia, (nombre, hora, dueno) in _CULTOS.items():
            if semana == 0 and dia == 5:        # el sábado de esta semana queda "sin crear"
                continue
            _EVENTOS.append({
                "id_evento": siguiente, "nombre": nombre, "tipo": "Culto",
                "fecha": lunes + timedelta(days=7 * semana + dia), "hora": hora,
                "lugar": "Templo principal", "descripcion": "", "id_ministerio": dueno,
                "estado": "Cancelado" if (semana, dia) in canceladas else "Programado",
            })
            siguiente += 1
    externos = [   # (días desde el lunes, nombre, hora, lugar, id_ministerio)
        (-30, "Visita a la iglesia hermana", time(10, 0), "Iglesia hermana, comunidad vecina", None),
        (-12, "Campaña de ayuda comunitaria", time(8, 30), "Parque central", None),
        (9, "Retiro de jóvenes", time(8, 0), "Casa de retiros", 1),
        (16, "Convivio de damas", time(15, 0), "Salón comunal", 2),
    ]
    for dias, nombre, hora, lugar, dueno in externos:
        _EVENTOS.append({"id_evento": siguiente, "nombre": nombre, "tipo": "Externo",
                         "fecha": lunes + timedelta(days=dias), "hora": hora, "lugar": lugar,
                         "descripcion": "Actividad fuera de la iglesia", "id_ministerio": dueno,
                         "estado": "Programado"})
        siguiente += 1


_cargar_pruebas()


def _visible(e, para_ministerio):
    if e["id_ministerio"] is None:
        return True
    if para_ministerio is None:                  # el pastor solo ve los cultos de los ministerios
        return e["tipo"] == "Culto"
    return e["id_ministerio"] == para_ministerio


def _filtrar(tipo, situacion, texto, para_ministerio=None):
    hoy = date.today()
    texto = (texto or "").strip().lower()
    resultado = []
    for e in _EVENTOS:
        if not _visible(e, para_ministerio):
            continue
        if tipo is not None and e["tipo"] != tipo:
            continue
        cancelado = e["estado"] == "Cancelado"
        if situacion == "proximas" and (cancelado or e["fecha"] < hoy):
            continue
        if situacion == "realizadas" and (cancelado or e["fecha"] >= hoy):
            continue
        if situacion == "canceladas" and not cancelado:
            continue
        if texto and texto not in f'{e["nombre"]} {e["lugar"]}'.lower():
            continue
        resultado.append(e)
    resultado.sort(key=lambda e: (e["fecha"], e["hora"]), reverse=True)
    return resultado


# ======================= FUNCIONES DEL ÁREA =======================
def listar_ministerios():
    """Devuelve la lista de (id_ministerio, nombre).

    TODO: SELECT id_ministerio, nombre FROM ministerios ORDER BY nombre;
    """
    return datos_miembros.listar_ministerios()


def listar_actividades(tipo=None, situacion=None, texto="", pagina=1, por_pagina=6, para_ministerio=None):
    """Devuelve las actividades de UNA página, de la más reciente a la más antigua.

    tipo: "Culto", "Externo" o None (todas)
    situacion: None, "proximas", "realizadas" o "canceladas"
    texto: busca en nombre y lugar ('' = sin búsqueda)
    para_ministerio: None = vista del pastor; un número = vista del líder de ese ministerio

    TODO:
        SELECT id_evento, nombre, tipo, fecha, hora, lugar, descripcion, estado, id_ministerio
        FROM eventos
        WHERE (%s IS NULL OR tipo = %s)
          AND (%s IS NULL OR nombre LIKE %s OR lugar LIKE %s)
          AND (%s IS NULL
               OR (%s = 'proximas'    AND estado <> 'Cancelado' AND fecha >= CURDATE())
               OR (%s = 'realizadas'  AND estado <> 'Cancelado' AND fecha <  CURDATE())
               OR (%s = 'canceladas'  AND estado =  'Cancelado'))
          AND <filtro de visibilidad: ver el comentario del inicio del archivo>
        ORDER BY fecha DESC, hora DESC
        LIMIT %s OFFSET %s;
      (el texto se envía como '%texto%'; OFFSET = (pagina - 1) * por_pagina)
    """
    inicio = (pagina - 1) * por_pagina
    return [dict(e) for e in _filtrar(tipo, situacion, texto, para_ministerio)[inicio:inicio + por_pagina]]


def contar_actividades(tipo=None, situacion=None, texto="", para_ministerio=None):
    """Cuántas actividades cumplen el filtro (para la paginación).

    TODO: el mismo SELECT de listar_actividades con COUNT(*) y sin ORDER BY ni LIMIT.
    """
    return len(_filtrar(tipo, situacion, texto, para_ministerio))


def resumen_mes(anio, mes, para_ministerio=None):
    """Devuelve {"total", "cultos", "externos", "canceladas"} de un mes (solo lo que esa vista puede ver).

    TODO: SELECT COUNT(*) AS total,
                 SUM(tipo = 'Culto')  AS cultos,
                 SUM(tipo = 'Externo') AS externos,
                 SUM(estado = 'Cancelado') AS canceladas
          FROM eventos
          WHERE YEAR(fecha) = %s AND MONTH(fecha) = %s
            AND <filtro de visibilidad>;
    """
    del_mes = [e for e in _EVENTOS if _visible(e, para_ministerio)
               and e["fecha"].year == anio and e["fecha"].month == mes]
    return {
        "total": len(del_mes),
        "cultos": sum(1 for e in del_mes if e["tipo"] == "Culto"),
        "externos": sum(1 for e in del_mes if e["tipo"] == "Externo"),
        "canceladas": sum(1 for e in del_mes if e["estado"] == "Cancelado"),
    }


def actividades_entre(desde, hasta, para_ministerio=None):
    """Actividades con fecha entre dos días (incluidos), ordenadas. Se usa en 'Cultos de esta semana'.

    TODO: SELECT id_evento, nombre, tipo, fecha, hora, lugar, descripcion, estado, id_ministerio
          FROM eventos WHERE fecha BETWEEN %s AND %s AND <filtro de visibilidad>
          ORDER BY fecha, hora;
    """
    return [dict(e) for e in sorted(_EVENTOS, key=lambda e: (e["fecha"], e["hora"]))
            if desde <= e["fecha"] <= hasta and _visible(e, para_ministerio)]


def existe_culto(fecha, excluir_id=None, id_ministerio=None):
    """True si ya hay un Culto de ese mismo dueño (general o del ministerio) en esa fecha.
    Se ignora el id indicado, para poder editar.

    TODO: SELECT COUNT(*) FROM eventos
          WHERE tipo = 'Culto' AND fecha = %s
            AND (id_ministerio <=> %s)              -- <=> compara también cuando es NULL
            AND (%s IS NULL OR id_evento <> %s);
    """
    return any(e["tipo"] == "Culto" and e["fecha"] == fecha and e["id_evento"] != excluir_id
               and e["id_ministerio"] == id_ministerio for e in _EVENTOS)


def obtener_actividad(id_evento):
    """Devuelve el diccionario de una actividad, o None.

    TODO: SELECT * FROM eventos WHERE id_evento = %s;
    """
    for e in _EVENTOS:
        if e["id_evento"] == id_evento:
            return dict(e)
    return None


def crear_actividad(datos):
    """Crea una actividad (siempre 'Programado'). Devuelve el id nuevo.

    datos: nombre, tipo, fecha, hora, lugar, descripcion, id_ministerio (None = general)

    TODO: INSERT INTO eventos (nombre, tipo, fecha, hora, lugar, descripcion, id_ministerio, estado)
          VALUES (%s, %s, %s, %s, %s, %s, %s, 'Programado');   -- id nuevo = cursor.lastrowid
    """
    nuevo_id = max((e["id_evento"] for e in _EVENTOS), default=0) + 1
    nuevo = dict(datos)
    nuevo.update({"id_evento": nuevo_id, "estado": "Programado"})
    _EVENTOS.append(nuevo)
    return nuevo_id


def actualizar_actividad(id_evento, datos):
    """Cambia los datos de una actividad (el dueño, id_ministerio, no se cambia).

    TODO: UPDATE eventos SET nombre=%s, tipo=%s, fecha=%s, hora=%s, lugar=%s, descripcion=%s
          WHERE id_evento=%s;
    """
    for e in _EVENTOS:
        if e["id_evento"] == id_evento:
            e.update({k: v for k, v in datos.items() if k != "id_ministerio"})
            return


def cambiar_estado(id_evento, estado):
    """Cancela ("Cancelado") o reactiva ("Programado") una actividad. Nunca se borra.

    TODO: UPDATE eventos SET estado = %s WHERE id_evento = %s;
    """
    for e in _EVENTOS:
        if e["id_evento"] == id_evento:
            e["estado"] = estado
            return


def proximas(limite=5, para_ministerio=None):
    """Próximas actividades no canceladas: lista de (nombre, fecha). La usa el Panel del pastor.

    TODO: SELECT nombre, fecha FROM eventos
          WHERE estado <> 'Cancelado' AND fecha >= CURDATE() AND <filtro de visibilidad>
          ORDER BY fecha, hora LIMIT %s;
    """
    hoy = date.today()
    futuras = sorted((e for e in _EVENTOS if e["estado"] != "Cancelado" and e["fecha"] >= hoy
                      and _visible(e, para_ministerio)), key=lambda e: (e["fecha"], e["hora"]))
    return [(e["nombre"], e["fecha"]) for e in futuras[:limite]]
