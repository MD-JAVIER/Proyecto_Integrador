"""
controlador_lideres.py
----------------------
Reglas y preparación de datos del área de Líderes.
No dibuja nada y no sabe de dónde vienen los datos (solo usa datos_lideres.py).

Reglas:
  1. Un miembro solo puede ser líder de UN ministerio.
  2. Debe cumplir la edad y el sexo del ministerio (Jóvenes 18 a 29; Caballeros: hombres de 30
     en adelante; Damas: mujeres de 30 en adelante). Es la misma regla de modulos/comunes/reglas_ministerios.py
"""
from modulos.comunes import reglas_ministerios as reglas
from modulos.lideres import datos_lideres


def _iniciales(nombres, apellidos):
    return (nombres[:1] + apellidos[:1]).upper()


# ---------- lectura ----------
def cargar_ministerios():
    """Cada ministerio con sus líderes: lista de diccionarios para dibujar las tarjetas."""
    lideres = datos_lideres.listar_lideres()
    resultado = []
    for id_ministerio, nombre in datos_lideres.listar_ministerios():
        de_este = [{
            "id_lider": l["id_lider"],
            "nombre": f'{l["nombres"]} {l["apellidos"]}',
            "iniciales": _iniciales(l["nombres"], l["apellidos"]),
            "telefono": l["telefono"] or "—",
            "correo": l["correo"],
            "activo": bool(l["activo"]),
        } for l in lideres if l["id_ministerio"] == id_ministerio]
        resultado.append({"id": id_ministerio, "nombre": nombre, "lideres": de_este})
    return resultado


def cargar_resumen():
    """Cifras de las tarjetas de arriba."""
    ministerios = cargar_ministerios()
    con_lider = sum(1 for m in ministerios if m["lideres"])
    return {
        "lideres": sum(len(m["lideres"]) for m in ministerios),
        "con_lider": con_lider,
        "sin_lider": len(ministerios) - con_lider,
    }


def cargar_ministerios_lista():
    return datos_lideres.listar_ministerios()


def _nombre_ministerio(id_ministerio):
    return dict(datos_lideres.listar_ministerios()).get(id_ministerio)


def texto_regla_ministerio(id_ministerio):
    """Por ejemplo: 'Caballeros: hombres de 30 años en adelante'."""
    nombre = _nombre_ministerio(id_ministerio)
    return f"{nombre}: {reglas.texto_regla(nombre)}" if nombre else ""


def cargar_candidatos(id_ministerio):
    """Miembros que SÍ se pueden nombrar líderes de ese ministerio (activos, sin ser líderes
    y que cumplen su edad y sexo): lista de (id_miembro, 'Nombre Apellido')."""
    nombre = _nombre_ministerio(id_ministerio)
    return [(id_m, f"{nombres} {apellidos}")
            for id_m, nombres, apellidos, nacimiento, sexo in datos_lideres.listar_candidatos()
            if reglas.ministerio_correspondiente(nacimiento, sexo) == nombre]


# ---------- escritura ----------
def validar(id_miembro, id_ministerio, correo="", clave=""):
    """Devuelve la lista de errores (vacía si todo está bien)."""
    errores = []
    correo = correo.strip()
    if "@" not in correo or "." not in correo.split("@")[-1] or " " in correo:
        errores.append("Escriba un correo válido: será el usuario con el que el líder inicia sesión.")
    elif datos_lideres.existe_correo(correo):
        errores.append("Ese correo ya tiene acceso al sistema; use otro.")
    if len(clave) < 6:
        errores.append("La contraseña temporal debe tener al menos 6 caracteres.")
    if id_miembro is None:
        errores.append("Seleccione un miembro de la lista.")
    if id_ministerio is None:
        errores.append("Seleccione el ministerio que va a liderar.")
    if id_miembro is not None:
        actual = datos_lideres.ministerio_de_lider(id_miembro)
        if actual is not None:
            errores.append(f"Ese miembro ya es líder de «{_nombre_ministerio(actual)}». "
                           "Un miembro solo puede liderar un ministerio.")
        elif id_ministerio is not None:
            m = datos_lideres.obtener_miembro(id_miembro)
            edad = reglas.calcular_edad(m["fecha_nacimiento"])
            ministerio = _nombre_ministerio(id_ministerio)
            if reglas.ministerio_correspondiente(m["fecha_nacimiento"], m["sexo"]) != ministerio:
                errores.append(f'{m["nombres"]} {m["apellidos"]} tiene {edad} años y no cumple para liderar '
                               f"«{ministerio}»: ese ministerio es para {reglas.texto_regla(ministerio)}.")
    return errores


def guardar(id_miembro, id_ministerio, correo, clave):
    """Nombra al líder y crea su acceso (correo y contraseña temporal)."""
    return datos_lideres.crear_lider(id_miembro, id_ministerio, correo.strip(), clave)


def eliminar(id_lider):
    datos_lideres.eliminar_lider(id_lider)


# ---------- para la pantalla del líder ----------
def ministerio_por_correo(correo):
    """Id del ministerio que lidera el usuario con ese correo (o None)."""
    return datos_lideres.ministerio_por_correo(correo)


def nombre_por_correo(correo):
    return datos_lideres.nombre_por_correo(correo)


def nombre_ministerio(id_ministerio):
    return _nombre_ministerio(id_ministerio)
