"""
dialogo_actividad.py
--------------------
Ventana (formulario emergente) para crear o editar una actividad.
Tipo: Culto o Evento externo. Valida con controlador_actividades.validar antes de guardar.
"""
from datetime import date

from PySide6.QtCore import Qt, QDate, QTime
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit,
    QDateEdit, QTimeEdit, QComboBox, QPushButton
)

from modulos.actividades import controlador_actividades as controlador
from modulos.comunes.estilos import estilo_aplicacion


def _a_qdate(fecha):
    return QDate(fecha.year, fecha.month, fecha.day)


class DialogoActividad(QDialog):
    def __init__(self, parent=None, id_evento=None, fecha=None, tipo="Culto", vista=None):
        """
        id_evento: si viene, se está EDITANDO esa actividad
        fecha, tipo: valores iniciales al crear (por ejemplo, desde la tarjeta de un culto de la semana)
        vista: None = el pastor (actividades generales); un número = líder de ese ministerio
        """
        super().__init__(parent)
        self._id = id_evento
        self._vista = vista
        self._ultimo_sugerido = None
        self.setStyleSheet(estilo_aplicacion())
        self.setWindowTitle("Editar actividad" if id_evento else "Nueva actividad")
        self.setModal(True)
        self.setMinimumWidth(560)

        titulo = QLabel("Editar actividad" if id_evento else "Nueva actividad")
        titulo.setObjectName("titulo_dialogo")

        # ----- campos -----
        self.cmb_tipo = QComboBox()
        for valor, texto in controlador.tipos_permitidos(vista):     # Caballeros no tiene culto propio
            self.cmb_tipo.addItem(texto, valor)
        self.txt_nombre = QLineEdit()
        self.fecha = QDateEdit()
        self.fecha.setCalendarPopup(True)
        self.fecha.setDisplayFormat("dd/MM/yyyy")
        self.fecha.setMinimumDate(QDate(2000, 1, 1))
        self.fecha.setMaximumDate(QDate.currentDate().addYears(5))
        self.hora = QTimeEdit()
        self.hora.setDisplayFormat("hh:mm AP")
        self.txt_lugar = QLineEdit()
        self.txt_descripcion = QLineEdit()
        self.txt_descripcion.setPlaceholderText("Opcional")

        rejilla = QGridLayout()
        rejilla.setHorizontalSpacing(16)
        rejilla.setVerticalSpacing(4)
        self._poner(rejilla, 0, 0, "Tipo", self.cmb_tipo)
        self._poner(rejilla, 0, 1, "Nombre", self.txt_nombre)
        self._poner(rejilla, 2, 0, "Fecha", self.fecha)
        self._poner(rejilla, 2, 1, "Hora", self.hora)
        self._poner(rejilla, 4, 0, "Lugar", self.txt_lugar)
        self._poner(rejilla, 4, 1, "Descripción", self.txt_descripcion)

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
        lay.addWidget(self.lbl_error)
        lay.addLayout(botones)

        self._cargar_datos(fecha, tipo)

        # Se conectan al final, para que cargar los datos no dispare el nombre automático
        self.cmb_tipo.currentIndexChanged.connect(self._sugerir_nombre)
        self.fecha.dateChanged.connect(self._sugerir_nombre)

    # ---------- construcción ----------
    def _poner(self, rejilla, fila, columna, etiqueta, campo):
        lbl = QLabel(etiqueta)
        lbl.setObjectName("etiqueta_form")
        rejilla.addWidget(lbl, fila, columna)
        rejilla.addWidget(campo, fila + 1, columna)

    def _cargar_datos(self, fecha, tipo):
        if self._id is not None:                         # editar: se llena con lo guardado
            a = controlador.cargar_actividad(self._id)
            self.cmb_tipo.setCurrentIndex(max(0, self.cmb_tipo.findData(a["tipo"])))
            self.txt_nombre.setText(a["nombre"])
            self.fecha.setDate(_a_qdate(a["fecha"]))
            self.hora.setTime(QTime(a["hora"].hour, a["hora"].minute))
            self.txt_lugar.setText(a["lugar"])
            self.txt_descripcion.setText(a["descripcion"])
            sugerido = self._nombre_sugerido()
            self._ultimo_sugerido = sugerido if a["nombre"] == sugerido else None
        else:                                            # nuevo
            self.cmb_tipo.setCurrentIndex(max(0, self.cmb_tipo.findData(tipo)))
            self.fecha.setDate(_a_qdate(fecha or date.today()))
            self.hora.setTime(QTime(19, 0))
            self._sugerir_nombre()

    # ---------- nombre automático ("Culto Miércoles") ----------
    def _nombre_sugerido(self):
        if self.cmb_tipo.currentData() != "Culto":
            return ""
        return f"Culto {controlador.DIAS[self.fecha.date().toPython().weekday()]}"

    def _sugerir_nombre(self):
        """Cambia el nombre solo si está vacío o si todavía es el que se había sugerido."""
        nuevo = self._nombre_sugerido()
        actual = self.txt_nombre.text().strip()
        if actual == "" or actual == self._ultimo_sugerido:
            self.txt_nombre.setText(nuevo)
        self._ultimo_sugerido = nuevo

    # ---------- guardar ----------
    def _guardar(self):
        hora = self.hora.time()
        datos = {
            "tipo": self.cmb_tipo.currentData(),
            "nombre": self.txt_nombre.text(),
            "fecha": self.fecha.date().toPython(),
            "hora": hora.toPython(),
            "lugar": self.txt_lugar.text(),
            "descripcion": self.txt_descripcion.text(),
        }
        errores = controlador.validar(datos, self._id, self._vista)
        if errores:
            self.lbl_error.setText("\n".join(errores))
            return
        controlador.guardar(datos, self._id, self._vista)
        self.accept()
