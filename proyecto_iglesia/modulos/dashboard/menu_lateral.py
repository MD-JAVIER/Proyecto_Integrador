"""
menu_lateral.py
---------------
Menú de la izquierda. Avisa a la ventana, mediante señales, cuando el usuario
elige un área o cierra sesión. No sabe nada de las páginas: solo emite "quiero ir a X".
"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QButtonGroup
)

from modulos.comunes.logo import cargar_logo
from modulos.dashboard.estilos_dashboard import VERDE

# (clave interna, texto del botón)
OPCIONES = [
    ("panel", "Panel"),
    ("miembros", "Miembros"),
    ("finanzas", "Finanzas"),
    ("actividades", "Actividades"),
    ("lideres", "Líderes"),
]


class MenuLateral(QFrame):
    pagina_seleccionada = Signal(str)   # emite la clave: "panel", "miembros", ...
    cerrar_sesion = Signal()

    def __init__(self, opciones=None):
        """opciones: lista de (clave, texto). Por defecto, el menú completo del pastor."""
        super().__init__()
        self.setObjectName("menu_lateral")
        self.setFixedWidth(230)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 16, 16, 20)
        lay.setSpacing(4)

        # Logo + nombre
        cabecera = QHBoxLayout()
        logo = QLabel()
        logo.setPixmap(cargar_logo(VERDE, 44))
        nombre = QLabel("Ekklesia")
        nombre.setObjectName("nombre_app")
        cabecera.addWidget(logo)
        cabecera.addSpacing(8)
        cabecera.addWidget(nombre)
        cabecera.addStretch()
        lay.addLayout(cabecera)

        etiqueta = QLabel("Menu")
        etiqueta.setObjectName("etiqueta_menu")
        lay.addSpacing(10)
        lay.addWidget(etiqueta)
        lay.addSpacing(6)

        # Botones de áreas: solo uno puede estar marcado a la vez
        self._grupo = QButtonGroup(self)
        self._grupo.setExclusive(True)
        self._botones = {}
        for clave, texto in (opciones or OPCIONES):
            boton = QPushButton(texto)
            boton.setObjectName("boton_menu")
            boton.setCheckable(True)
            boton.setCursor(Qt.PointingHandCursor)
            boton.clicked.connect(lambda _=False, c=clave: self.pagina_seleccionada.emit(c))
            self._grupo.addButton(boton)
            self._botones[clave] = boton
            lay.addWidget(boton)

        lay.addStretch()

        # Cerrar sesión (no se marca, solo avisa)
        cerrar = QPushButton("Cerrar")
        cerrar.setObjectName("boton_menu")
        cerrar.setCursor(Qt.PointingHandCursor)
        cerrar.clicked.connect(self.cerrar_sesion.emit)
        lay.addWidget(cerrar)

    def marcar(self, clave):
        """Resalta el botón de un área (se usa cuando se navega desde una tarjeta)."""
        if clave in self._botones:
            self._botones[clave].setChecked(True)
