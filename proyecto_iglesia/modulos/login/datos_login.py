"""
datos_login.py
--------------
ÚNICO archivo del login que habla con los datos.

AHORA: usa datos de prueba (sin base de datos) para poder probar el login.
DESPUÉS: Marcos reemplaza el cuerpo de la función con la consulta real
a la base de datos "grupo" (MySQL, puerto 3303).
El nombre de la función y lo que devuelve NO deben cambiar.
"""

# --- DATOS DE PRUEBA (borrar cuando se conecte la base de datos) ---
_USUARIOS_PRUEBA = {
    # correo: (clave, rol)
    "pastor@iglesia.org": ("1234", "Administrador"),
    "lider@iglesia.org": ("1234", "Líder"),       # líder de Jóvenes (de prueba)
    "damas@iglesia.org": ("1234", "Líder"),       # líder de Damas (de prueba)
}


def buscar_usuario(correo):
    """Busca un usuario por su correo.

    Debe devolver: (clave, rol)  o  None si el usuario no existe o está inactivo.

    TODO (Marcos):
        SELECT u.clave, r.nombre_rol
        FROM usuarios u
        JOIN roles r ON r.id_rol = u.id_rol
        WHERE u.correo = %s AND u.activo = 1;
    Notas:
      - En la tabla usuarios el campo de ingreso es "correo" (antes "usuario").
      - La clave debe guardarse cifrada (hash) en la base de datos.
    """
    return _USUARIOS_PRUEBA.get(correo.lower())


# ---------- accesos de los líderes (los crea el pastor al nombrar un líder) ----------
def existe_correo(correo):
    """True si ya hay un usuario con ese correo.

    TODO: SELECT COUNT(*) FROM usuarios WHERE correo = %s;
    """
    return correo.strip().lower() in _USUARIOS_PRUEBA


def crear_usuario(correo, clave, rol):
    """Crea el acceso de un usuario (en la base real forma parte de la misma transacción
    que crea al líder; la clave se guarda CIFRADA con bcrypt o argon2, nunca en texto plano).

    TODO: INSERT INTO usuarios (nombre, correo, clave, id_rol, activo)
          VALUES (%s, %s, <clave cifrada>, (SELECT id_rol FROM roles WHERE nombre_rol = %s), 1);
    """
    _USUARIOS_PRUEBA[correo.strip().lower()] = (clave, rol)


def eliminar_usuario(correo):
    """Quita el acceso de un usuario (cuando se elimina a un líder).

    TODO: UPDATE usuarios SET activo = 0 WHERE correo = %s;
    """
    _USUARIOS_PRUEBA.pop(correo.strip().lower(), None)
