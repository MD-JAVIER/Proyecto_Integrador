"""
controlador_miembros.py
-----------------------
Reglas y preparación de datos del área de Miembros.
No dibuja nada y no sabe de dónde vienen los datos (solo usa datos_miembros.py).
"""
from datetime import date

from modulos.comunes import reglas_ministerios as reglas
from modulos.miembros import datos_miembros

POR_PAGINA = 6        # filas por página (cambiar aquí si se quiere otra cantidad)
DIAS_AVISO = 10        # desde estos días sin asistir se muestra el aviso
DIAS_INACTIVO = 15     # a los 15 días sin asistir pasa a inactivo (regla de asistencia)

_MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
          "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


# ---------- utilidades ----------
def fecha_larga(fecha):
    return f"{fecha.day} de {_MESES[fecha.month - 1]} de {fecha.year}" if fecha else "—"


def _dias_desde(fecha):
    return (date.today() - fecha).days if fecha else None


def texto_ultima_asistencia(fecha):
    dias = _dias_desde(fecha)
    if dias is None:
        return "Sin asistencias"
    if dias == 0:
        return "Hoy"
    if dias == 1:
        return "Ayer"
    return f"Hace {dias} días"


def _iniciales(nombres, apellidos):
    return (nombres[:1] + apellidos[:1]).upper()


def _hay_aviso(activo, fecha_ultima):
    """Aviso para quien está activo pero lleva varios días sin asistir."""
    dias = _dias_desde(fecha_ultima)
    return bool(activo) and dias is not None and DIAS_AVISO <= dias < DIAS_INACTIVO


# ---------- lectura ----------
def cargar_ministerios():
    return datos_miembros.listar_ministerios()


def cargar_resumen(id_ministerio=None):
    return datos_miembros.resumen_estados(id_ministerio)


def cargar_tabla(estado, id_ministerio, texto, pagina, solo_nuevos=False):
    """Devuelve {"filas", "total", "pagina", "paginas", "desde", "hasta"} listo para dibujar."""
    total = datos_miembros.contar_miembros(estado, id_ministerio, texto, solo_nuevos)
    paginas = max(1, -(-total // POR_PAGINA))          # división hacia arriba
    pagina = max(1, min(pagina, paginas))

    filas = []
    for m in datos_miembros.listar_miembros(estado, id_ministerio, texto, pagina, POR_PAGINA, solo_nuevos):
        dias = _dias_desde(m["ultima_asistencia"])
        filas.append({
            "id": m["id_miembro"],
            "nombre": f'{m["nombres"]} {m["apellidos"]}',
            "iniciales": _iniciales(m["nombres"], m["apellidos"]),
            "ministerios": ", ".join(m["ministerios"]) or "—",
            "telefono": m["telefono"] or "—",
            "ultima": texto_ultima_asistencia(m["ultima_asistencia"]),
            "aviso": _hay_aviso(m["activo"], m["ultima_asistencia"]),
            "dias": dias,
            "activo": bool(m["activo"]),
        })
    desde = (pagina - 1) * POR_PAGINA + 1 if total else 0
    hasta = desde + len(filas) - 1 if total else 0
    return {"filas": filas, "total": total, "pagina": pagina, "paginas": paginas,
            "desde": desde, "hasta": hasta}


def cargar_detalle(id_miembro):
    """Datos de un miembro para la ventana de detalle, o None."""
    m = datos_miembros.obtener_miembro(id_miembro)
    if m is None:
        return None
    return {
        "id": m["id_miembro"],
        "nombre": f'{m["nombres"]} {m["apellidos"]}',
        "iniciales": _iniciales(m["nombres"], m["apellidos"]),
        "activo": bool(m["activo"]),
        "telefono": m["telefono"] or "—",
        "direccion": m["direccion"] or "—",
        "nacimiento": f'{fecha_larga(m["fecha_nacimiento"])} ({reglas.calcular_edad(m["fecha_nacimiento"])} años)',
        "sexo": "Masculino" if m.get("sexo") == "M" else "Femenino" if m.get("sexo") == "F" else "—",
        "ingreso": fecha_larga(m["fecha_ingreso"]),
        "ministerios": ", ".join(m["ministerios"]) or "—",
        "ultima": texto_ultima_asistencia(m["ultima_asistencia"]),
        "aviso": _hay_aviso(m["activo"], m["ultima_asistencia"]),
        "datos": m,    # el diccionario original, para llenar el formulario de edición
    }


# ---------- regla de asistencia (15 días) ----------
def revisar_inactividad():
    """Pasa a inactivo a quien lleva 15 días o más sin asistir. Devuelve cuántos cambiaron.
    Se ejecuta al iniciar sesión y al entrar al Panel o a Miembros."""
    return datos_miembros.aplicar_regla_inactividad(DIAS_INACTIVO)


# ---------- regla de ministerio (edad y sexo) ----------
def id_ministerio_sugerido(fecha_nacimiento, sexo):
    """Id del ministerio que le corresponde por edad y sexo, o None si no corresponde ninguno."""
    nombre = reglas.ministerio_correspondiente(fecha_nacimiento, sexo) if sexo in ("M", "F") else None
    for id_min, nombre_min in datos_miembros.listar_ministerios():
        if nombre_min == nombre:
            return id_min
    return None


def texto_ayuda_ministerio(fecha_nacimiento, sexo):
    """Texto en vivo del formulario: 'Edad: 35 años · le corresponde: Caballeros'."""
    edad = reglas.calcular_edad(fecha_nacimiento)
    if edad < reglas.EDAD_MINIMA:
        return f"Edad: {edad} años · los ministerios son desde los 18 años"
    if sexo not in ("M", "F"):
        return f"Edad: {edad} años · seleccione el sexo para ver su ministerio"
    return f"Edad: {edad} años · le corresponde: {reglas.ministerio_correspondiente(fecha_nacimiento, sexo)}"


# ---------- escritura ----------
def validar(datos, ids_ministerios):
    """Devuelve la lista de errores (vacía si todo está bien)."""
    errores = []
    if len(datos["nombres"].strip()) < 2:
        errores.append("Escriba los nombres.")
    if len(datos["apellidos"].strip()) < 2:
        errores.append("Escriba los apellidos.")

    telefono = datos["telefono"].strip()
    digitos = sum(1 for c in telefono if c.isdigit())
    permitido = all(c.isdigit() or c in " +-()" for c in telefono)
    if not telefono or not permitido or not 8 <= digitos <= 15:
        errores.append("Escriba un teléfono válido (entre 8 y 15 números).")

    hoy = date.today()
    if datos["fecha_nacimiento"] >= hoy:
        errores.append("La fecha de nacimiento debe ser anterior a hoy.")
    if datos["fecha_ingreso"] > hoy:
        errores.append("La fecha de ingreso no puede ser futura.")
    elif datos["fecha_ingreso"] <= datos["fecha_nacimiento"]:
        errores.append("La fecha de ingreso debe ser posterior a la de nacimiento.")
    if datos.get("sexo") not in ("M", "F"):
        errores.append("Seleccione el sexo.")

    # Un solo ministerio, y debe ser el que le corresponde por edad y sexo
    if len(ids_ministerios) != 1:
        errores.append("Seleccione un ministerio (cada miembro pertenece a uno solo).")
    elif datos.get("sexo") in ("M", "F"):
        edad = reglas.calcular_edad(datos["fecha_nacimiento"])
        correcto = reglas.ministerio_correspondiente(datos["fecha_nacimiento"], datos["sexo"])
        elegido = dict(datos_miembros.listar_ministerios()).get(ids_ministerios[0])
        if correcto is None:
            errores.append(f"Tiene {edad} años: los ministerios son para personas de 18 años en adelante.")
        elif elegido != correcto:
            errores.append(f"Por su edad ({edad} años) y sexo le corresponde «{correcto}» "
                           f"({reglas.texto_regla(correcto)}), no «{elegido}».")
    return errores


def guardar(datos, ids_ministerios, id_miembro=None):
    """Crea (id_miembro=None) o actualiza un miembro. Devuelve su id."""
    limpio = {
        "nombres": datos["nombres"].strip(),
        "apellidos": datos["apellidos"].strip(),
        "telefono": datos["telefono"].strip(),
        "direccion": datos["direccion"].strip(),
        "sexo": datos["sexo"],
        "fecha_nacimiento": datos["fecha_nacimiento"],
        "fecha_ingreso": datos["fecha_ingreso"],
    }
    if id_miembro is None:
        return datos_miembros.crear_miembro(limpio, ids_ministerios)
    datos_miembros.actualizar_miembro(id_miembro, limpio, ids_ministerios)
    return id_miembro


def cambiar_estado(id_miembro, activo):
    datos_miembros.cambiar_estado(id_miembro, activo)
