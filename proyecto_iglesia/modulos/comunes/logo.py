"""
logo.py
-------
Carga el logo de Ekklesia (recursos/imagenes/logo.svg) en el color y tamaño
que se pida. Se usa en el login (blanco) y en el menú lateral (verde).
"""
from pathlib import Path

from PySide6.QtCore import Qt, QByteArray
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer

RUTA_LOGO = Path(__file__).resolve().parents[2] / "recursos" / "imagenes" / "logo.svg"
COLOR_ORIGINAL = "#1E7A50"   # color con el que está dibujado el archivo .svg


def cargar_logo(color=COLOR_ORIGINAL, alto=40):
    """Devuelve un QPixmap del logo con el color y la altura indicados."""
    svg = RUTA_LOGO.read_text(encoding="utf-8").replace(COLOR_ORIGINAL, color)
    render = QSvgRenderer(QByteArray(svg.encode("utf-8")))

    tam = render.defaultSize()
    ancho = int(alto * tam.width() / tam.height())

    # Se dibuja al doble de tamaño para que se vea nítido en pantallas de alta resolución
    pixmap = QPixmap(ancho * 2, alto * 2)
    pixmap.fill(Qt.transparent)
    pintor = QPainter(pixmap)
    render.render(pintor)
    pintor.end()
    pixmap.setDevicePixelRatio(2)
    return pixmap
