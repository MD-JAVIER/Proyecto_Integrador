"""
dialogo_lider.py
----------------
Ventana (formulario emergente) para nombrar a un miembro como líder de un ministerio.

Regla: un miembro solo puede ser líder de UN ministerio. Por eso la lista de miembros
solo muestra a quienes todavía no son líderes, y además se valida al guardar.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QCompleter, QLineEdit
)

from modulos.comunes.estilos import estilo_aplicacion
from modulos.lideres import controlador_lideres as controlador


class DialogoLider(QDialog):
    def __init__(self, parent=None, id_ministerio=None):
        """id_ministerio: si viene (desde el botón 'Agregar líder' de una tarjeta), queda preseleccionado."""
        super().__init__(parent)
        self.setStyleSheet(estilo_aplicacion())
        self.setWindowTitle("Nuevo líder")
        self.setModal(True)
        self.setMinimumWidth(600)

        titulo = QLabel("Nuevo líder")
        titulo.setObjectName("titulo_dialogo")

        # ----- ministerio -----
        etiqueta_min = QLabel("Ministerio que va a liderar")
        etiqueta_min.setObjectName("etiqueta_form")
        self.cmb_ministerio = QComboBox()
        for id_min, nombre in controlador.cargar_ministerios_lista():
            self.cmb_ministerio.addItem(nombre, id_min)
        if id_ministerio is not None:
            self.cmb_ministerio.setCurrentIndex(max(0, self.cmb_ministerio.findData(id_ministerio)))

        # ----- miembro (lista donde también se puede escribir para buscar) -----
        etiqueta_mi = QLabel("Miembro")
        etiqueta_mi.setObjectName("etiqueta_form")
        self.cmb_miembro = QComboBox()
        self.cmb_miembro.setEditable(True)
        self.cmb_miembro.setInsertPolicy(QComboBox.NoInsert)
        self.cmb_miembro.lineEdit().setPlaceholderText("Escriba para buscar un miembro")
        completador = self.cmb_miembro.completer()
        completador.setFilterMode(Qt.MatchContains)           # busca en cualquier parte del nombre
        completador.setCaseSensitivity(Qt.CaseInsensitive)
        completador.setCompletionMode(QCompleter.PopupCompletion)

        self.lbl_regla = QLabel("")
        self.lbl_regla.setObjectName("aviso_form")
        self.lbl_regla.setWordWrap(True)
        # ----- acceso del líder -----
        etiqueta_correo = QLabel("Correo de acceso")
        etiqueta_correo.setObjectName("etiqueta_form")
        self.txt_correo = QLineEdit()
        self.txt_correo.setPlaceholderText("lider@iglesia.org")
        etiqueta_clave = QLabel("Contraseña temporal")
        etiqueta_clave.setObjectName("etiqueta_form")
        self.txt_clave = QLineEdit()
        self.txt_clave.setPlaceholderText("Mínimo 6 caracteres; el líder la recibe de usted")
        columna_correo = QVBoxLayout()
        columna_correo.setSpacing(4)
        columna_correo.addWidget(etiqueta_correo)
        columna_correo.addWidget(self.txt_correo)
        columna_clave = QVBoxLayout()
        columna_clave.setSpacing(4)
        columna_clave.addWidget(etiqueta_clave)
        columna_clave.addWidget(self.txt_clave)
        fila_acceso = QHBoxLayout()
        fila_acceso.setSpacing(16)
        fila_acceso.addLayout(columna_correo, 1)
        fila_acceso.addLayout(columna_clave, 1)

        aviso = QLabel("Un miembro solo puede ser líder de un ministerio. "
                       "Solo aparecen miembros activos que cumplen la edad del ministerio y aún no son líderes.")
        aviso.setObjectName("aviso_form")
        aviso.setWordWrap(True)

        self.lbl_error = QLabel("")
        self.lbl_error.setObjectName("error_form")
        self.lbl_error.setWordWrap(True)
        self.lbl_error.setMinimumHeight(70)
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
        lay.setSpacing(6)
        lay.addWidget(titulo)
        lay.addSpacing(8)
        lay.addWidget(etiqueta_min)
        lay.addWidget(self.cmb_ministerio)
        lay.addSpacing(6)
        lay.addWidget(etiqueta_mi)
        lay.addWidget(self.cmb_miembro)
        lay.addSpacing(4)
        lay.addWidget(self.lbl_regla)
        lay.addWidget(aviso)
        lay.addSpacing(6)
        lay.addLayout(fila_acceso)
        lay.addWidget(self.lbl_error)
        lay.addLayout(botones)

        self._cargar_miembros()
        self.cmb_ministerio.currentIndexChanged.connect(self._cargar_miembros)

    def _cargar_miembros(self):
        """Llena la lista solo con los miembros que cumplen la edad del ministerio elegido."""
        id_ministerio = self.cmb_ministerio.currentData()
        self.cmb_miembro.clear()
        for id_miembro, nombre in controlador.cargar_candidatos(id_ministerio):
            self.cmb_miembro.addItem(nombre, id_miembro)
        self.cmb_miembro.setCurrentIndex(-1)
        self.lbl_regla.setText(controlador.texto_regla_ministerio(id_ministerio))
        self.lbl_error.setText("")

    def _miembro_elegido(self):
        """Devuelve el id del miembro escrito/seleccionado, o None si el texto no coincide con la lista."""
        texto = self.cmb_miembro.currentText().strip()
        posicion = self.cmb_miembro.findText(texto, Qt.MatchFixedString)   # sin distinguir mayúsculas
        return self.cmb_miembro.itemData(posicion) if posicion >= 0 else None

    def _guardar(self):
        id_miembro = self._miembro_elegido()
        id_ministerio = self.cmb_ministerio.currentData()

        errores = controlador.validar(id_miembro, id_ministerio, self.txt_correo.text(), self.txt_clave.text())
        if errores:
            self.lbl_error.setText("\n".join(errores))
            return
        try:
            controlador.guardar(id_miembro, id_ministerio, self.txt_correo.text(), self.txt_clave.text())
        except ValueError as error:          # por si la base rechaza un líder repetido
            self.lbl_error.setText(str(error))
            return
        self.accept()
