"""
iconos.py
---------
Pequeño juego de iconos de línea (estilo outline) dibujados como SVG,
para no depender de archivos externos. Se piden por nombre, color y tamaño.
"""
from PySide6.QtCore import Qt, QByteArray
from PySide6.QtGui import QPixmap, QPainter, QIcon
from PySide6.QtSvg import QSvgRenderer

# Cada icono es el interior de un SVG de 24 x 24
_FORMAS = {
    "panel": '<rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="3" width="7" height="7" rx="2"/>'
             '<rect x="3" y="14" width="7" height="7" rx="2"/><rect x="14" y="14" width="7" height="7" rx="2"/>',
    "usuarios": '<circle cx="9" cy="7" r="4"/><path d="M3 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2"/>'
                '<path d="M16 3.13a4 4 0 0 1 0 7.75"/><path d="M21 21v-2a4 4 0 0 0-3-3.85"/>',
    "billetera": '<path d="M17 8V5a1 1 0 0 0-1-1H6a2 2 0 0 0 0 4h12a1 1 0 0 1 1 1v3m0 4v3a1 1 0 0 1-1 1H6a2 2 0 0 1-2-2V6"/>'
                 '<path d="M20 12v4h-4a2 2 0 0 1 0-4h4"/>',
    "calendario": '<rect x="4" y="5" width="16" height="16" rx="2"/><path d="M16 3v4M8 3v4M4 11h16"/>',
    "corona": '<path d="M12 6l4 6l5-4l-2 10H5L3 8l5 4z"/><circle cx="12" cy="4.5" r="1"/>',
    "salir": '<path d="M14 8V6a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h7a2 2 0 0 0 2-2v-2"/>'
             '<path d="M9 12h12l-3-3M18 15l3-3"/>',
    "buscar": '<circle cx="10" cy="10" r="7"/><path d="M21 21l-6-6"/>',
    "flecha": '<path d="M7 17L17 7M8 7h9v9"/>',
    "mas": '<path d="M12 5v14M5 12h14"/>',
    "ojo": '<path d="M12 5C7 5 3 9 2 12c1 3 5 7 10 7s9-4 10-7c-1-3-5-7-10-7z"/><circle cx="12" cy="12" r="3"/>',
    "lapiz": '<path d="M4 20h4L19 9a2.8 2.8 0 0 0-4-4L4 16z"/><path d="M13.5 6.5l4 4"/>',
    "papelera": '<path d="M4 7h16M10 11v6M14 11v6M5 7l1 12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2l1-12M9 7V4h6v3"/>',
    "cerrar": '<path d="M18 6L6 18M6 6l12 12"/>',
    "reiniciar": '<path d="M20 11A8 8 0 1 0 19 16"/><path d="M20 4v7h-7"/>',
    "encender": '<path d="M12 3v9"/><path d="M6.3 6.3a8 8 0 1 0 11.4 0"/>',
}


def pixmap_icono(nombre, color="#8A918D", tamano=22):
    """Devuelve un QPixmap del icono, nítido en pantallas de alta resolución."""
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
           f'stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
           f'{_FORMAS[nombre]}</svg>')
    render = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    pixmap = QPixmap(tamano * 2, tamano * 2)
    pixmap.fill(Qt.transparent)
    pintor = QPainter(pixmap)
    render.render(pintor)
    pintor.end()
    pixmap.setDevicePixelRatio(2)
    return pixmap


def icono(nombre, color_normal="#8A918D", color_marcado=None, tamano=22):
    """QIcon con un color normal y otro cuando el botón está marcado (checked)."""
    ic = QIcon()
    ic.addPixmap(pixmap_icono(nombre, color_normal, tamano), QIcon.Normal, QIcon.Off)
    ic.addPixmap(pixmap_icono(nombre, color_marcado or color_normal, tamano), QIcon.Normal, QIcon.On)
    return ic
