"""
datos_finanzas.py
-----------------
ÚNICO archivo del área de Finanzas que habla con los datos.

AHORA: usa ofrendas de prueba guardadas en memoria (si se cierra el programa,
los cambios se pierden). Así el área funciona completa.
DESPUÉS: se reemplaza el cuerpo de cada función por su consulta SQL
(el SQL está en el comentario TODO de cada una).
Los nombres de las funciones, sus parámetros y lo que devuelven NO deben cambiar.

Regla de la base de datos: solo puede haber UNA ofrenda por mes y año
(restricción única sobre mes + anio en la tabla ofrendas).
"""
from datetime import date

# ======================= DATOS DE PRUEBA (borrar al conectar la base) =======================
_OFRENDAS = []


def _cargar_pruebas():
    hoy = date.today()
    anterior = [1100, 980, 1350, 1200, 1500, 1250, 1400, 1300, 1600, 1450, 1700, 2100]
    actual = [1200, 950, 1500, 1100, 1750, 1300, 1650, 1400, 1900]     # enero a septiembre
    siguiente_id = 1
    for anio, montos in ((hoy.year - 1, anterior), (hoy.year, actual)):
        for mes, monto in enumerate(montos, start=1):
            if anio == hoy.year and mes >= hoy.month:      # el mes actual queda pendiente
                continue
            _OFRENDAS.append({"id_ofrenda": siguiente_id, "mes": mes, "anio": anio,
                              "monto": float(monto), "registrado_por": "Pastor"})
            siguiente_id += 1


_cargar_pruebas()


# ======================= FUNCIONES DEL ÁREA =======================
def listar_anios():
    """Devuelve la lista de años que tienen ofrendas (de mayor a menor).

    TODO: SELECT DISTINCT anio FROM ofrendas ORDER BY anio DESC;
    """
    return sorted({o["anio"] for o in _OFRENDAS}, reverse=True)


def listar_ofrendas(anio):
    """Devuelve las ofrendas registradas de un año (lista de diccionarios).

    Cada diccionario: id_ofrenda, mes, anio, monto, registrado_por (nombre).

    TODO: SELECT o.id_ofrenda, o.mes, o.anio, o.monto, u.correo AS registrado_por
          FROM ofrendas o
          JOIN usuarios u ON u.id_usuario = o.id_usuario
          WHERE o.anio = %s
          ORDER BY o.mes;
    """
    return [dict(o) for o in sorted(_OFRENDAS, key=lambda o: o["mes"]) if o["anio"] == anio]


def ofrendas_por_mes(anio):
    """Devuelve {mes: monto} del año. Los meses sin registro no aparecen.
    (También lo usa el gráfico del Panel.)

    TODO: SELECT mes, SUM(monto) FROM ofrendas WHERE anio = %s GROUP BY mes;
    """
    return {o["mes"]: o["monto"] for o in _OFRENDAS if o["anio"] == anio}


def registrar_ofrenda(mes, anio, monto, correo_usuario):
    """Registra la ofrenda de un mes. Devuelve el id nuevo.
    Debe fallar con ValueError si ese mes y año ya tienen ofrenda.

    TODO: INSERT INTO ofrendas (mes, anio, monto, id_usuario)
          VALUES (%s, %s, %s, (SELECT id_usuario FROM usuarios WHERE correo = %s));
          -- si MySQL responde error 1062 (duplicado), lanzar ValueError
    """
    if any(o["mes"] == mes and o["anio"] == anio for o in _OFRENDAS):
        raise ValueError("Ese mes ya tiene una ofrenda registrada.")
    nuevo_id = max((o["id_ofrenda"] for o in _OFRENDAS), default=0) + 1
    _OFRENDAS.append({"id_ofrenda": nuevo_id, "mes": mes, "anio": anio, "monto": float(monto),
                      "registrado_por": correo_usuario.split("@")[0].capitalize()})
    return nuevo_id


def actualizar_monto(id_ofrenda, monto):
    """Cambia el monto de una ofrenda ya registrada.

    TODO: UPDATE ofrendas SET monto = %s WHERE id_ofrenda = %s;
    """
    for o in _OFRENDAS:
        if o["id_ofrenda"] == id_ofrenda:
            o["monto"] = float(monto)
            return
