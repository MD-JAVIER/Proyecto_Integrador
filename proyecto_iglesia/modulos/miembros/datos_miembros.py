"""
datos_miembros.py
-----------------
ÚNICO archivo del área de Miembros que habla con los datos.

AHORA: trabaja con una lista de 60 miembros de prueba guardada en memoria
(si se cierra el programa, los cambios se pierden). Así el área funciona completa.
DESPUÉS: se reemplaza el cuerpo de cada función por su consulta SQL
(el SQL está en el comentario TODO de cada una).
Los nombres de las funciones, sus parámetros y lo que devuelven NO deben cambiar.

Formato de un miembro (diccionario):
    id_miembro, nombres, apellidos, telefono, direccion, sexo ("M" o "F"),
    fecha_nacimiento (date), fecha_ingreso (date), activo (1 o 0),
    ministerios (lista de nombres), ids_ministerios (lista de ids),
    ultima_asistencia (date o None)
"""
import random
from datetime import date, timedelta

_MINISTERIOS = [(1, "Jóvenes"), (2, "Damas"), (3, "Caballeros")]
_NOMBRE_MINISTERIO = dict(_MINISTERIOS)


# ======================= DATOS DE PRUEBA (borrar al conectar la base) =======================
def _generar_miembros():
    azar = random.Random(7)
    femeninos = ["Ana", "María", "Lucía", "Elena", "Carmen", "Rosa", "Sofía", "Daniela",
                 "Gabriela", "Karla", "Marta", "Julia", "Paola", "Andrea", "Isabel"]
    masculinos = ["Carlos", "Daniel", "Jorge", "Luis", "Pedro", "José", "Miguel", "Andrés",
                  "Marcos", "Esteban", "Rafael", "Samuel", "David", "Mateo", "Josué"]
    apellidos = ["Martínez", "López", "Ruiz", "Torres", "Pérez", "Gómez", "Flores", "Castillo",
                 "Ramírez", "Herrera", "Mendoza", "Vargas", "Rivera", "Salazar", "Morales"]
    hoy = date.today()
    miembros = []
    siguiente = 1
    for id_min, cantidad in ((1, 25), (2, 20), (3, 15)):          # 25 + 20 + 15 = 60
        for _ in range(cantidad):
            if id_min == 2:
                sexo = "F"
            elif id_min == 3:
                sexo = "M"
            else:
                sexo = azar.choice(["F", "M"])
            nombre = azar.choice(femeninos if sexo == "F" else masculinos)
            edad = azar.randint(18, 29) if id_min == 1 else azar.randint(30, 70)   # regla por edad
            miembros.append({
                "id_miembro": siguiente,
                "nombres": nombre,
                "apellidos": f"{azar.choice(apellidos)} {azar.choice(apellidos)}",
                "telefono": f"8800 {1000 + siguiente}",
                "direccion": "Barrio central, casa " + str(azar.randint(1, 80)),
                "sexo": sexo,
                "fecha_nacimiento": hoy - timedelta(days=edad * 365 + azar.randint(0, 300)),
                "fecha_ingreso": hoy - timedelta(days=azar.randint(40, 1100)),
                "activo": 1,
                "ids_ministerios": [id_min],
                "ultima_asistencia": hoy - timedelta(days=azar.randint(0, 9)),
            })
            siguiente += 1

    inactivos = set(azar.sample(range(57), 12))                    # 12 inactivos (sin contar los 3 nuevos)
    por_avisar = [i for i in range(60) if i not in inactivos][:5]  # 5 cerca de quedar inactivos
    for i, m in enumerate(miembros):
        if i in inactivos:
            m["activo"] = 0
            m["ultima_asistencia"] = hoy - timedelta(days=azar.randint(16, 60))
        elif i in por_avisar:
            m["ultima_asistencia"] = hoy - timedelta(days=azar.randint(10, 14))
    for m in miembros[-3:]:                                        # 3 ingresaron este mes
        m["fecha_ingreso"] = hoy - timedelta(days=min(hoy.day - 1, azar.randint(0, 3)))
        m["activo"] = 1
        m["ultima_asistencia"] = hoy
    return miembros


_MIEMBROS = _generar_miembros()


def _con_nombres_de_ministerios(m):
    copia = dict(m)
    copia["ids_ministerios"] = list(m["ids_ministerios"])
    copia["ministerios"] = [_NOMBRE_MINISTERIO[i] for i in m["ids_ministerios"]]
    return copia


def _es_nuevo(m):
    hoy = date.today()
    return m["fecha_ingreso"].year == hoy.year and m["fecha_ingreso"].month == hoy.month


def _filtrar(estado, id_ministerio, texto, solo_nuevos=False):
    texto = (texto or "").strip().lower()
    resultado = []
    for m in _MIEMBROS:
        if solo_nuevos and not _es_nuevo(m):
            continue
        if estado is not None and m["activo"] != estado:
            continue
        if id_ministerio is not None and id_ministerio not in m["ids_ministerios"]:
            continue
        if texto and texto not in f'{m["nombres"]} {m["apellidos"]} {m["telefono"]}'.lower():
            continue
        resultado.append(m)
    resultado.sort(key=lambda m: (m["apellidos"], m["nombres"]))
    return resultado


# ======================= FUNCIONES DEL ÁREA =======================
def listar_ministerios():
    """Devuelve una lista de (id_ministerio, nombre).

    TODO: SELECT id_ministerio, nombre FROM ministerios ORDER BY nombre;
    """
    return list(_MINISTERIOS)


def listar_miembros(estado=None, id_ministerio=None, texto="", pagina=1, por_pagina=10, solo_nuevos=False):
    """Devuelve la lista de miembros de UNA página (lista de diccionarios).

    estado: 1 (activos), 0 (inactivos) o None (todos)
    id_ministerio: id o None (todos)
    texto: busca en nombres, apellidos y teléfono ('' = sin búsqueda)
    solo_nuevos: True = solo los que ingresaron este mes
    Cada diccionario trae: id_miembro, nombres, apellidos, telefono, activo,
    ministerios (lista de nombres) y ultima_asistencia (date o None).

    TODO:
        SELECT m.id_miembro, m.nombres, m.apellidos, m.telefono, m.activo,
               GROUP_CONCAT(DISTINCT mi.nombre ORDER BY mi.nombre SEPARATOR ', ') AS ministerios,
               (SELECT MAX(e.fecha)
                  FROM asistencia a JOIN eventos e ON e.id_evento = a.id_evento
                 WHERE a.id_miembro = m.id_miembro AND a.presente = 1
                   AND e.tipo = 'Culto') AS ultima_asistencia
        FROM miembros m
        LEFT JOIN miembro_ministerio mm ON mm.id_miembro = m.id_miembro
        LEFT JOIN ministerios mi ON mi.id_ministerio = mm.id_ministerio
        WHERE (%s IS NULL OR m.activo = %s)
          AND (%s IS NULL OR m.nombres LIKE %s OR m.apellidos LIKE %s OR m.telefono LIKE %s)
          AND (%s IS NULL OR EXISTS (SELECT 1 FROM miembro_ministerio x
                                      WHERE x.id_miembro = m.id_miembro AND x.id_ministerio = %s))
          AND (%s = 0 OR (YEAR(m.fecha_ingreso) = YEAR(CURDATE())
                          AND MONTH(m.fecha_ingreso) = MONTH(CURDATE())))   -- solo_nuevos (0 o 1)
        GROUP BY m.id_miembro
        ORDER BY m.apellidos, m.nombres
        LIMIT %s OFFSET %s;
      (el texto se envía como '%texto%'; OFFSET = (pagina - 1) * por_pagina;
       si GROUP_CONCAT devuelve un texto, separarlo en lista con .split(', '))
    """
    filtrados = _filtrar(estado, id_ministerio, texto, solo_nuevos)
    inicio = (pagina - 1) * por_pagina
    return [_con_nombres_de_ministerios(m) for m in filtrados[inicio:inicio + por_pagina]]


def contar_miembros(estado=None, id_ministerio=None, texto="", solo_nuevos=False):
    """Devuelve cuántos miembros cumplen el filtro (para la paginación).

    TODO: el mismo SELECT de listar_miembros pero con COUNT(DISTINCT m.id_miembro)
          y sin GROUP BY, ORDER BY ni LIMIT.
    """
    return len(_filtrar(estado, id_ministerio, texto, solo_nuevos))


def resumen_estados(id_ministerio=None):
    """Devuelve {"total", "activos", "inactivos", "nuevos_mes"}.

    TODO:
        SELECT COUNT(*) AS total,
               SUM(m.activo = 1) AS activos,
               SUM(m.activo = 0) AS inactivos,
               SUM(YEAR(m.fecha_ingreso) = YEAR(CURDATE())
                   AND MONTH(m.fecha_ingreso) = MONTH(CURDATE())) AS nuevos_mes
        FROM miembros m
        WHERE (%s IS NULL OR EXISTS (SELECT 1 FROM miembro_ministerio x
                                      WHERE x.id_miembro = m.id_miembro AND x.id_ministerio = %s));
    """
    lista = _filtrar(None, id_ministerio, "")
    return {
        "total": len(lista),
        "activos": sum(1 for m in lista if m["activo"] == 1),
        "inactivos": sum(1 for m in lista if m["activo"] == 0),
        "nuevos_mes": sum(1 for m in lista if _es_nuevo(m)),
    }


def obtener_miembro(id_miembro):
    """Devuelve el diccionario completo de un miembro, o None si no existe.

    TODO: SELECT * FROM miembros WHERE id_miembro = %s;
          SELECT id_ministerio FROM miembro_ministerio WHERE id_miembro = %s;
          y la última asistencia con la subconsulta de listar_miembros.
    """
    for m in _MIEMBROS:
        if m["id_miembro"] == id_miembro:
            return _con_nombres_de_ministerios(m)
    return None


def crear_miembro(datos, ids_ministerios):
    """Crea un miembro y lo asigna a sus ministerios. Devuelve el id nuevo.

    datos: nombres, apellidos, telefono, direccion, sexo, fecha_nacimiento, fecha_ingreso
    (ids_ministerios trae UN solo ministerio)

    TODO (en UNA transacción: si algo falla, rollback):
        INSERT INTO miembros (nombres, apellidos, telefono, direccion, sexo,
                              fecha_nacimiento, fecha_ingreso, activo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 1);
        -- id nuevo = cursor.lastrowid
        INSERT INTO miembro_ministerio (id_miembro, id_ministerio) VALUES (%s, %s);  -- uno por ministerio
        conexion.commit()
    """
    nuevo_id = max(m["id_miembro"] for m in _MIEMBROS) + 1
    nuevo = dict(datos)
    nuevo.update({"id_miembro": nuevo_id, "activo": 1,
                  "ids_ministerios": list(ids_ministerios), "ultima_asistencia": None})
    _MIEMBROS.append(nuevo)
    return nuevo_id


def actualizar_miembro(id_miembro, datos, ids_ministerios):
    """Actualiza los datos y los ministerios de un miembro.

    TODO (en UNA transacción):
        UPDATE miembros SET nombres=%s, apellidos=%s, telefono=%s, direccion=%s, sexo=%s,
               fecha_nacimiento=%s, fecha_ingreso=%s WHERE id_miembro=%s;
        DELETE FROM miembro_ministerio WHERE id_miembro=%s;
        INSERT INTO miembro_ministerio (id_miembro, id_ministerio) VALUES (%s, %s);  -- uno por ministerio
        conexion.commit()
    """
    for m in _MIEMBROS:
        if m["id_miembro"] == id_miembro:
            m.update(datos)
            m["ids_ministerios"] = list(ids_ministerios)
            return


def cambiar_estado(id_miembro, activo):
    """Desactiva (0) o reactiva (1) a un miembro. Nunca se borra.

    TODO: UPDATE miembros SET activo = %s WHERE id_miembro = %s;
    """
    for m in _MIEMBROS:
        if m["id_miembro"] == id_miembro:
            m["activo"] = 1 if activo else 0
            return


def aplicar_regla_inactividad(dias=15):
    """Regla de asistencia: pasa a INACTIVO todo miembro activo que lleva `dias` días o más
    sin asistir a un culto. Si nunca ha asistido, se cuenta desde su fecha de ingreso.
    Devuelve cuántos miembros pasaron a inactivos.

    TODO:
        UPDATE miembros m
        SET m.activo = 0
        WHERE m.activo = 1
          AND COALESCE(
                (SELECT MAX(e.fecha)
                   FROM asistencia a JOIN eventos e ON e.id_evento = a.id_evento
                  WHERE a.id_miembro = m.id_miembro AND a.presente = 1
                    AND e.tipo = 'Culto' AND e.estado <> 'Cancelado'),
                m.fecha_ingreso
              ) <= DATE_SUB(CURDATE(), INTERVAL %s DAY);
        -- cursor.rowcount = cuántos cambiaron
    (opcional: dejarlo como un EVENT de MySQL que corra todos los días)
    """
    hoy = date.today()
    cambiados = 0
    for m in _MIEMBROS:
        if m["activo"] != 1:
            continue
        referencia = m["ultima_asistencia"] or m["fecha_ingreso"]
        if (hoy - referencia).days >= dias:
            m["activo"] = 0
            cambiados += 1
    return cambiados


def registrar_asistencia_prueba(id_miembro, fecha):
    """SOLO PARA LOS DATOS DE PRUEBA (en la base real no existe: la última asistencia se calcula
    desde la tabla asistencia y la reactivación la hace guardar_asistencia).
    Deja la fecha como última asistencia y reactiva al miembro.
    Devuelve True si estaba inactivo y volvió a quedar activo."""
    for m in _MIEMBROS:
        if m["id_miembro"] == id_miembro:
            if m["ultima_asistencia"] is None or fecha > m["ultima_asistencia"]:
                m["ultima_asistencia"] = fecha
            estaba_inactivo = m["activo"] == 0
            m["activo"] = 1
            return estaba_inactivo
    return False


def listar_ingresos(desde, hasta, id_ministerio=None):
    """Miembros que ingresaron entre dos fechas (incluidas): lista de (nombres, apellidos, fecha_ingreso).
    Se usa en los informes de miembros. Si se indica un ministerio, solo los de ese ministerio.

    TODO: SELECT m.nombres, m.apellidos, m.fecha_ingreso FROM miembros m
          WHERE m.fecha_ingreso BETWEEN %s AND %s
            AND (%s IS NULL OR EXISTS (SELECT 1 FROM miembro_ministerio x
                                        WHERE x.id_miembro = m.id_miembro AND x.id_ministerio = %s))
          ORDER BY m.fecha_ingreso, m.apellidos;
    """
    return sorted(((m["nombres"], m["apellidos"], m["fecha_ingreso"]) for m in _MIEMBROS
                   if desde <= m["fecha_ingreso"] <= hasta
                   and (id_ministerio is None or id_ministerio in m["ids_ministerios"])),
                  key=lambda x: (x[2], x[1]))
