"""
pagina_lideres.py
-----------------
Área "Líderes": una tarjeta por ministerio con sus líderes (nombre y teléfono),
botón para agregar un líder y botón para quitarlo.

Solo dibuja y reacciona a los clics; los datos y las reglas están en controlador_lideres.
"""
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QScrollArea, QMessageBox
)

from modulos.comunes.iconos import icono
from modulos.dashboard.estilos_dashboard import VERDE_OSCURO
from modulos.lideres import controlador_lideres as controlador
from modulos.lideres.dialogo_lider import DialogoLider

COLUMNAS = 3
ROJO = "#B3261E"


def _vaciar(layout):
    """Quita todos los elementos de un layout (para volver a llenarlo con datos nuevos)."""
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.setParent(None)
            widget.deleteLater()
        elif item.layout():
            _vaciar(item.layout())


class PaginaLideres(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("pagina")

        contenido = QWidget()
        contenido.setObjectName("contenido_scroll")
        cuerpo = QVBoxLayout(contenido)
        cuerpo.setContentsMargins(0, 0, 12, 0)
        cuerpo.setSpacing(14)
        cuerpo.addLayout(self._crear_tarjetas())
        self.rejilla = QGridLayout()
        self.rejilla.setSpacing(14)
        cuerpo.addLayout(self.rejilla)
        cuerpo.addStretch()

        area = QScrollArea()
        area.setWidgetResizable(True)
        area.setFrameShape(QFrame.NoFrame)
        area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        area.setWidget(contenido)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(14)
        lay.addLayout(self._crear_encabezado())
        lay.addWidget(area, 1)

        self.refrescar()

    # ======================= construcción =======================
    def _crear_encabezado(self):
        titulo = QLabel("Líderes")
        titulo.setObjectName("titulo_pagina")
        subtitulo = QLabel("Cada líder dirige un solo ministerio")
        subtitulo.setObjectName("subtitulo_pagina")
        textos = QVBoxLayout()
        textos.setSpacing(0)
        textos.addWidget(titulo)
        textos.addWidget(subtitulo)

        btn_nuevo = QPushButton("  Nuevo líder")
        btn_nuevo.setObjectName("boton_lleno")
        btn_nuevo.setIcon(icono("mas", "#FFFFFF", tamano=16))
        btn_nuevo.setIconSize(QSize(16, 16))
        btn_nuevo.setCursor(Qt.PointingHandCursor)
        btn_nuevo.clicked.connect(lambda: self._nuevo())

        fila = QHBoxLayout()
        fila.addLayout(textos, 1)
        fila.addWidget(btn_nuevo)
        return fila

    def _crear_tarjetas(self):
        fila = QHBoxLayout()
        fila.setSpacing(14)
        self._numeros = {}
        for clave, titulo, destacada in (
            ("lideres", "Líderes", True),
            ("con_lider", "Ministerios con líder", False),
            ("sin_lider", "Ministerios sin líder", False),
        ):
            tarjeta = QFrame()
            tarjeta.setObjectName("tarjeta_destacada" if destacada else "tarjeta_fija")
            tarjeta.setMinimumHeight(86)
            sufijo = "_blanco" if destacada else ""
            lbl_titulo = QLabel(titulo)
            lbl_titulo.setObjectName("titulo_tarjeta" + sufijo)
            lbl_numero = QLabel("0")
            lbl_numero.setObjectName("numero_tarjeta" + sufijo)
            lay = QVBoxLayout(tarjeta)
            lay.setContentsMargins(18, 12, 18, 12)
            lay.addWidget(lbl_titulo)
            lay.addWidget(lbl_numero)
            self._numeros[clave] = lbl_numero
            fila.addWidget(tarjeta, 1)
        return fila

    # ======================= datos =======================
    def refrescar(self):
        """Vuelve a pedir los datos y redibuja las tarjetas."""
        for clave, cantidad in controlador.cargar_resumen().items():
            self._numeros[clave].setText(str(cantidad))

        _vaciar(self.rejilla)
        for i, ministerio in enumerate(controlador.cargar_ministerios()):
            self.rejilla.addWidget(self._tarjeta_ministerio(ministerio), i // COLUMNAS, i % COLUMNAS)
        for columna in range(COLUMNAS):
            self.rejilla.setColumnStretch(columna, 1)

    def _tarjeta_ministerio(self, ministerio):
        """Tarjeta de un ministerio: su nombre, sus líderes y el botón para agregar otro."""
        tarjeta = QFrame()
        tarjeta.setObjectName("tarjeta_fija")
        tarjeta.setMinimumHeight(200)

        titulo = QLabel(ministerio["nombre"])
        titulo.setObjectName("ministerio_titulo")
        lideres = ministerio["lideres"]
        chip = QLabel(f"{len(lideres)} líder" + ("es" if len(lideres) != 1 else "") if lideres else "Sin líder")
        chip.setObjectName("chip_programada" if lideres else "chip_sin_crear")
        cabecera = QHBoxLayout()
        cabecera.addWidget(titulo)
        cabecera.addStretch()
        cabecera.addWidget(chip, alignment=Qt.AlignVCenter)

        lay = QVBoxLayout(tarjeta)
        lay.setContentsMargins(18, 14, 16, 14)
        lay.setSpacing(10)
        lay.addLayout(cabecera)

        if lideres:
            for lider in lideres:
                lay.addLayout(self._fila_lider(lider, ministerio["nombre"]))
        else:
            vacio = QLabel("Todavía no tiene un líder asignado.")
            vacio.setObjectName("sin_lider")
            vacio.setWordWrap(True)
            lay.addWidget(vacio)

        lay.addStretch()
        agregar = QPushButton("Agregar líder")
        agregar.setObjectName("boton_registrar")
        agregar.setCursor(Qt.PointingHandCursor)
        agregar.clicked.connect(lambda _=False, i=ministerio["id"]: self._nuevo(i))
        fila_agregar = QHBoxLayout()
        fila_agregar.addWidget(agregar)
        fila_agregar.addStretch()
        lay.addLayout(fila_agregar)
        return tarjeta

    def _fila_lider(self, lider, nombre_ministerio):
        avatar = QLabel(lider["iniciales"])
        avatar.setObjectName("avatar_miembro" if lider["activo"] else "avatar_miembro_inactivo")
        avatar.setFixedSize(32, 32)
        avatar.setAlignment(Qt.AlignCenter)

        lbl_nombre = QLabel(lider["nombre"])
        lbl_nombre.setObjectName("lider_nombre")
        detalle = f'{lider["telefono"]}  ·  {lider["correo"]}' + ("" if lider["activo"] else "  ·  miembro inactivo")
        lbl_detalle = QLabel(detalle)
        lbl_detalle.setObjectName("lider_detalle")
        textos = QVBoxLayout()
        textos.setSpacing(0)
        textos.addWidget(lbl_nombre)
        textos.addWidget(lbl_detalle)

        quitar = QPushButton()
        quitar.setObjectName("boton_icono")
        quitar.setFixedSize(30, 30)
        quitar.setIcon(icono("papelera", ROJO, tamano=18))
        quitar.setIconSize(QSize(18, 18))
        quitar.setToolTip("Eliminar líder")
        quitar.setCursor(Qt.PointingHandCursor)
        quitar.clicked.connect(lambda _=False, l=lider, m=nombre_ministerio: self._eliminar(l, m))

        fila = QHBoxLayout()
        fila.setSpacing(10)
        fila.addWidget(avatar)
        fila.addLayout(textos, 1)
        fila.addWidget(quitar)
        return fila

    # ======================= eventos =======================
    def _nuevo(self, id_ministerio=None):
        if DialogoLider(self, id_ministerio).exec():
            self.refrescar()

    def _eliminar(self, lider, nombre_ministerio):
        caja = QMessageBox(self)
        caja.setIcon(QMessageBox.Question)
        caja.setWindowTitle("Eliminar líder")
        caja.setText(f'¿Eliminar a {lider["nombre"]} como líder de «{nombre_ministerio}»?')
        caja.setInformativeText("Seguirá siendo miembro de la iglesia, pero se le quita el cargo y su acceso al sistema.")
        boton_si = caja.addButton("Eliminar líder", QMessageBox.AcceptRole)
        caja.addButton("Volver", QMessageBox.RejectRole)
        caja.exec()
        if caja.clickedButton() is boton_si:
            controlador.eliminar(lider["id_lider"])
            self.refrescar()
