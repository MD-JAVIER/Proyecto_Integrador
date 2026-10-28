"""
barra_superior.py
-----------------
Barra de arriba: muestra quién inició sesión (foto, nombre y correo).
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel


class BarraSuperior(QFrame):
    def __init__(self, nombre, correo):
        super().__init__()
        self.setObjectName("barra_superior")
        self.setFixedHeight(58)

        # Círculo oscuro: aquí irá la foto del usuario más adelante
        avatar = QLabel()
        avatar.setObjectName("avatar")
        avatar.setFixedSize(34, 34)

        lbl_nombre = QLabel(nombre)
        lbl_nombre.setObjectName("usuario_nombre")
        lbl_correo = QLabel(correo)
        lbl_correo.setObjectName("usuario_correo")

        textos = QVBoxLayout()
        textos.setSpacing(0)
        textos.setAlignment(Qt.AlignVCenter)
        textos.addWidget(lbl_nombre)
        textos.addWidget(lbl_correo)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(24, 0, 24, 0)
        lay.addStretch()
        lay.addWidget(avatar, alignment=Qt.AlignVCenter)
        lay.addSpacing(8)
        lay.addLayout(textos)
