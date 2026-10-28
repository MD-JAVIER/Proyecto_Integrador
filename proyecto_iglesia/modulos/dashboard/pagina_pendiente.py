"""
pagina_pendiente.py
-------------------
Página provisional para las áreas que todavía no se construyen
(Miembros, Finanzas, Actividades, Líderes). Permite probar la navegación.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class PaginaPendiente(QWidget):
    def __init__(self, titulo):
        super().__init__()
        self.setObjectName("pagina")

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setObjectName("titulo_pagina")
        lbl_texto = QLabel("Esta área se construirá en el siguiente paso.")
        lbl_texto.setObjectName("texto_pagina")

        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignCenter)
        lay.addWidget(lbl_titulo, alignment=Qt.AlignCenter)
        lay.addWidget(lbl_texto, alignment=Qt.AlignCenter)
