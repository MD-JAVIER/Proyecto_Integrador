"""
dialogo_informe.py
------------------
Ventana para generar un informe en Word con el formato de la institución:
    tipo "miembros" -> Informe general de miembros (período: mes y año)
    tipo "ofrendas" -> Informe general de ofrendas (período: año)
    tipo "ministerio" -> Informe reducido de los miembros de UN ministerio (para su líder; mes y año)

Pide el nombre de la iglesia (se recuerda), el período y unas observaciones opcionales; luego
pregunta dónde guardar el archivo, lo genera y lo abre. Sin cuadros de mensaje: si algo falla,
el error aparece dentro de esta misma ventana.
"""
from datetime import date
from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPlainTextEdit,
    QPushButton, QFileDialog
)

from modulos.comunes.estilos import estilo_aplicacion
from modulos.informes import controlador_informes as controlador

TITULOS = {"miembros": "Informe general de miembros", "ofrendas": "Informe general de ofrendas",
           "ministerio": "Informe de miembros del ministerio"}


class DialogoInforme(QDialog):
    def __init__(self, parent=None, tipo="miembros", id_ministerio=None):
        super().__init__(parent)
        self._tipo = tipo
        self._ministerio = id_ministerio
        self.ruta_generada = None
        self.setStyleSheet(estilo_aplicacion())
        titulo_ventana = TITULOS[tipo]
        if tipo == "ministerio":
            titulo_ventana += f" {controlador.nombre_ministerio(id_ministerio)}"
        self.setWindowTitle(titulo_ventana)
        self.setModal(True)
        self.setMinimumWidth(520)

        titulo = QLabel(titulo_ventana)
        titulo.setObjectName("titulo_dialogo")

        self.txt_iglesia = QLineEdit(controlador.nombre_iglesia_guardado())
        self.txt_iglesia.setPlaceholderText("Nombre de la iglesia o congregación")

        # ----- período -----
        self.cmb_mes = QComboBox()
        for numero, nombre in enumerate(controlador.MESES, start=1):
            self.cmb_mes.addItem(nombre, numero)
        self.cmb_mes.setCurrentIndex(date.today().month - 1)
        self.cmb_anio = QComboBox()
        anios = controlador.anios_para_ofrendas() if tipo == "ofrendas" else controlador.anios_para_miembros()
        for anio in anios:
            self.cmb_anio.addItem(str(anio), anio)

        self.txt_observaciones = QPlainTextEdit()
        self.txt_observaciones.setPlaceholderText("Opcional. Se escribe en «Observaciones generales».")
        self.txt_observaciones.setFixedHeight(80)
        self.txt_observaciones.setObjectName("observaciones_informe")

        if tipo == "miembros":
            aviso = ("El resumen y la clasificación muestran el estado actual del sistema. "
                     "Los nuevos miembros se cuentan en el mes elegido.")
        elif tipo == "ministerio":
            aviso = ("Informe reducido de los miembros de tu ministerio. El resumen muestra el estado actual; "
                     "los nuevos miembros se cuentan en el mes elegido.")
        else:
            aviso = "Incluye las ofrendas registradas del año elegido, mes por mes, con su total."
        lbl_aviso = QLabel(aviso)
        lbl_aviso.setObjectName("aviso_form")
        lbl_aviso.setWordWrap(True)

        self.lbl_error = QLabel("")
        self.lbl_error.setObjectName("error_form")
        self.lbl_error.setWordWrap(True)

        btn_generar = QPushButton("Generar informe")
        btn_generar.setObjectName("boton_lleno")
        btn_generar.setCursor(Qt.PointingHandCursor)
        btn_generar.clicked.connect(self._generar)
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("boton_texto")
        btn_cancelar.setCursor(Qt.PointingHandCursor)
        btn_cancelar.clicked.connect(self.reject)
        botones = QHBoxLayout()
        botones.addStretch()
        botones.addWidget(btn_cancelar)
        botones.addWidget(btn_generar)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 24, 28, 22)
        lay.setSpacing(6)
        lay.addWidget(titulo)
        lay.addSpacing(8)
        lay.addWidget(self._etiqueta("Iglesia o congregación"))
        lay.addWidget(self.txt_iglesia)
        lay.addSpacing(6)
        if tipo in ("miembros", "ministerio"):
            fila = QHBoxLayout()
            fila.setSpacing(16)
            fila.addLayout(self._columna("Mes", self.cmb_mes), 1)
            fila.addLayout(self._columna("Año", self.cmb_anio), 1)
            lay.addLayout(fila)
        else:
            lay.addWidget(self._etiqueta("Año"))
            lay.addWidget(self.cmb_anio)
        lay.addSpacing(6)
        lay.addWidget(self._etiqueta("Observaciones generales"))
        lay.addWidget(self.txt_observaciones)
        lay.addWidget(lbl_aviso)
        lay.addWidget(self.lbl_error)
        lay.addLayout(botones)

    # ---------- construcción ----------
    def _etiqueta(self, texto):
        lbl = QLabel(texto)
        lbl.setObjectName("etiqueta_form")
        return lbl

    def _columna(self, texto, campo):
        col = QVBoxLayout()
        col.setSpacing(4)
        col.addWidget(self._etiqueta(texto))
        col.addWidget(campo)
        return col

    # ---------- generar ----------
    def _generar(self):
        anio = self.cmb_anio.currentData()
        mes = self.cmb_mes.currentData()
        ministerio = controlador.nombre_ministerio(self._ministerio) if self._tipo == "ministerio" else ""
        sugerido = controlador.nombre_archivo(self._tipo, anio, mes, ministerio)
        carpeta = Path.home() / "Documents"
        inicio = str((carpeta if carpeta.exists() else Path.home()) / sugerido)

        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar informe", inicio, "Documento de Word (*.docx)")
        if not ruta:
            return                                   # el usuario canceló: no pasa nada
        if not ruta.lower().endswith(".docx"):
            ruta += ".docx"

        iglesia = self.txt_iglesia.text()
        observaciones = self.txt_observaciones.toPlainText()
        try:
            if self._tipo == "miembros":
                controlador.generar_informe_miembros(ruta, iglesia, anio, mes, observaciones)
            elif self._tipo == "ministerio":
                controlador.generar_informe_ministerio(ruta, self._ministerio, iglesia, anio, mes, observaciones)
            else:
                controlador.generar_informe_ofrendas(ruta, iglesia, anio, observaciones)
        except PermissionError:
            self.lbl_error.setText("No se pudo guardar: el archivo está abierto en otro programa. "
                                   "Ciérrelo o elija otro nombre.")
            return
        except OSError as error:
            self.lbl_error.setText(f"No se pudo guardar el informe: {error}")
            return

        controlador.recordar_nombre_iglesia(iglesia)
        self.ruta_generada = ruta
        QDesktopServices.openUrl(QUrl.fromLocalFile(ruta))      # abre el documento
        self.accept()
