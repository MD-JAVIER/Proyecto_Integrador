"""
dialogo_miembro.py
------------------
Ventana con el formulario para crear o editar un miembro.

Reglas:
  - Cada miembro pertenece a UN solo ministerio (lista desplegable, no casillas).
  - El ministerio depende de la edad y el sexo (18 a 29 = Jóvenes; 30 o más = Caballeros
    o Damas). El formulario lo sugiere solo y lo valida al guardar.
"""
from datetime import date

from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit,
    QDateEdit, QComboBox, QPushButton
)

from modulos.comunes.estilos import estilo_aplicacion
from modulos.miembros import controlador_miembros as controlador


def _a_qdate(fecha):
    return QDate(fecha.year, fecha.month, fecha.day)


class DialogoMiembro(QDialog):
    def __init__(self, parent=None, id_miembro=None, ministerio_fijo=None):
        super().__init__(parent)
        self._id = id_miembro
        self._ministerio_fijo = ministerio_fijo
        self.setStyleSheet(estilo_aplicacion())
        self.setWindowTitle("Editar miembro" if id_miembro else "Nuevo miembro")
        self.setModal(True)
        self.setMinimumWidth(560)

        titulo = QLabel("Editar miembro" if id_miembro else "Nuevo miembro")
        titulo.setObjectName("titulo_dialogo")

        # ----- campos de texto y fechas -----
        self.txt_nombres = QLineEdit()
        self.txt_apellidos = QLineEdit()
        self.txt_telefono = QLineEdit()
        self.txt_telefono.setPlaceholderText("8800 0000")
        self.txt_direccion = QLineEdit()
        self.fecha_nacimiento = self._crear_fecha(date(2000, 1, 1))
        self.fecha_ingreso = self._crear_fecha(date.today())

        # ----- sexo y ministerio (uno solo) -----
        self.cmb_sexo = QComboBox()
        self.cmb_sexo.addItem("Seleccione", None)
        self.cmb_sexo.addItem("Masculino", "M")
        self.cmb_sexo.addItem("Femenino", "F")
        self.cmb_ministerio = QComboBox()
        self.cmb_ministerio.addItem("Seleccione", None)
        for id_min, nombre in controlador.cargar_ministerios():
            self.cmb_ministerio.addItem(nombre, id_min)

        self.lbl_ayuda = QLabel("")
        self.lbl_ayuda.setObjectName("aviso_form")

        rejilla = QGridLayout()
        rejilla.setHorizontalSpacing(16)
        rejilla.setVerticalSpacing(4)
        self._poner(rejilla, 0, 0, "Nombres", self.txt_nombres)
        self._poner(rejilla, 0, 1, "Apellidos", self.txt_apellidos)
        self._poner(rejilla, 2, 0, "Teléfono", self.txt_telefono)
        self._poner(rejilla, 2, 1, "Dirección", self.txt_direccion)
        self._poner(rejilla, 4, 0, "Fecha de nacimiento", self.fecha_nacimiento)
        self._poner(rejilla, 4, 1, "Fecha de ingreso", self.fecha_ingreso)
        self._poner(rejilla, 6, 0, "Sexo", self.cmb_sexo)
        self._poner(rejilla, 6, 1, "Ministerio", self.cmb_ministerio)

        self.lbl_error = QLabel("")
        self.lbl_error.setObjectName("error_form")
        self.lbl_error.setWordWrap(True)
        self.lbl_error.setMinimumHeight(56)
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
        lay.addWidget(self.lbl_ayuda)
        lay.addWidget(self.lbl_error)
        lay.addLayout(botones)

        self._cargar_datos()
        self._actualizar_ayuda()

        # Se conectan al final para que cargar los datos no cambie el ministerio solo
        self.fecha_nacimiento.dateChanged.connect(self._sugerir_ministerio)
        self.cmb_sexo.currentIndexChanged.connect(self._sugerir_ministerio)

    # ---------- construcción ----------
    def _crear_fecha(self, fecha):
        campo = QDateEdit()
        campo.setCalendarPopup(True)
        campo.setDisplayFormat("dd/MM/yyyy")
        campo.setMinimumDate(QDate(1900, 1, 1))
        campo.setMaximumDate(QDate.currentDate())
        campo.setDate(_a_qdate(fecha))
        return campo

    def _poner(self, rejilla, fila, columna, etiqueta, campo):
        lbl = QLabel(etiqueta)
        lbl.setObjectName("etiqueta_form")
        rejilla.addWidget(lbl, fila, columna)
        rejilla.addWidget(campo, fila + 1, columna)

    def _cargar_datos(self):
        """Si se está editando, llena el formulario; si hay ministerio fijo (Líder), lo deja puesto."""
        if self._id is not None:
            m = controlador.cargar_detalle(self._id)["datos"]
            self.txt_nombres.setText(m["nombres"])
            self.txt_apellidos.setText(m["apellidos"])
            self.txt_telefono.setText(m["telefono"])
            self.txt_direccion.setText(m["direccion"])
            self.fecha_nacimiento.setDate(_a_qdate(m["fecha_nacimiento"]))
            self.fecha_ingreso.setDate(_a_qdate(m["fecha_ingreso"]))
            self.cmb_sexo.setCurrentIndex(max(0, self.cmb_sexo.findData(m.get("sexo"))))
            if m["ids_ministerios"]:
                self.cmb_ministerio.setCurrentIndex(self.cmb_ministerio.findData(m["ids_ministerios"][0]))
        if self._ministerio_fijo is not None:           # un Líder solo maneja su ministerio
            self.cmb_ministerio.setCurrentIndex(self.cmb_ministerio.findData(self._ministerio_fijo))
            self.cmb_ministerio.setEnabled(False)

    # ---------- sugerencia automática del ministerio ----------
    def _sugerir_ministerio(self):
        """Al cambiar la fecha de nacimiento o el sexo, propone el ministerio que corresponde."""
        if self._ministerio_fijo is None:
            sugerido = controlador.id_ministerio_sugerido(
                self.fecha_nacimiento.date().toPython(), self.cmb_sexo.currentData())
            # Sin ministerio que corresponda (menor de 18 o sin sexo elegido): se deja en "Seleccione"
            self.cmb_ministerio.setCurrentIndex(self.cmb_ministerio.findData(sugerido) if sugerido else 0)
        self._actualizar_ayuda()

    def _actualizar_ayuda(self):
        self.lbl_ayuda.setText(controlador.texto_ayuda_ministerio(
            self.fecha_nacimiento.date().toPython(), self.cmb_sexo.currentData()))

    # ---------- guardar ----------
    def _guardar(self):
        datos = {
            "nombres": self.txt_nombres.text(),
            "apellidos": self.txt_apellidos.text(),
            "telefono": self.txt_telefono.text(),
            "direccion": self.txt_direccion.text(),
            "sexo": self.cmb_sexo.currentData(),
            "fecha_nacimiento": self.fecha_nacimiento.date().toPython(),
            "fecha_ingreso": self.fecha_ingreso.date().toPython(),
        }
        id_min = self.cmb_ministerio.currentData()
        ids = [id_min] if id_min is not None else []

        errores = controlador.validar(datos, ids)
        if errores:
            self.lbl_error.setText("\n".join(errores))
            return
        controlador.guardar(datos, ids, self._id)
        self.accept()
