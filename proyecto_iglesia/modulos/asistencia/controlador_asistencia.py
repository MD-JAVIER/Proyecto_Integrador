"""
controlador_asistencia.py
-------------------------
Reglas y preparación de datos del área de Asistencia (la usa el LÍDER).
No dibuja nada y no sabe de dónde vienen los datos (solo usa datos_asistencia.py).

Reglas:
  - El líder solo ve a los miembros de SU ministerio.
  - Solo se puede registrar asistencia de cultos ya realizados (hasta hoy) y de los últimos 7 días.
  - Los cultos cancelados no se pueden registrar.
  - Quien asiste queda activo; quien pasa 15 días sin asistir pasa a inactivo.
"""
from datetime import date, timedelta

from modulos.actividades import controlador_actividades as actividades
from modulos.asistencia import datos_asistencia
from modulos.miembros import controlador_miembros as miembros

DIAS_REGISTRABLES = 7


def cargar_cultos(id_ministerio):
    """Cultos que el líder puede registrar: [{'id', 'texto'}], del más reciente al más antiguo."""
    hoy = date.today()
    resultado = []
    for c in datos_asistencia.listar_cultos(id_ministerio, hoy - timedelta(days=DIAS_REGISTRABLES), hoy):
        ambito = actividades.texto_ambito(c["id_ministerio"])
        resultado.append({
            "id": c["id_evento"],
            "texto": f'{c["nombre"]} · {actividades.texto_fecha_corta(c["fecha"])} ({ambito})',
        })
    return resultado


def cargar_lista(id_evento, id_ministerio):
    """Filas para marcar: miembros del ministerio con su estado y si ya tienen asistencia guardada."""
    marcas = datos_asistencia.obtener_marcas(id_evento)
    filas = []
    for m in datos_asistencia.listar_miembros(id_ministerio):
        filas.append({
            "id": m["id_miembro"],
            "nombre": f'{m["nombres"]} {m["apellidos"]}',
            "iniciales": (m["nombres"][:1] + m["apellidos"][:1]).upper(),
            "activo": bool(m["activo"]),
            "ultima": miembros.texto_ultima_asistencia(m["ultima_asistencia"]),
            "aviso": miembros._hay_aviso(m["activo"], m["ultima_asistencia"]),
            "presente": marcas.get(m["id_miembro"], False),
        })
    return filas


def guardar(id_evento, marcas):
    """Guarda la asistencia y vuelve a revisar la regla de los 15 días.
    Devuelve {"presentes": n, "reactivados": n, "inactivados": n}."""
    reactivados = datos_asistencia.guardar_asistencia(id_evento, marcas)
    inactivados = miembros.revisar_inactividad()
    return {"presentes": sum(1 for p in marcas.values() if p),
            "reactivados": reactivados, "inactivados": inactivados}
