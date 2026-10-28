"""
controlador_dashboard.py
------------------------
Toma los datos de datos_dashboard.py y los deja listos para dibujar.
No dibuja nada y no sabe de dónde vienen los datos.
"""
from datetime import date

from modulos.dashboard import datos_dashboard
from modulos.dashboard.estilos_dashboard import VERDE_OSCURO, VERDE_CLARO, GRIS

LETRAS_MES = ["E", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]


def obtener_nombre_y_correo(correo):
    return datos_dashboard.nombre_usuario(correo), correo


def datos_resumen():
    """{"total", "jovenes", "damas", "caballeros"}"""
    return datos_dashboard.resumen_miembros()


def datos_ofrendas(cantidad_meses=7):
    """Lista de (letra_del_mes, total, color, texto_del_tooltip) de los últimos meses.

    Los meses con ofrenda igual o mayor al promedio se pintan de verde;
    el resto, de gris (así se ve de un vistazo cuáles fueron los mejores meses).
    """
    hoy = date.today()

    # Lista de (año, mes) desde hace N meses hasta el mes actual
    periodos = []
    anio, mes = hoy.year, hoy.month
    for _ in range(cantidad_meses):
        periodos.append((anio, mes))
        mes -= 1
        if mes == 0:
            mes, anio = 12, anio - 1
    periodos.reverse()

    # Se consulta cada año una sola vez
    por_anio = {}
    for a, _ in periodos:
        if a not in por_anio:
            por_anio[a] = datos_dashboard.ofrendas_por_mes(a)

    totales = [por_anio[a].get(m, 0.0) for a, m in periodos]
    promedio = sum(totales) / len(totales) if totales else 0

    resultado = []
    for (a, m), total in zip(periodos, totales):
        color = VERDE_CLARO if (total > 0 and total >= promedio) else GRIS
        tooltip = f"{datos_dashboard.nombre_mes(m).capitalize()} {a}: {total:,.2f}"
        resultado.append((LETRAS_MES[m - 1], total, color, tooltip))
    return resultado


def datos_estado_miembros():
    """Lista para el gráfico 'P y A': activos e inactivos con su porcentaje."""
    activos, inactivos = datos_dashboard.miembros_activos_inactivos()
    total = activos + inactivos
    if total == 0:
        return [("0 %", 0, VERDE_OSCURO, "Activos: 0"), ("0 %", 0, VERDE_CLARO, "Inactivos: 0")]

    p_activos = round(activos * 100 / total)
    p_inactivos = 100 - p_activos
    return [
        (f"{p_activos} %", p_activos, VERDE_OSCURO, f"Activos: {activos}"),
        (f"{p_inactivos} %", p_inactivos, VERDE_CLARO, f"Inactivos: {inactivos}"),
    ]


def datos_lideres():
    return datos_dashboard.lideres()


def datos_actividades():
    """Lista de (nombre, 'Fecha: 7 de octubre')."""
    resultado = []
    for nombre, fecha in datos_dashboard.actividades_proximas():
        texto = f"Fecha: {fecha.day} de {datos_dashboard.nombre_mes(fecha.month)}"
        resultado.append((nombre, texto))
    return resultado
