"""
pagina_finanzas.py
------------------
Área "Finanzas" del pastor: resumen del año, gráfico de ofrendas por mes
(igual al del Panel) e historial mensual.

Regla: solo se permite una ofrenda por mes. Si el mes ya tiene monto, solo se edita.
Solo dibuja y reacciona a los clics; los datos y las reglas están en controlador_finanzas.
"""
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QTableWidget, QHeaderView, QAbstractItemView
)

from modulos.comunes.iconos import icono
from modulos.dashboard.componentes import GraficoPildoras
from modulos.dashboard.estilos_dashboard import VERDE_OSCURO
from modulos.finanzas import controlador_finanzas as controlador
from modulos.informes.dialogo_informe import DialogoInforme
from modulos.finanzas.dialogo_ofrenda import DialogoOfrenda

COLUMNAS = ["Mes", "Monto", "Registrado por", "Acciones"]


class PaginaFinanzas(QWidget):
    def __init__(self, correo):
        super().__init__()
        self.setObjectName("pagina")
        self._correo = correo
        self._anio = controlador.anio_actual()

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(14)
        lay.addLayout(self._crear_encabezado())
        lay.addLayout(self._crear_tarjetas())
        lay.addWidget(self._crear_grafico(), 1)
        lay.addWidget(self._crear_historial(), 1)

        self.refrescar()

    # ======================= construcción =======================
    def _crear_encabezado(self):
        titulo = QLabel("Finanzas")
        titulo.setObjectName("titulo_pagina")
        subtitulo = QLabel("Ofrendas mensuales de la iglesia")
        subtitulo.setObjectName("subtitulo_pagina")
        textos = QVBoxLayout()
        textos.setSpacing(0)
        textos.addWidget(titulo)
        textos.addWidget(subtitulo)

        self.btn_registrar = QPushButton()
        self.btn_registrar.setObjectName("boton_lleno")
        self.btn_registrar.setCursor(Qt.PointingHandCursor)
        self.btn_registrar.setIconSize(QSize(16, 16))
        self.btn_registrar.setText("  Agregar ofrenda")
        self.btn_registrar.setIcon(icono("mas", "#FFFFFF", tamano=16))
        self.btn_registrar.clicked.connect(lambda: self._registrar(self._anio, None))

        btn_informe = QPushButton("Informe de ofrendas")
        btn_informe.setObjectName("boton_borde")
        btn_informe.setCursor(Qt.PointingHandCursor)
        btn_informe.clicked.connect(lambda: DialogoInforme(self, "ofrendas").exec())

        fila = QHBoxLayout()
        fila.addLayout(textos, 1)
        fila.addWidget(btn_informe)
        fila.addSpacing(8)
        fila.addWidget(self.btn_registrar)
        return fila

    def _tarjeta(self, destacada=False):
        """Tarjeta con título, número grande y detalle. Devuelve (tarjeta, titulo, numero, detalle)."""
        tarjeta = QFrame()
        tarjeta.setObjectName("tarjeta_destacada" if destacada else "tarjeta_fija")
        tarjeta.setMinimumHeight(98)
        sufijo = "_blanco" if destacada else ""
        lbl_titulo = QLabel("")
        lbl_titulo.setObjectName("titulo_tarjeta" + sufijo)
        lbl_numero = QLabel("")
        lbl_numero.setObjectName("numero_tarjeta" + sufijo)
        lbl_detalle = QLabel("")
        lbl_detalle.setObjectName("detalle_tarjeta" + sufijo)
        lay = QVBoxLayout(tarjeta)
        lay.setContentsMargins(18, 12, 18, 12)
        lay.setSpacing(0)
        lay.addWidget(lbl_titulo)
        lay.addWidget(lbl_numero)
        lay.addWidget(lbl_detalle)
        return tarjeta, lbl_titulo, lbl_numero, lbl_detalle

    def _crear_tarjetas(self):
        fila = QHBoxLayout()
        fila.setSpacing(14)
        self._tarjetas = {}
        for clave, destacada in (("total", True), ("mes", False), ("mejor", False), ("promedio", False)):
            tarjeta, titulo, numero, detalle = self._tarjeta(destacada)
            self._tarjetas[clave] = (titulo, numero, detalle)
            fila.addWidget(tarjeta, 1)
        # El título de la primera tarjeta es fijo
        self._tarjetas["total"][0].setText("Total del año")
        return fila

    def _crear_grafico(self):
        marco = QFrame()
        marco.setObjectName("tarjeta_fija")

        titulo = QLabel("Ofrendas por mes")
        titulo.setObjectName("titulo_seccion")
        self.cmb_anio = QComboBox()
        self.cmb_anio.setObjectName("filtro_anio")
        self.cmb_anio.currentIndexChanged.connect(self._cambio_anio)

        cabecera = QHBoxLayout()
        cabecera.addWidget(titulo)
        cabecera.addStretch()
        cabecera.addWidget(self.cmb_anio)

        self.grafico = GraficoPildoras(ancho_barra=34)

        lay = QVBoxLayout(marco)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.addLayout(cabecera)
        lay.addWidget(self.grafico, 1)
        return marco

    def _crear_historial(self):
        marco = QFrame()
        marco.setObjectName("tarjeta_fija")
        lay = QVBoxLayout(marco)
        lay.setContentsMargins(12, 8, 12, 8)

        self.tabla = QTableWidget(0, len(COLUMNAS))
        self.tabla.setObjectName("tabla")
        self.tabla.setHorizontalHeaderLabels(COLUMNAS)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.verticalHeader().setDefaultSectionSize(46)
        self.tabla.setShowGrid(False)
        self.tabla.setSelectionMode(QAbstractItemView.NoSelection)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.setFocusPolicy(Qt.NoFocus)
        encabezado = self.tabla.horizontalHeader()
        encabezado.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        encabezado.setHighlightSections(False)
        encabezado.setSectionResizeMode(0, QHeaderView.Stretch)
        for columna, ancho in ((1, 170), (2, 170), (3, 130)):
            encabezado.setSectionResizeMode(columna, QHeaderView.Fixed)
            self.tabla.setColumnWidth(columna, ancho)

        lay.addWidget(self.tabla)
        return marco

    # ======================= datos =======================
    def refrescar(self):
        """Vuelve a pedir los datos y redibuja todo."""
        # Años disponibles (se conserva el año elegido)
        self.cmb_anio.blockSignals(True)
        self.cmb_anio.clear()
        for anio in controlador.cargar_anios():
            self.cmb_anio.addItem(str(anio), anio)
        self.cmb_anio.setCurrentIndex(max(0, self.cmb_anio.findData(self._anio)))
        self.cmb_anio.blockSignals(False)

        # Botón principal: siempre dice "Agregar ofrenda"; el mes se elige en el formulario.
        # Se desactiva solo si el año elegido ya tiene todos sus meses registrados.
        hay_meses = bool(controlador.meses_disponibles(self._anio))
        self.btn_registrar.setEnabled(hay_meses)
        self.btn_registrar.setToolTip("" if hay_meses else "Todos los meses de este año ya tienen ofrenda")

        # Tarjetas
        resumen = controlador.cargar_resumen(self._anio)
        numero, detalle = resumen["total"]
        self._tarjetas["total"][1].setText(numero)
        self._tarjetas["total"][2].setText(detalle)
        for clave in ("mes", "mejor", "promedio"):
            titulo, numero, detalle = resumen[clave]
            self._tarjetas[clave][0].setText(titulo)
            self._tarjetas[clave][1].setText(numero)
            self._tarjetas[clave][2].setText(detalle)

        # Gráfico e historial
        self.grafico.establecer_datos(controlador.cargar_grafico(self._anio))
        self._llenar_historial(controlador.cargar_historial(self._anio))

    def _limpiar_tabla(self):
        for fila in range(self.tabla.rowCount()):
            for columna in range(self.tabla.columnCount()):
                celda = self.tabla.cellWidget(fila, columna)
                if celda is not None:
                    self.tabla.removeCellWidget(fila, columna)
                    celda.hide()
                    celda.deleteLater()
        self.tabla.setRowCount(0)

    def _llenar_historial(self, filas):
        self._limpiar_tabla()
        self.tabla.setRowCount(len(filas))
        for i, fila in enumerate(filas):
            self.tabla.setCellWidget(i, 0, self._celda_texto(fila["nombre_mes"]))
            self.tabla.setCellWidget(i, 1, self._celda_monto(fila))
            self.tabla.setCellWidget(i, 2, self._celda_texto(fila["registrado_por"]))
            self.tabla.setCellWidget(i, 3, self._celda_accion(fila))

    # ---------- celdas ----------
    def _contenedor(self):
        widget = QWidget()
        lay = QHBoxLayout(widget)
        lay.setContentsMargins(8, 0, 6, 0)
        return widget, lay

    def _celda_texto(self, texto):
        widget, lay = self._contenedor()
        lbl = QLabel(texto)
        lbl.setObjectName("texto_tabla")
        lay.addWidget(lbl)
        return widget

    def _celda_monto(self, fila):
        widget, lay = self._contenedor()
        if fila["pendiente"]:
            chip = QLabel("Pendiente")
            chip.setObjectName("chip_pendiente")
            lay.addWidget(chip, alignment=Qt.AlignVCenter)
            lay.addStretch()
        else:
            lbl = QLabel(fila["monto_texto"])
            lbl.setObjectName("texto_tabla")
            lay.addWidget(lbl)
        return widget

    def _celda_accion(self, fila):
        widget, lay = self._contenedor()
        if fila["pendiente"]:
            boton = QPushButton("Registrar")
            boton.setObjectName("boton_registrar")
            boton.clicked.connect(lambda _=False, m=fila["mes"]: self._registrar(self._anio, m))
        else:
            boton = QPushButton()
            boton.setObjectName("boton_icono")
            boton.setFixedSize(30, 30)
            boton.setIcon(icono("lapiz", VERDE_OSCURO, tamano=18))
            boton.setIconSize(QSize(18, 18))
            boton.setToolTip("Editar monto")
            boton.clicked.connect(lambda _=False, f=fila: self._editar(f))
        boton.setCursor(Qt.PointingHandCursor)
        lay.addWidget(boton)
        lay.addStretch()
        return widget

    # ======================= eventos =======================
    def _cambio_anio(self):
        self._anio = self.cmb_anio.currentData()
        self.refrescar()

    def _registrar(self, anio, mes):
        if DialogoOfrenda(self, anio, self._correo, mes=mes).exec():
            self._anio = anio
            self.refrescar()

    def _editar(self, fila):
        dialogo = DialogoOfrenda(self, self._anio, self._correo, mes=fila["mes"],
                                 id_ofrenda=fila["id"], monto=fila["monto"])
        if dialogo.exec():
            self.refrescar()
