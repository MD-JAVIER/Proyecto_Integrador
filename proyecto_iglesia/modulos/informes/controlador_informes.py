"""
controlador_informes.py
-----------------------
Arma el contenido de los informes (números y textos ya listos) y le pide a generador_docx.py
que los escriba en el formato de la institución. No dibuja pantallas.

Importante: el informe de miembros muestra el estado ACTUAL del sistema (el sistema no guarda un
historial de cómo estaba un mes pasado); solo "Nuevos miembros" se cuenta dentro del período elegido.
"""
import calendar
from datetime import date

from modulos.comunes import configuracion
from modulos.comunes import reglas_ministerios as reglas
from modulos.finanzas import controlador_finanzas as finanzas
from modulos.informes import datos_informes, generador_docx

MESES = finanzas.MESES            # "Enero" ... "Diciembre"
ORDEN_CLASIFICACION = ["Caballeros", "Damas", "Jóvenes"]      # el orden de la plantilla de la institución


# ---------- ajustes ----------
def nombre_iglesia_guardado():
    return configuracion.obtener("nombre_iglesia", "")


def recordar_nombre_iglesia(nombre):
    configuracion.guardar("nombre_iglesia", nombre.strip())


def anios_para_miembros():
    hoy = date.today().year
    return [hoy, hoy - 1, hoy - 2]


def anios_para_ofrendas():
    return finanzas.cargar_anios()


def nombre_ministerio(id_ministerio):
    return datos_informes.nombre_ministerio(id_ministerio)


def nombre_archivo(tipo, anio, mes=None, ministerio=""):
    if tipo == "miembros":
        return f"Informe_General_de_Miembros_{anio}-{mes:02d}.docx"
    if tipo == "ministerio":
        return f"Informe_de_Miembros_{ministerio}_{anio}-{mes:02d}.docx".replace(" ", "_")
    return f"Informe_General_de_Ofrendas_{anio}.docx"


# ---------- formato de números ----------
def _monto(valor):
    return finanzas.formato_monto(valor)


# ======================= INFORME DE MIEMBROS =======================
def datos_informe_miembros(iglesia, anio, mes, observaciones):
    hoy = date.today()
    resumen = datos_informes.resumen_miembros()
    total, activos, inactivos = resumen["total"], resumen["activos"], resumen["inactivos"]

    por_ministerio = dict(datos_informes.contar_por_ministerio())
    clasificacion = []
    for nombre in ORDEN_CLASIFICACION:
        regla = reglas.texto_regla(nombre)
        clasificacion.append((str(por_ministerio.get(nombre, 0)), regla[:1].upper() + regla[1:]))
    clasificacion.append((str(total), "Cada miembro se cuenta una sola vez"))                   # TOTAL

    desde = date(anio, mes, 1)
    hasta = date(anio, mes, calendar.monthrange(anio, mes)[1])
    ingresos = datos_informes.ingresos_en_periodo(desde, hasta)
    nombres = [f"{n} {a}" for n, a, _ in ingresos]
    detalle_nuevos = ", ".join(nombres[:4]) + (f" y {len(nombres) - 4} más" if len(nombres) > 4 else "")
    movimientos = [(str(len(ingresos)), detalle_nuevos or "Ninguno en el período")]      # solo nuevos miembros

    return {
        "iglesia": iglesia,
        "periodo": f"{MESES[mes - 1]} {anio}",
        "fecha": hoy,
        "resumen": (str(total), str(activos), str(inactivos)),
        "clasificacion": clasificacion,
        "movimientos": movimientos,
        "observaciones": observaciones,
        "nota": f"Informe generado por el sistema Ekklesia el {hoy.day:02d}/{hoy.month:02d}/{hoy.year}. "
                "Cada miembro se cuenta una sola vez.",
    }


def generar_informe_miembros(ruta, iglesia, anio, mes, observaciones=""):
    generador_docx.generar_informe_miembros(ruta, datos_informe_miembros(iglesia, anio, mes, observaciones))


# ======================= INFORME DE OFRENDAS =======================
def datos_informe_ofrendas(iglesia, anio, observaciones):
    hoy = date.today()
    del_anio = datos_informes.ofrendas_del_anio(anio)
    montos = {mes: o["monto"] for mes, o in del_anio.items()}
    total = sum(montos.values())
    cantidad = len(montos)

    if montos:
        mejor = max(montos, key=montos.get)
        mejor_texto = f"{MESES[mejor - 1]} ({_monto(montos[mejor])})"
        promedio = _monto(round(total / cantidad, 2))
    else:
        mejor_texto, promedio = "—", "—"

    ultimo_mes = hoy.month if anio == hoy.year else 12
    meses = []
    for mes in range(1, 13):
        if mes in del_anio:
            meses.append((MESES[mes - 1], _monto(montos[mes]), f"Registrado por {del_anio[mes]['registrado_por']}"))
        elif mes <= ultimo_mes:
            meses.append((MESES[mes - 1], "—", "Pendiente de registrar"))
        else:
            meses.append((MESES[mes - 1], "—", "Aún no corresponde"))

    return {
        "iglesia": iglesia,
        "periodo": f"Año {anio}",
        "fecha": hoy,
        "resumen": (_monto(total), str(cantidad), promedio, mejor_texto),
        "meses": meses,
        "total": (_monto(total), f"{cantidad} meses registrados"),
        "observaciones": observaciones,
        "nota": f"Informe generado por el sistema Ekklesia el {hoy.day:02d}/{hoy.month:02d}/{hoy.year}.",
    }


def generar_informe_ofrendas(ruta, iglesia, anio, observaciones=""):
    generador_docx.generar_informe_ofrendas(ruta, datos_informe_ofrendas(iglesia, anio, observaciones))


# ======================= INFORME REDUCIDO DE UN MINISTERIO =======================
def datos_informe_ministerio(id_ministerio, iglesia, anio, mes, observaciones):
    """Lo mismo que el informe general, pero solo con los miembros de ese ministerio."""
    hoy = date.today()
    resumen = datos_informes.resumen_miembros(id_ministerio)
    total, activos, inactivos = resumen["total"], resumen["activos"], resumen["inactivos"]

    desde = date(anio, mes, 1)
    hasta = date(anio, mes, calendar.monthrange(anio, mes)[1])
    ingresos = datos_informes.ingresos_en_periodo(desde, hasta, id_ministerio)
    nombres = [f"{n} {a}" for n, a, _ in ingresos]
    detalle = ", ".join(nombres[:4]) + (f" y {len(nombres) - 4} más" if len(nombres) > 4 else "")

    return {
        "iglesia": iglesia,
        "ministerio": nombre_ministerio(id_ministerio),
        "periodo": f"{MESES[mes - 1]} {anio}",
        "fecha": hoy,
        "resumen": (str(total), str(activos), str(inactivos)),
        "movimientos": [(str(len(ingresos)), detalle or "Ninguno en el período")],
        "observaciones": observaciones,
        "nota": f"Informe generado por el sistema Ekklesia el {hoy.day:02d}/{hoy.month:02d}/{hoy.year}. "
                "Cada miembro se cuenta una sola vez.",
    }


def generar_informe_ministerio(ruta, id_ministerio, iglesia, anio, mes, observaciones=""):
    generador_docx.generar_informe_ministerio(
        ruta, datos_informe_ministerio(id_ministerio, iglesia, anio, mes, observaciones))
