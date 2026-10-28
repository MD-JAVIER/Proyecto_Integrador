"""
reglas_ministerios.py
---------------------
Regla única para saber a qué ministerio corresponde una persona.
La usan el área de Miembros (al registrar) y el área de Líderes (al nombrar líderes),
para que ambas apliquen exactamente lo mismo.

    18 a 29 años .............. Jóvenes (hombres y mujeres)
    30 años o más, hombre ..... Caballeros
    30 años o más, mujer ...... Damas
    menor de 18 años .......... no tiene ministerio
"""
from datetime import date

EDAD_MINIMA = 18
EDAD_ADULTO = 30            # desde esta edad se pasa a Caballeros o Damas

JOVENES = "Jóvenes"
CABALLEROS = "Caballeros"
DAMAS = "Damas"

REGLAS = {
    JOVENES: "personas de 18 a 29 años",
    CABALLEROS: "hombres de 30 años en adelante",
    DAMAS: "mujeres de 30 años en adelante",
}


def calcular_edad(fecha_nacimiento, hoy=None):
    """Años cumplidos a la fecha de hoy."""
    hoy = hoy or date.today()
    return hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))


def ministerio_correspondiente(fecha_nacimiento, sexo):
    """Devuelve el nombre del ministerio que le toca por edad y sexo ('M' o 'F'), o None si es menor de 18."""
    edad = calcular_edad(fecha_nacimiento)
    if edad < EDAD_MINIMA:
        return None
    if edad < EDAD_ADULTO:
        return JOVENES
    return CABALLEROS if sexo == "M" else DAMAS


def texto_regla(nombre_ministerio):
    """Frase para mostrar al usuario, por ejemplo: 'hombres de 30 años en adelante'."""
    return REGLAS.get(nombre_ministerio, "")


# ---------- cultos de la semana ----------
# día de la semana (lunes = 0 ... domingo = 6)
DIAS_CULTO_GENERAL = (4, 6)                        # viernes y domingo: de toda la iglesia
DIA_CULTO_MINISTERIO = {DAMAS: 2, JOVENES: 5}      # miércoles = Damas, sábado = Jóvenes (Caballeros no tiene)
