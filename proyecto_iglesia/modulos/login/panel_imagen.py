"""
panel_imagen.py
---------------
Panel izquierdo del login: foto a pantalla completa del panel con el logo
arriba y el versículo abajo.
"""
from pathlib import Path

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QPixmap, QLinearGradient, QColor
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel

from modulos.comunes.logo import cargar_logo
from modulos.login.estilos_login import ESTILO_PANEL_IMAGEN

# carpeta raíz del proyecto -> recursos/imagenes/login.jpg
RUTA_IMAGEN = Path(__file__).resolve().parents[2] / "recursos" / "imagenes" / "login.jpg"


class PanelImagen(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(ESTILO_PANEL_IMAGEN)
        self._foto = QPixmap(str(RUTA_IMAGEN))

        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 24, 28, 28)

        # Logo (en blanco) junto al nombre
        icono = QLabel()
        icono.setPixmap(cargar_logo("#FFFFFF", 44))
        nombre = QLabel("Ekklesia")
        nombre.setObjectName("logo")
        cabecera = QHBoxLayout()
        cabecera.setSpacing(10)
        cabecera.addWidget(icono)
        cabecera.addWidget(nombre)
        cabecera.addStretch()

        versiculo = QLabel("Todo lo puedo en Cristo\nque me fortalece")
        versiculo.setObjectName("versiculo")

        cita = QLabel("Filipenses 4:13")
        cita.setObjectName("cita")

        lay.addLayout(cabecera)
        lay.addStretch()
        lay.addWidget(versiculo)
        lay.addWidget(cita)

    def paintEvent(self, evento):
        p = QPainter(self)
        p.setRenderHint(QPainter.SmoothPixmapTransform)

        # La foto cubre todo el panel (recortando lo que sobre)
        if not self._foto.isNull():
            escala = max(self.width() / self._foto.width(),
                         self.height() / self._foto.height())
            ancho = self._foto.width() * escala
            alto = self._foto.height() * escala
            x = -(ancho - self.width()) * 0.40   # un poco a la izquierda del centro
            y = -(alto - self.height()) * 0.5
            p.drawPixmap(QRectF(x, y, ancho, alto), self._foto,
                         QRectF(self._foto.rect()))
        else:
            p.fillRect(self.rect(), QColor("#0E623D"))

        # Sombra suave arriba y abajo para que el texto blanco se lea bien
        arriba = QLinearGradient(0, 0, 0, self.height() * 0.25)
        arriba.setColorAt(0, QColor(0, 0, 0, 150))
        arriba.setColorAt(1, QColor(0, 0, 0, 0))
        p.fillRect(self.rect(), arriba)

        abajo = QLinearGradient(0, self.height() * 0.65, 0, self.height())
        abajo.setColorAt(0, QColor(0, 0, 0, 0))
        abajo.setColorAt(1, QColor(0, 0, 0, 190))
        p.fillRect(self.rect(), abajo)
