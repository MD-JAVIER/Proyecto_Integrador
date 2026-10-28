"""
pagina_asistencia.py
--------------------
Pantalla del LÍDER para marcar quién asistió a un culto.

Muestra solo a los miembros de su ministerio. Al guardar, el estado de cada miembro
cambia solo: quien asistió queda activo y quien pasa 15 días sin asistir pasa a inactivo.
Solo dibuja y reacciona a los clics; las reglas están en controlador_asistencia.
"""
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QCheckBox, QTableWidget, QHeaderView, QAbstractItemView, QStackedLayout
)

from modulos.asistencia import controlador_asistencia as controlador

COLUMNAS = ["Miembro", "Estado", "Última asistencia", "Asistió"]


class PaginaAsistencia(QWidget):
    def __init__(self, id_ministerio):
        super().__init__()
        self.setObjectName("pagina")
        self._ministerio = id_ministerio
        self._checks = {}                       # {id_miembro: casilla}

        self._temporizador = QTimer(self)       # oculta el aviso de "guardado" después de unos segundos
        self._temporizador.setSingleShot(True)
        self._temporizador.setInterval(6000)
        self._temporizador.timeout.connect(lambda: self.lbl_estado.setVisible(False))

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(14)
        lay.addLayout(self._crear_encabezado())
        lay.addLayout(self._crear_barra())
        lay.addWidget(self._crear_tabla(), 1)

        self.refrescar()

    # ======================= construcción =======================
    def _crear_encabezado(self):
        titulo = QLabel("Asistencia")
        titulo.setObjectName("titulo_pagina")
        subtitulo = QLabel("Marca quién asistió al culto")
        subtitulo.setObjectName("subtitulo_pagina")
        textos = QVBoxLayout()
        textos.setSpacing(0)
        textos.addWidget(titulo)
        textos.addWidget(subtitulo)

        self.btn_guardar = QPushButton("Guardar asistencia")
        self.btn_guardar.setObjectName("boton_lleno")
        self.btn_guardar.setCursor(Qt.PointingHandCursor)
        self.btn_guardar.clicked.connect(self._guardar)

        fila = QHBoxLayout()
        fila.addLayout(textos, 1)
        fila.addWidget(self.btn_guardar)
        return fila

    def _crear_barra(self):
        lbl = QLabel("Culto")
        lbl.setObjectName("etiqueta_form")
        self.cmb_culto = QComboBox()
        self.cmb_culto.setObjectName("selector_culto")
        self.cmb_culto.currentIndexChanged.connect(self._cargar_lista)

        self.lbl_contador = QLabel("")
        self.lbl_contador.setObjectName("contador_asistencia")

        btn_todos = QPushButton("Marcar todos")
        btn_ninguno = QPushButton("Quitar todos")
        for boton, valor in ((btn_todos, True), (btn_ninguno, False)):
            boton.setObjectName("boton_pequeno")
            boton.setCursor(Qt.PointingHandCursor)
            boton.clicked.connect(lambda _=False, v=valor: self._marcar_todos(v))

        self.lbl_estado = QLabel("")
        self.lbl_estado.setObjectName("estado_guardado")
        self.lbl_estado.setVisible(False)

        fila = QHBoxLayout()
        fila.setSpacing(10)
        fila.addWidget(lbl)
        fila.addWidget(self.cmb_culto)
        fila.addWidget(self.lbl_contador)
        fila.addStretch()
        fila.addWidget(btn_todos)
        fila.addWidget(btn_ninguno)

        bloque = QVBoxLayout()
        bloque.setSpacing(8)
        bloque.addLayout(fila)
        bloque.addWidget(self.lbl_estado, alignment=Qt.AlignLeft)
        return bloque

    def _crear_tabla(self):
        marco = QFrame()
        marco.setObjectName("tarjeta_fija")
        lay = QVBoxLayout(marco)
        lay.setContentsMargins(12, 8, 12, 8)

        self.tabla = QTableWidget(0, len(COLUMNAS))
        self.tabla.setObjectName("tabla")
        self.tabla.setHorizontalHeaderLabels(COLUMNAS)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.verticalHeader().setDefaultSectionSize(54)
        self.tabla.setShowGrid(False)
        self.tabla.setSelectionMode(QAbstractItemView.NoSelection)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.setFocusPolicy(Qt.NoFocus)
        encabezado = self.tabla.horizontalHeader()
        encabezado.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        encabezado.setHighlightSections(False)
        encabezado.setSectionResizeMode(0, QHeaderView.Stretch)
        for columna, ancho in ((1, 130), (2, 210), (3, 90)):
            encabezado.setSectionResizeMode(columna, QHeaderView.Fixed)
            self.tabla.setColumnWidth(columna, ancho)

        self.lbl_vacio = QLabel("No hay cultos para registrar.\n"
                                "Solo se puede registrar la asistencia de los cultos de los últimos 7 días.")
        self.lbl_vacio.setObjectName("vacio")
        self.lbl_vacio.setAlignment(Qt.AlignCenter)

        self._pila = QStackedLayout()
        self._pila.addWidget(self.tabla)
        self._pila.addWidget(self.lbl_vacio)
        lay.addLayout(self._pila)
        return marco

    # ======================= datos =======================
    def refrescar(self):
        """Vuelve a pedir los cultos y la lista (conserva el culto elegido si sigue disponible)."""
        elegido = self.cmb_culto.currentData()
        self.cmb_culto.blockSignals(True)
        self.cmb_culto.clear()
        for culto in controlador.cargar_cultos(self._ministerio):
            self.cmb_culto.addItem(culto["texto"], culto["id"])
        posicion = self.cmb_culto.findData(elegido)
        self.cmb_culto.setCurrentIndex(posicion if posicion >= 0 else 0)
        self.cmb_culto.blockSignals(False)
        self._cargar_lista()

    def _limpiar_tabla(self):
        for fila in range(self.tabla.rowCount()):
            for columna in range(self.tabla.columnCount()):
                celda = self.tabla.cellWidget(fila, columna)
                if celda is not None:
                    self.tabla.removeCellWidget(fila, columna)
                    celda.hide()
                    celda.deleteLater()
        self.tabla.setRowCount(0)
        self._checks = {}

    def _cargar_lista(self):
        self._limpiar_tabla()
        id_evento = self.cmb_culto.currentData()
        hay_culto = id_evento is not None
        self.btn_guardar.setEnabled(hay_culto)
        self._pila.setCurrentIndex(0 if hay_culto else 1)
        if not hay_culto:
            self.lbl_contador.setText("")
            return

        filas = controlador.cargar_lista(id_evento, self._ministerio)
        self.tabla.setRowCount(len(filas))
        for i, f in enumerate(filas):
            self.tabla.setCellWidget(i, 0, self._celda_nombre(f))
            self.tabla.setCellWidget(i, 1, self._celda_estado(f))
            self.tabla.setCellWidget(i, 2, self._celda_ultima(f))
            self.tabla.setCellWidget(i, 3, self._celda_casilla(f))
        self._actualizar_contador()

    # ---------- celdas ----------
    def _contenedor(self, direccion=QHBoxLayout):
        widget = QWidget()
        lay = direccion(widget)
        lay.setContentsMargins(8, 0, 6, 0)
        return widget, lay

    def _celda_nombre(self, f):
        widget, lay = self._contenedor()
        lay.setSpacing(10)
        avatar = QLabel(f["iniciales"])
        avatar.setObjectName("avatar_miembro" if f["activo"] else "avatar_miembro_inactivo")
        avatar.setFixedSize(32, 32)
        avatar.setAlignment(Qt.AlignCenter)
        nombre = QLabel(f["nombre"])
        nombre.setObjectName("texto_tabla")
        lay.addWidget(avatar)
        lay.addWidget(nombre, 1)
        return widget

    def _celda_estado(self, f):
        widget, lay = self._contenedor()
        chip = QLabel("Activo" if f["activo"] else "Inactivo")
        chip.setObjectName("chip_activo" if f["activo"] else "chip_inactivo")
        lay.addWidget(chip, alignment=Qt.AlignVCenter)
        lay.addStretch()
        return widget

    def _celda_ultima(self, f):
        widget, lay = self._contenedor(QVBoxLayout)
        lay.setSpacing(0)
        lay.setAlignment(Qt.AlignVCenter)
        lbl = QLabel(f["ultima"])
        lbl.setObjectName("texto_tabla")
        lay.addWidget(lbl)
        if f["aviso"]:
            aviso = QLabel("Cerca de quedar inactivo")
            aviso.setObjectName("aviso_asistencia")
            lay.addWidget(aviso)
        return widget

    def _celda_casilla(self, f):
        widget, lay = self._contenedor()
        casilla = QCheckBox()
        casilla.setChecked(f["presente"])
        casilla.setCursor(Qt.PointingHandCursor)
        casilla.stateChanged.connect(lambda _: self._actualizar_contador())
        self._checks[f["id"]] = casilla
        lay.addWidget(casilla)
        lay.addStretch()
        return widget

    # ======================= eventos =======================
    def _actualizar_contador(self):
        presentes = sum(1 for c in self._checks.values() if c.isChecked())
        self.lbl_contador.setText(f"Presentes: {presentes} de {len(self._checks)}")

    def _marcar_todos(self, valor):
        for casilla in self._checks.values():
            casilla.setChecked(valor)

    def _guardar(self):
        id_evento = self.cmb_culto.currentData()
        if id_evento is None:
            return
        marcas = {i: c.isChecked() for i, c in self._checks.items()}
        resultado = controlador.guardar(id_evento, marcas)

        texto = f'Asistencia guardada: {resultado["presentes"]} presentes.'
        if resultado["reactivados"]:
            texto += f' {resultado["reactivados"]} reactivado(s).'
        if resultado["inactivados"]:
            texto += f' {resultado["inactivados"]} pasaron a inactivos por 15 días sin asistir.'
        self.lbl_estado.setText(texto)
        self.lbl_estado.setVisible(True)
        self._temporizador.start()
        self._cargar_lista()            # vuelve a dibujar con los estados ya actualizados
