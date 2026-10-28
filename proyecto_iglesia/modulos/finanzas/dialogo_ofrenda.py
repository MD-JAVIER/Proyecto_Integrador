"""
dialogo_ofrenda.py
------------------
Ventana para registrar la ofrenda de un mes o corregir su monto.
Tiene solo tres datos, igual que la tabla `ofrendas`: mes, año y monto.
(Quién la registró se toma del usuario que inició sesión.)
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit,
    QComboBox, QDoubleSpinBox, QPushButton, QAbstractSpinBox
)

from modulos.comunes.estilos import estilo_aplicacion
from modulos.finanzas import controlador_finanzas as controlador


class DialogoOfrenda(QDialog):
    def __init__(self, parent, anio, correo, mes=None, id_ofrenda=None, monto=None):
        """
        anio:        año de la ofrenda
        mes:         mes que se quiere preseleccionar (o el que se está editando)
        id_ofrenda:  si viene, se está EDITANDO y el mes no se puede cambiar
        """
        super().__init__(parent)
        self._anio = anio
        self._correo = correo
        self._id = id_ofrenda
        self.setStyleSheet(estilo_aplicacion())
        self.setWindowTitle("Editar ofrenda" if id_ofrenda else "Registrar ofrenda")
        self.setModal(True)
        self.setMinimumWidth(440)

        titulo = QLabel("Editar ofrenda" if id_ofrenda else "Registrar ofrenda")
        titulo.setObjectName("titulo_dialogo")

        # ----- mes -----
        self.cmb_mes = QComboBox()
        if id_ofrenda is None:
            for numero, nombre in controlador.meses_disponibles(anio):
                self.cmb_mes.addItem(nombre, numero)
            if mes is not None:
                self.cmb_mes.setCurrentIndex(max(0, self.cmb_mes.findData(mes)))
            else:                                   # sin mes indicado: se propone el más reciente
                self.cmb_mes.setCurrentIndex(self.cmb_mes.count() - 1)
        else:
            self.cmb_mes.addItem(controlador.MESES[mes - 1], mes)
            self.cmb_mes.setEnabled(False)          # al editar no se cambia el mes

        # ----- año (solo lectura) -----
        self.txt_anio = QLineEdit(str(anio))
        self.txt_anio.setReadOnly(True)

        # ----- monto -----
        self.spn_monto = QDoubleSpinBox()
        self.spn_monto.setRange(0, 9_999_999.99)
        self.spn_monto.setDecimals(2)
        self.spn_monto.setGroupSeparatorShown(True)
        self.spn_monto.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.spn_monto.setValue(monto or 0)
        self.spn_monto.selectAll()

        rejilla = QGridLayout()
        rejilla.setHorizontalSpacing(16)
        rejilla.setVerticalSpacing(4)
        self._poner(rejilla, 0, 0, "Mes", self.cmb_mes)
        self._poner(rejilla, 0, 1, "Año", self.txt_anio)
        self._poner(rejilla, 2, 0, "Monto de la ofrenda", self.spn_monto)

        self.lbl_error = QLabel("")
        self.lbl_error.setObjectName("error_form")
        self.lbl_error.setWordWrap(True)
        self.lbl_error.setMinimumHeight(40)
        self.lbl_error.setAlignment(Qt.AlignTop)

        btn_guardar = QPushButton("Guardar")
        btn_guardar.setObjectName("boton_lleno")
        btn_guardar.setCursor(Qt.PointingHandCursor)
        btn_guardar.clicked.connect(self._guardar)
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("boton_texto")
        btn_cancelar.setCursor(Qt.PointingHandCursor)
        btn_cancelar.clicked.connect(self.reject)
        botones = QHBoxLayout()
        botones.addStretch()
        botones.addWidget(btn_cancelar)
        botones.addWidget(btn_guardar)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 24, 28, 22)
        lay.setSpacing(10)
        lay.addWidget(titulo)
        lay.addSpacing(6)
        lay.addLayout(rejilla)
        lay.addWidget(self.lbl_error)
        lay.addLayout(botones)

    def _poner(self, rejilla, fila, columna, etiqueta, campo):
        lbl = QLabel(etiqueta)
        lbl.setObjectName("etiqueta_form")
        rejilla.addWidget(lbl, fila, columna)
        rejilla.addWidget(campo, fila + 1, columna)

    def _guardar(self):
        mes = self.cmb_mes.currentData()
        monto = self.spn_monto.value()

        errores = controlador.validar(mes, self._anio, monto, self._id)
        if errores:
            self.lbl_error.setText("\n".join(errores))
            return
        try:
            controlador.guardar(mes, self._anio, monto, self._correo, self._id)
        except ValueError as error:          # por si la base rechaza un mes duplicado
            self.lbl_error.setText(str(error))
            return
        self.accept()
