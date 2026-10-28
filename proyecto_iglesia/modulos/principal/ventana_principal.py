"""
ventana_principal.py
--------------------
Ventana temporal que aparece después del login, solo para comprobar
que el ingreso y el rol funcionan. Se reemplaza luego por el sistema real.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class VentanaPrincipal(QWidget):
    def __init__(self, usuario, rol):
        super().__init__()
        self.setWindowTitle("Ekklesia")
        self.setMinimumSize(460, 300)

        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignCenter)

        lbl = QLabel(f"Sesión iniciada\n\nCorreo: {usuario}\nRol: {rol}")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("font-size: 16px; color: black;")
        lay.addWidget(lbl)
