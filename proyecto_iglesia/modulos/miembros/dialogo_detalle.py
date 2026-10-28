"""
dialogo_detalle.py
------------------
Ventana con los datos completos de un miembro.
Desde aquí se puede ir a editar, desactivar o reactivar.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton
)

from modulos.comunes.estilos import estilo_aplicacion
from modulos.miembros import controlador_miembros as controlador


class DialogoDetalle(QDialog):
    def __init__(self, parent, id_miembro, solo_lectura=False):
        super().__init__(parent)
        self.accion = None              # "editar" si el usuario pidió editar
        self._id = id_miembro
        self.setStyleSheet(estilo_aplicacion())
        self.setWindowTitle("Detalle del miembro")
        self.setModal(True)
        self.setMinimumWidth(480)

        d = controlador.cargar_detalle(id_miembro)
        self._detalle = d

        # ----- cabecera: avatar, nombre y estado -----
        avatar = QLabel(d["iniciales"])
        avatar.setObjectName("avatar_grande" if d["activo"] else "avatar_grande_inactivo")
        avatar.setFixedSize(64, 64)
        avatar.setAlignment(Qt.AlignCenter)

        nombre = QLabel(d["nombre"])
        nombre.setObjectName("titulo_dialogo")
        chip = QLabel("Activo" if d["activo"] else "Inactivo")
        chip.setObjectName("chip_activo" if d["activo"] else "chip_inactivo")
        fila_chip = QHBoxLayout()
        fila_chip.addWidget(chip)
        fila_chip.addStretch()
        textos = QVBoxLayout()
        textos.setSpacing(4)
        textos.addWidget(nombre)
        textos.addLayout(fila_chip)

        cabecera = QHBoxLayout()
        cabecera.setSpacing(16)
        cabecera.addWidget(avatar)
        cabecera.addLayout(textos, 1)

        # ----- datos -----
        ultima = d["ultima"] + ("  ·  cerca de quedar inactivo" if d["aviso"] else "")
        rejilla = QGridLayout()
        rejilla.setHorizontalSpacing(24)
        rejilla.setVerticalSpacing(2)
        campos = [
            ("Teléfono", d["telefono"]), ("Dirección", d["direccion"]),
            ("Fecha de nacimiento", d["nacimiento"]), ("Sexo", d["sexo"]),
            ("Ministerio", d["ministerios"]), ("Fecha de ingreso", d["ingreso"]),
            ("Última asistencia", ultima),
        ]
        for i, (etiqueta, valor) in enumerate(campos):
            fila, columna = (i // 2) * 2, i % 2
            lbl_e = QLabel(etiqueta)
            lbl_e.setObjectName("dato_etiqueta")
            lbl_v = QLabel(valor)
            lbl_v.setObjectName("aviso_asistencia" if (etiqueta == "Última asistencia" and d["aviso"]) else "dato_valor")
            lbl_v.setWordWrap(True)
            rejilla.addWidget(lbl_e, fila, columna)
            rejilla.addWidget(lbl_v, fila + 1, columna)
            rejilla.setRowMinimumHeight(fila + 1, 34)

        # ----- botones -----
        btn_editar = QPushButton("Editar")
        btn_editar.setObjectName("boton_lleno")
        btn_editar.clicked.connect(self._editar)
        btn_estado = QPushButton("Desactivar" if d["activo"] else "Reactivar")
        btn_estado.setObjectName("boton_borde")
        btn_estado.clicked.connect(self._cambiar_estado)
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setObjectName("boton_texto")
        btn_cerrar.clicked.connect(self.accept)
        for boton in (btn_editar, btn_estado, btn_cerrar):
            boton.setCursor(Qt.PointingHandCursor)
        botones = QHBoxLayout()
        botones.addStretch()
        botones.addWidget(btn_cerrar)
        if not solo_lectura:                       # el líder solo consulta
            botones.addWidget(btn_estado)
            botones.addWidget(btn_editar)
        else:
            btn_estado.hide()
            btn_editar.hide()

        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 24, 28, 22)
        lay.setSpacing(14)
        lay.addLayout(cabecera)
        lay.addSpacing(6)
        lay.addLayout(rejilla)
        lay.addSpacing(8)
        lay.addLayout(botones)

    def _editar(self):
        self.accion = "editar"
        self.accept()

    def _cambiar_estado(self):
        """Desactiva o reactiva directamente (se puede deshacer con el mismo botón)."""
        controlador.cambiar_estado(self._id, not self._detalle["activo"])
        self.accept()
