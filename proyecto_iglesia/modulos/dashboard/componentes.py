"""
componentes.py
--------------
Piezas visuales reutilizables del dashboard:
  - TarjetaClicable: un recuadro que avisa cuando le hacen clic (acceso directo).
  - GraficoPildoras: gráfico de barras con forma de píldora, dibujado a mano.
"""
from PySide6.QtCore import Qt, Signal, QRectF
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtWidgets import QFrame, QWidget, QToolTip


class TarjetaClicable(QFrame):
    """Recuadro que emite la señal `clicked` cuando se hace clic dentro de él."""
    clicked = Signal()

    def __init__(self):
        super().__init__()
        self.setCursor(Qt.PointingHandCursor)

    def mouseReleaseEvent(self, evento):
        dentro = self.rect().contains(evento.position().toPoint())
        if evento.button() == Qt.LeftButton and dentro:
            self.clicked.emit()
        super().mouseReleaseEvent(evento)


class GraficoPildoras(QWidget):
    """Barras redondeadas (píldoras).

    `datos` es una lista de tuplas: (etiqueta, valor, color, texto_tooltip)
    La barra más alta ocupa todo el alto; las demás son proporcionales.
    """

    def __init__(self, ancho_barra=34):
        super().__init__()
        self._datos = []
        self._ancho_barra = ancho_barra
        self._columnas = []          # rectángulos de cada columna, para el tooltip
        self.setMinimumHeight(100)
        self.setMouseTracking(True)

    def establecer_datos(self, datos):
        self._datos = list(datos)
        self.update()                # pide redibujar el gráfico

    # ---------- dibujo ----------
    def paintEvent(self, evento):
        if not self._datos:
            return

        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)

        ancho_total, alto_total = self.width(), self.height()
        alto_etiqueta = 18
        alto_barras = alto_total - alto_etiqueta - 4
        maximo = max(valor for _, valor, _, _ in self._datos) or 1
        ancho_columna = ancho_total / len(self._datos)
        ancho_barra = min(self._ancho_barra, ancho_columna * 0.7)

        fuente = QFont()
        fuente.setPointSize(8)
        pintor.setFont(fuente)

        self._columnas = []
        for i, (etiqueta, valor, color, _) in enumerate(self._datos):
            # Altura proporcional. Una barra con valor siempre mide al menos 1,5 veces su
            # ancho (para que se vea como píldora); si el valor es 0 se dibuja solo un punto.
            if valor <= 0:
                alto = ancho_barra
            else:
                alto = max(ancho_barra * 1.5, alto_barras * valor / maximo)
            x = i * ancho_columna + (ancho_columna - ancho_barra) / 2
            y = alto_barras - alto

            pintor.setPen(Qt.NoPen)
            pintor.setBrush(QColor(color))
            pintor.drawRoundedRect(QRectF(x, y, ancho_barra, alto),
                                   ancho_barra / 2, ancho_barra / 2)

            pintor.setPen(QColor("#000000"))
            pintor.drawText(QRectF(i * ancho_columna, alto_barras + 2, ancho_columna, alto_etiqueta),
                            Qt.AlignCenter, etiqueta)

            self._columnas.append(QRectF(i * ancho_columna, 0, ancho_columna, alto_total))

    # ---------- tooltip al pasar el mouse ----------
    def mouseMoveEvent(self, evento):
        punto = evento.position()
        for i, columna in enumerate(self._columnas):
            if columna.contains(punto):
                QToolTip.showText(evento.globalPosition().toPoint(), self._datos[i][3], self)
                break
        super().mouseMoveEvent(evento)
