"""
configuracion.py
----------------
Guarda ajustes pequeños que conviene recordar entre sesiones, por ejemplo el nombre de la iglesia
que se escribe en los informes. Se guardan en un archivo de la carpeta del usuario
(~/.ekklesia/configuracion.json), no en la base de datos.
"""
import json
from pathlib import Path

RUTA = Path.home() / ".ekklesia" / "configuracion.json"


def _leer():
    try:
        return json.loads(RUTA.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def obtener(clave, por_defecto=""):
    return _leer().get(clave, por_defecto)


def guardar(clave, valor):
    datos = _leer()
    datos[clave] = valor
    try:
        RUTA.parent.mkdir(parents=True, exist_ok=True)
        RUTA.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        pass          # si no se puede guardar, simplemente no se recuerda
