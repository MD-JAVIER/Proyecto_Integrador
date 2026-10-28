"""
controlador_login.py
--------------------
Lógica del login. No dibuja nada y no sabe de dónde vienen los datos:
solo usa la función de datos_login.py.
"""
from modulos.login import datos_login


def validar_login(correo, clave):
    """Valida las credenciales.

    Devuelve una tupla (ok, mensaje, rol):
        (True,  "",               "Administrador")  -> ingreso correcto
        (False, "texto del error", "")              -> ingreso rechazado
    El rol sale de la cuenta del usuario, no se elige en la pantalla.
    """
    correo = correo.strip()

    if not correo or not clave:
        return False, "Ingrese su correo y contraseña.", ""

    if "@" not in correo:
        return False, "Ingrese un correo válido.", ""

    datos = datos_login.buscar_usuario(correo)
    if datos is None:
        return False, "Correo o contraseña incorrectos.", ""

    clave_guardada, rol = datos
    if clave != clave_guardada:
        return False, "Correo o contraseña incorrectos.", ""

    return True, "", rol
