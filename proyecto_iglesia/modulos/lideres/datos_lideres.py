"""
datos_lideres.py
----------------
ÚNICO archivo del área de Líderes que habla con los datos.

AHORA: usa líderes de prueba guardados en memoria (si se cierra el programa,
los cambios se pierden). Así el área funciona completa.
DESPUÉS: se reemplaza el cuerpo de cada función por su consulta SQL
(el SQL está en el comentario TODO de cada una).
Los nombres de las funciones, sus parámetros y lo que devuelven NO deben cambiar.

NUEVA TABLA que necesita la base de datos (la novena):

    CREATE TABLE lideres (
        id_lider      INT AUTO_INCREMENT PRIMARY KEY,
        id_miembro    INT NOT NULL UNIQUE,    -- UNIQUE = un miembro solo puede ser líder de UN ministerio
        id_ministerio INT NOT NULL,
        id_usuario    INT NOT NULL UNIQUE,    -- el acceso (correo y clave) con el que el líder inicia sesión
        FOREIGN KEY (id_miembro)    REFERENCES miembros(id_miembro),
        FOREIGN KEY (id_usuario)    REFERENCES usuarios(id_usuario),
        FOREIGN KEY (id_ministerio) REFERENCES ministerios(id_ministerio)
    ) ENGINE=InnoDB;

Un líder es un MIEMBRO de la iglesia al que se le asigna un ministerio.
Quitar a un líder borra esta asignación y desactiva su acceso: la persona sigue siendo miembro.
"""
from modulos.login import datos_login
from modulos.miembros import datos_miembros

# ======================= DATOS DE PRUEBA (borrar al conectar la base) =======================
_LIDERES = []     # cada uno: {"id_lider", "id_miembro", "id_ministerio"}


def _cargar_pruebas():
    # Un líder en Jóvenes (1) y otro en Damas (2); Caballeros (3) queda sin líder
    for id_ministerio, correo in ((1, "lider@iglesia.org"), (2, "damas@iglesia.org")):
        candidato = datos_miembros.listar_miembros(1, id_ministerio, "", 1, 1)[0]
        _LIDERES.append({"id_lider": len(_LIDERES) + 1,
                         "id_miembro": candidato["id_miembro"],
                         "id_ministerio": id_ministerio,
                         "correo": correo})


_cargar_pruebas()


# ======================= FUNCIONES DEL ÁREA =======================
def listar_ministerios():
    """Devuelve la lista de (id_ministerio, nombre).

    TODO: SELECT id_ministerio, nombre FROM ministerios ORDER BY nombre;
    """
    return datos_miembros.listar_ministerios()


def listar_lideres():
    """Devuelve todos los líderes con sus datos (lista de diccionarios).

    Cada diccionario: id_lider, id_miembro, id_ministerio, nombres, apellidos,
    correo (su acceso), telefono y activo (1 o 0, si el miembro sigue activo).

    TODO: SELECT l.id_lider, l.id_miembro, l.id_ministerio, u.correo,
                 m.nombres, m.apellidos, m.telefono, m.activo
          FROM lideres l
          JOIN miembros m ON m.id_miembro = l.id_miembro
          JOIN usuarios u ON u.id_usuario = l.id_usuario
          ORDER BY m.apellidos, m.nombres;
    """
    resultado = []
    for l in _LIDERES:
        m = datos_miembros.obtener_miembro(l["id_miembro"])
        resultado.append({**l, "nombres": m["nombres"], "apellidos": m["apellidos"],
                          "telefono": m["telefono"], "activo": m["activo"]})
    resultado.sort(key=lambda x: (x["apellidos"], x["nombres"]))
    return resultado


def listar_candidatos():
    """Miembros ACTIVOS que todavía no son líderes:
    lista de (id_miembro, nombres, apellidos, fecha_nacimiento, sexo).
    (El controlador filtra después a quienes cumplen la edad del ministerio.)

    TODO: SELECT id_miembro, nombres, apellidos, fecha_nacimiento, sexo
          FROM miembros
          WHERE activo = 1
            AND id_miembro NOT IN (SELECT id_miembro FROM lideres)
          ORDER BY apellidos, nombres;
    """
    ya_lideres = {l["id_miembro"] for l in _LIDERES}
    resultado = []
    for m in datos_miembros.listar_miembros(1, None, "", 1, 100000):
        if m["id_miembro"] in ya_lideres:
            continue
        completo = datos_miembros.obtener_miembro(m["id_miembro"])
        resultado.append((m["id_miembro"], completo["nombres"], completo["apellidos"],
                          completo["fecha_nacimiento"], completo["sexo"]))
    return resultado


def obtener_miembro(id_miembro):
    """Datos de un miembro para validar la regla de edad: nombres, apellidos, fecha_nacimiento, sexo.

    TODO: SELECT nombres, apellidos, fecha_nacimiento, sexo FROM miembros WHERE id_miembro = %s;
    """
    m = datos_miembros.obtener_miembro(id_miembro)
    if m is None:
        return None
    return {k: m[k] for k in ("nombres", "apellidos", "fecha_nacimiento", "sexo")}


def ministerio_de_lider(id_miembro):
    """Devuelve el id del ministerio que lidera ese miembro, o None si no es líder.

    TODO: SELECT id_ministerio FROM lideres WHERE id_miembro = %s;
    """
    for l in _LIDERES:
        if l["id_miembro"] == id_miembro:
            return l["id_ministerio"]
    return None


def existe_correo(correo):
    """True si ese correo ya tiene acceso al sistema."""
    return datos_login.existe_correo(correo)


def crear_lider(id_miembro, id_ministerio, correo, clave):
    """Nombra a un miembro como líder de un ministerio y le crea su acceso. Devuelve el id nuevo.
    Debe fallar con ValueError si ese miembro ya es líder (de cualquier ministerio) o el correo ya existe.

    TODO (en UNA transacción):
        INSERT INTO usuarios (nombre, correo, clave, id_rol, activo)
        VALUES (%s, %s, <clave cifrada>, (SELECT id_rol FROM roles WHERE nombre_rol = 'Líder'), 1);
        -- id_usuario = cursor.lastrowid
        INSERT INTO lideres (id_miembro, id_ministerio, id_usuario) VALUES (%s, %s, %s);
        conexion.commit()
        -- si MySQL responde error 1062 (duplicado), hacer rollback y lanzar ValueError
    """
    if ministerio_de_lider(id_miembro) is not None:
        raise ValueError("Ese miembro ya es líder de un ministerio.")
    if datos_login.existe_correo(correo):
        raise ValueError("Ese correo ya tiene acceso al sistema.")
    datos_login.crear_usuario(correo, clave, "Líder")
    nuevo_id = max((l["id_lider"] for l in _LIDERES), default=0) + 1
    _LIDERES.append({"id_lider": nuevo_id, "id_miembro": id_miembro,
                     "id_ministerio": id_ministerio, "correo": correo.strip().lower()})
    return nuevo_id


def eliminar_lider(id_lider):
    """Quita el cargo de líder y su acceso (la persona sigue siendo miembro).

    TODO (en UNA transacción):
        UPDATE usuarios SET activo = 0 WHERE id_usuario = (SELECT id_usuario FROM lideres WHERE id_lider = %s);
        DELETE FROM lideres WHERE id_lider = %s;
    """
    for l in _LIDERES:
        if l["id_lider"] == id_lider:
            datos_login.eliminar_usuario(l["correo"])
    _LIDERES[:] = [l for l in _LIDERES if l["id_lider"] != id_lider]


def ministerio_por_correo(correo):
    """Ministerio que lidera el usuario con ese correo (para armar su pantalla), o None.

    TODO: SELECT l.id_ministerio FROM lideres l
          JOIN usuarios u ON u.id_usuario = l.id_usuario WHERE u.correo = %s AND u.activo = 1;
    """
    for l in _LIDERES:
        if l["correo"] == correo.strip().lower():
            return l["id_ministerio"]
    return None


def nombre_por_correo(correo):
    """Nombre completo del líder con ese correo, o None.

    TODO: SELECT CONCAT(m.nombres, ' ', m.apellidos) FROM lideres l
          JOIN usuarios u ON u.id_usuario = l.id_usuario
          JOIN miembros m ON m.id_miembro = l.id_miembro WHERE u.correo = %s;
    """
    for l in _LIDERES:
        if l["correo"] == correo.strip().lower():
            m = datos_miembros.obtener_miembro(l["id_miembro"])
            return f'{m["nombres"]} {m["apellidos"]}'
    return None
