"""
controlador_finanzas.py
-----------------------
Reglas y preparación de datos del área de Finanzas.
No dibuja nada y no sabe de dónde vienen los datos (solo usa datos_finanzas.py).
"""
from datetime import date

from modulos.dashboard.estilos_dashboard import VERDE_CLARO, GRIS
from modulos.finanzas import datos_finanzas

MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
         "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
LETRAS_MES = ["E", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]


# ---------- utilidades ----------
def formato_monto(monto):
    """1900.0 -> '1,900'   |   1900.5 -> '1,900.50'"""
    if float(monto) == int(monto):
        return f"{int(monto):,}"
    return f"{monto:,.2f}"


def mes_actual():
    return date.today().month


def anio_actual():
    return date.today().year


def nombre_mes_actual():
    return MESES[mes_actual() - 1]


def _ultimo_mes_visible(anio):
    """Hasta qué mes se puede registrar: el mes actual si es el año actual; si no, diciembre."""
    return mes_actual() if anio == anio_actual() else 12


def _ofrendas_dict(anio):
    return {o["mes"]: o for o in datos_finanzas.listar_ofrendas(anio)}


# ---------- lectura ----------
def cargar_anios():
    anios = set(datos_finanzas.listar_anios())
    anios.add(anio_actual())            # el año actual siempre está disponible
    return sorted(anios, reverse=True)


def mes_actual_pendiente():
    return mes_actual() not in _ofrendas_dict(anio_actual())


def cargar_resumen(anio):
    """Textos de las cuatro tarjetas de arriba."""
    ofrendas = _ofrendas_dict(anio)
    montos = {m: o["monto"] for m, o in ofrendas.items()}
    total = sum(montos.values())
    cantidad = len(montos)

    if montos:
        mejor_mes = max(montos, key=montos.get)
        mejor = (MESES[mejor_mes - 1], formato_monto(montos[mejor_mes]))
        promedio = formato_monto(round(total / cantidad, 2))
    else:
        mejor, promedio = ("—", ""), "0"

    if anio == anio_actual():
        mes = mes_actual()
        if mes in montos:
            tarjeta_mes = ("Mes actual", formato_monto(montos[mes]), f"{MESES[mes - 1]} {anio}")
        else:
            tarjeta_mes = ("Mes actual", "Pendiente", f"{MESES[mes - 1]} {anio}")
    else:
        tarjeta_mes = ("Meses registrados", f"{cantidad} de 12", str(anio))

    return {
        "total": (formato_monto(total), f"{cantidad} meses registrados"),
        "mes": tarjeta_mes,
        "mejor": ("Mejor mes", mejor[0], mejor[1]),
        "promedio": ("Promedio mensual", promedio, "de los meses registrados"),
    }


def cargar_grafico(anio):
    """Lista de (letra, valor, color, tooltip) para los 12 meses.

    Igual que el gráfico del Panel: los meses con ofrenda igual o mayor al promedio
    van en verde claro y el resto en gris. Los meses sin registro quedan como un punto.
    """
    montos = {m: o["monto"] for m, o in _ofrendas_dict(anio).items()}
    promedio = sum(montos.values()) / len(montos) if montos else 0

    datos = []
    for mes in range(1, 13):
        valor = montos.get(mes, 0.0)
        color = VERDE_CLARO if (valor > 0 and valor >= promedio) else GRIS
        texto = f"{MESES[mes - 1]} {anio}: " + (formato_monto(valor) if mes in montos else "sin registrar")
        datos.append((LETRAS_MES[mes - 1], valor, color, texto))
    return datos


def cargar_historial(anio):
    """Filas del historial, del mes más reciente al más antiguo."""
    ofrendas = _ofrendas_dict(anio)
    filas = []
    for mes in range(_ultimo_mes_visible(anio), 0, -1):
        o = ofrendas.get(mes)
        filas.append({
            "mes": mes,
            "nombre_mes": MESES[mes - 1],
            "id": o["id_ofrenda"] if o else None,
            "monto": o["monto"] if o else None,
            "monto_texto": formato_monto(o["monto"]) if o else None,
            "registrado_por": o["registrado_por"] if o else "—",
            "pendiente": o is None,
        })
    return filas


def meses_disponibles(anio):
    """Meses que todavía se pueden registrar: [(número, nombre), ...] en orden."""
    registrados = _ofrendas_dict(anio)
    return [(m, MESES[m - 1]) for m in range(1, _ultimo_mes_visible(anio) + 1) if m not in registrados]


# ---------- escritura ----------
def validar(mes, anio, monto, id_ofrenda=None):
    """Devuelve la lista de errores (vacía si todo está bien)."""
    errores = []
    if mes is None:
        errores.append("Seleccione el mes.")
    elif anio == anio_actual() and mes > mes_actual():
        errores.append("No se puede registrar un mes que todavía no llega.")
    elif id_ofrenda is None and mes in _ofrendas_dict(anio):
        errores.append("Ese mes ya tiene una ofrenda registrada; edítela desde el historial.")
    if monto <= 0:
        errores.append("Escriba un monto mayor que cero.")
    return errores


def guardar(mes, anio, monto, correo_usuario, id_ofrenda=None):
    """Registra una ofrenda nueva o cambia el monto de una existente. Devuelve su id."""
    if id_ofrenda is None:
        return datos_finanzas.registrar_ofrenda(mes, anio, monto, correo_usuario)
    datos_finanzas.actualizar_monto(id_ofrenda, monto)
    return id_ofrenda
