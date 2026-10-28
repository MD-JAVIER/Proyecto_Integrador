"""
controlador_actividades.py
--------------------------
Reglas y preparación de datos del área de Actividades.
No dibuja nada y no sabe de dónde vienen los datos (solo usa datos_actividades.py).

El parámetro `vista` dice quién está mirando:
    None   -> el PASTOR: gestiona las actividades generales y solo VE los cultos de los ministerios.
    número -> el LÍDER de ese ministerio: gestiona las suyas y solo VE las generales.
"""
from datetime import date, timedelta

from modulos.actividades import datos_actividades
from modulos.comunes import reglas_ministerios as reglas

POR_PAGINA = 6
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
NOMBRE_TIPO = {"Culto": "Culto", "Externo": "Evento externo"}


# ---------- ministerios ----------
def _nombres_ministerios():
    return dict(datos_actividades.listar_ministerios())          # {id: nombre}


def texto_ambito(id_ministerio):
    """'General' o el nombre del ministerio dueño de la actividad."""
    return "General" if id_ministerio is None else _nombres_ministerios().get(id_ministerio, "—")


def _dia_culto_del_ministerio(id_ministerio):
    """Día de la semana del culto de un ministerio (miércoles = Damas, sábado = Jóvenes) o None."""
    return reglas.DIA_CULTO_MINISTERIO.get(_nombres_ministerios().get(id_ministerio))


def dias_de_culto_permitidos(vista):
    """Días en que esa vista puede crear un Culto: el pastor, viernes y domingo; el líder, el de su ministerio."""
    if vista is None:
        return reglas.DIAS_CULTO_GENERAL
    dia = _dia_culto_del_ministerio(vista)
    return (dia,) if dia is not None else ()


def tipos_permitidos(vista):
    """Opciones del formulario: [(valor, texto), ...]. Caballeros no tiene culto propio."""
    tipos = []
    if dias_de_culto_permitidos(vista):
        tipos.append(("Culto", "Culto"))
    tipos.append(("Externo", "Evento externo"))
    return tipos


def puede_gestionar(id_ministerio_dueno, vista):
    """El pastor gestiona lo general; el líder, lo de su ministerio."""
    return id_ministerio_dueno == vista


# ---------- utilidades de formato ----------
def texto_hora(hora):
    """time(19, 0) -> '7:00 pm'"""
    h = hora.hour % 12 or 12
    return f"{h}:{hora.minute:02d} {'am' if hora.hour < 12 else 'pm'}"


def texto_fecha_larga(fecha):
    """14 de octubre"""
    return f"{fecha.day} de {MESES[fecha.month - 1]}"


def texto_fecha_corta(fecha):
    """Mié 14 oct"""
    return f"{DIAS[fecha.weekday()][:3]} {fecha.day} {MESES[fecha.month - 1][:3]}"


def situacion(actividad):
    """Programada, Realizada o Cancelada (la 'realizada' se calcula por la fecha)."""
    if actividad["estado"] == "Cancelado":
        return "Cancelada"
    return "Realizada" if actividad["fecha"] < date.today() else "Programada"


# ---------- lectura ----------
def cargar_resumen(vista=None):
    """Cifras del mes actual para las tarjetas."""
    hoy = date.today()
    return datos_actividades.resumen_mes(hoy.year, hoy.month, vista)


def cargar_semana(vista=None):
    """Los cultos de la semana actual que esa vista puede ver.

    Pastor: miércoles (Damas), viernes (general), sábado (Jóvenes) y domingo (general).
    Líder: los dos generales y el culto de su propio ministerio (si tiene).
    Si el culto todavía no existe, 'creada' es False; 'puede_crear' dice si esa vista puede crearlo.
    """
    hoy = date.today()
    lunes = hoy - timedelta(days=hoy.weekday())
    ids_por_nombre = {nombre: id_min for id_min, nombre in _nombres_ministerios().items()}

    # (día, dueño)
    cultos = [(dia, None) for dia in reglas.DIAS_CULTO_GENERAL]
    for nombre, dia in reglas.DIA_CULTO_MINISTERIO.items():
        dueno = ids_por_nombre.get(nombre)
        if vista is None or vista == dueno:        # el líder solo ve el culto de SU ministerio
            cultos.append((dia, dueno))
    cultos.sort()

    existentes = {(a["fecha"], a["id_ministerio"]): a
                  for a in datos_actividades.actividades_entre(lunes, lunes + timedelta(days=6), vista)
                  if a["tipo"] == "Culto"}
    tarjetas = []
    for dia, dueno in cultos:
        fecha = lunes + timedelta(days=dia)
        actividad = existentes.get((fecha, dueno))
        gestionable = puede_gestionar(dueno, vista)
        tarjetas.append({
            "dia": DIAS[dia],
            "fecha": fecha,
            "fecha_texto": texto_fecha_larga(fecha),
            "es_hoy": fecha == hoy,
            "ambito": texto_ambito(dueno),
            "creada": actividad is not None,
            "id": actividad["id_evento"] if actividad else None,
            "hora": texto_hora(actividad["hora"]) if actividad else "",
            "lugar": actividad["lugar"] if actividad else "",
            "situacion": situacion(actividad) if actividad else "Sin crear",
            "gestionable": gestionable,
            "puede_crear": gestionable and actividad is None,
        })
    return tarjetas


def cargar_tabla(tipo, sit, texto, pagina, vista=None):
    """Devuelve {"filas", "total", "pagina", "paginas", "desde", "hasta"} listo para dibujar."""
    total = datos_actividades.contar_actividades(tipo, sit, texto, vista)
    paginas = max(1, -(-total // POR_PAGINA))
    pagina = max(1, min(pagina, paginas))

    filas = []
    for a in datos_actividades.listar_actividades(tipo, sit, texto, pagina, POR_PAGINA, vista):
        estado = situacion(a)
        gestionable = puede_gestionar(a["id_ministerio"], vista)
        filas.append({
            "id": a["id_evento"],
            "nombre": a["nombre"],
            "ambito": texto_ambito(a["id_ministerio"]),
            "tipo": NOMBRE_TIPO[a["tipo"]],
            "fecha": texto_fecha_corta(a["fecha"]),
            "hora": texto_hora(a["hora"]),
            "lugar": a["lugar"],
            "situacion": estado,
            "gestionable": gestionable,
            "se_puede_cancelar": gestionable and estado == "Programada",
            "cancelada": estado == "Cancelada",
        })
    desde = (pagina - 1) * POR_PAGINA + 1 if total else 0
    hasta = desde + len(filas) - 1 if total else 0
    return {"filas": filas, "total": total, "pagina": pagina, "paginas": paginas,
            "desde": desde, "hasta": hasta}


def cargar_actividad(id_evento):
    """El diccionario original de una actividad, para llenar el formulario de edición."""
    return datos_actividades.obtener_actividad(id_evento)


# ---------- escritura ----------
def validar(datos, id_evento=None, vista=None):
    """Devuelve la lista de errores (vacía si todo está bien). `vista` = quién está guardando."""
    errores = []
    if len(datos["nombre"].strip()) < 3:
        errores.append("Escriba el nombre de la actividad.")
    if len(datos["lugar"].strip()) < 2:
        errores.append("Escriba el lugar.")
    if len(datos["descripcion"]) > 250:
        errores.append("La descripción no puede pasar de 250 caracteres.")

    if datos["tipo"] == "Culto":
        permitidos = dias_de_culto_permitidos(vista)
        if not permitidos:
            errores.append("Este ministerio no tiene un culto propio. Use «Evento externo».")
        elif datos["fecha"].weekday() not in permitidos:
            dias = " y ".join(DIAS[d].lower() for d in permitidos)
            quien = "Los cultos generales son" if vista is None else "El culto de tu ministerio es"
            errores.append(f"{quien} el {dias}. Para otro día use «Evento externo».")
        elif datos_actividades.existe_culto(datos["fecha"], id_evento, vista):
            errores.append("Ya hay un culto registrado ese día.")
    return errores


def guardar(datos, id_evento=None, vista=None):
    """Crea (id_evento=None) o actualiza una actividad. Devuelve su id.
    Al crear, la actividad queda a nombre de quien la guarda: general (pastor) o su ministerio (líder)."""
    limpio = {
        "nombre": datos["nombre"].strip(),
        "tipo": datos["tipo"],
        "fecha": datos["fecha"],
        "hora": datos["hora"],
        "lugar": datos["lugar"].strip(),
        "descripcion": datos["descripcion"].strip(),
    }
    if id_evento is None:
        limpio["id_ministerio"] = vista
        return datos_actividades.crear_actividad(limpio)
    datos_actividades.actualizar_actividad(id_evento, limpio)
    return id_evento


def cancelar(id_evento):
    datos_actividades.cambiar_estado(id_evento, "Cancelado")


def reactivar(id_evento):
    datos_actividades.cambiar_estado(id_evento, "Programado")
