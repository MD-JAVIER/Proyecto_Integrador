"""
pagina_actividades.py
---------------------
Área "Actividades": tarjetas de resumen del mes, los 4 cultos de la semana,
historial con filtros (tipo y situación), paginación y formulario emergente.

Solo dibuja y reacciona a los clics; los datos y las reglas están en
controlador_actividades. Toda la página se desplaza hacia abajo (QScrollArea).
"""
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QComboBox, QButtonGroup, QTableWidget, QHeaderView, QAbstractItemView,
    QStackedLayout, QScrollArea
)

from modulos.actividades import controlador_actividades as controlador
from modulos.actividades.dialogo_actividad import DialogoActividad
from modulos.comunes.iconos import icono
from modulos.dashboard.estilos_dashboard import VERDE_OSCURO, VERDE

COLUMNAS = ["Actividad", "Ámbito", "Tipo", "Fecha", "Hora", "Lugar", "Estado", "Acciones"]
ROJO = "#B3261E"
CHIPS = {"Programada": "chip_programada", "Realizada": "chip_realizada",
         "Cancelada": "chip_cancelada", "Sin crear": "chip_sin_crear"}


def _vaciar(layout):
    """Quita todos los elementos de un layout (para volver a llenarlo con datos nuevos)."""
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.setParent(None)        # desaparece de inmediato
            widget.deleteLater()
        elif item.layout():
            _vaciar(item.layout())


class PaginaActividades(QWidget):
    def __init__(self, id_ministerio=None):
        """id_ministerio: None = vista del pastor; un número = vista del líder de ese ministerio."""
        super().__init__()
        self.setObjectName("pagina")
        self._vista = id_ministerio
        self._tipo = None            # None = todas, "Culto" o "Externo"
        self._situacion = None       # None, "proximas", "realizadas" o "canceladas"
        self._texto = ""
        self._pagina = 1

        self._temporizador = QTimer(self)
        self._temporizador.setSingleShot(True)
        self._temporizador.setInterval(250)
        self._temporizador.timeout.connect(self._aplicar_busqueda)

        # Encabezado fijo arriba y el resto dentro de un área con desplazamiento
        contenido = QWidget()
        contenido.setObjectName("contenido_scroll")
        cuerpo = QVBoxLayout(contenido)
        cuerpo.setContentsMargins(0, 0, 12, 0)
        cuerpo.setSpacing(14)
        cuerpo.addLayout(self._crear_tarjetas())
        cuerpo.addLayout(self._crear_semana())
        cuerpo.addLayout(self._crear_filtros())
        cuerpo.addWidget(self._crear_tabla())
        cuerpo.addLayout(self._crear_pie())
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
        titulo = QLabel("Actividades")
        titulo.setObjectName("titulo_pagina")
        subtitulo = QLabel("Cultos y eventos de la iglesia" if self._vista is None
                           else "Los cultos generales y las actividades de tu ministerio")
        subtitulo.setObjectName("subtitulo_pagina")
        textos = QVBoxLayout()
        textos.setSpacing(0)
        textos.addWidget(titulo)
        textos.addWidget(subtitulo)

        btn_nueva = QPushButton("  Nueva actividad")
        btn_nueva.setObjectName("boton_lleno")
        btn_nueva.setIcon(icono("mas", "#FFFFFF", tamano=16))
        btn_nueva.setIconSize(QSize(16, 16))
        btn_nueva.setCursor(Qt.PointingHandCursor)
        btn_nueva.clicked.connect(lambda: self._nueva())

        fila = QHBoxLayout()
        fila.addLayout(textos, 1)
        fila.addWidget(btn_nueva)
        return fila

    def _crear_tarjetas(self):
        fila = QHBoxLayout()
        fila.setSpacing(14)
        self._numeros = {}
        for clave, titulo, destacada in (
            ("total", "Actividades del mes", True),
            ("cultos", "Cultos", False),
            ("externos", "Eventos externos", False),
            ("canceladas", "Canceladas", False),
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

    def _crear_semana(self):
        bloque = QVBoxLayout()
        bloque.setSpacing(8)
        titulo = QLabel("Cultos de esta semana")
        titulo.setObjectName("titulo_seccion")
        bloque.addWidget(titulo)
        self.lay_semana = QHBoxLayout()
        self.lay_semana.setSpacing(14)
        bloque.addLayout(self.lay_semana)
        return bloque

    def _crear_filtros(self):
        self.txt_buscar = QLineEdit()
        self.txt_buscar.setObjectName("buscador")
        self.txt_buscar.setPlaceholderText("Buscar por nombre o lugar")
        self.txt_buscar.setClearButtonEnabled(True)
        self.txt_buscar.textChanged.connect(lambda _: self._temporizador.start())

        self._grupo_tipo = QButtonGroup(self)
        self._grupo_tipo.setExclusive(True)
        fila = QHBoxLayout()
        fila.setSpacing(8)
        fila.addWidget(self.txt_buscar, 1)
        for tipo, texto in ((None, "Todas"), ("Culto", "Cultos"), ("Externo", "Eventos externos")):
            boton = QPushButton(texto)
            boton.setObjectName("pildora")
            boton.setCheckable(True)
            boton.setCursor(Qt.PointingHandCursor)
            boton.clicked.connect(lambda _=False, t=tipo: self._elegir_tipo(t))
            self._grupo_tipo.addButton(boton)
            fila.addWidget(boton)
            if tipo is None:
                boton.setChecked(True)

        self.cmb_situacion = QComboBox()
        self.cmb_situacion.setObjectName("filtro")
        for texto, valor in (("Todas las situaciones", None), ("Próximas", "proximas"),
                             ("Realizadas", "realizadas"), ("Canceladas", "canceladas")):
            self.cmb_situacion.addItem(texto, valor)
        self.cmb_situacion.currentIndexChanged.connect(self._cambio_situacion)
        fila.addWidget(self.cmb_situacion)
        return fila

    def _crear_tabla(self):
        marco = QFrame()
        marco.setObjectName("tarjeta_fija")
        lay = QVBoxLayout(marco)
        lay.setContentsMargins(12, 8, 12, 8)

        self.tabla = QTableWidget(0, len(COLUMNAS))
        self.tabla.setObjectName("tabla")
        self.tabla.setHorizontalHeaderLabels(COLUMNAS)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.verticalHeader().setDefaultSectionSize(52)
        self.tabla.setShowGrid(False)
        self.tabla.setSelectionMode(QAbstractItemView.NoSelection)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.setFocusPolicy(Qt.NoFocus)
        self.tabla.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)   # la página es la que se desplaza
        encabezado = self.tabla.horizontalHeader()
        encabezado.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        encabezado.setHighlightSections(False)
        encabezado.setSectionResizeMode(0, QHeaderView.Stretch)
        for columna, ancho in ((1, 85), (2, 100), (3, 95), (4, 80), (5, 120), (6, 125), (7, 85)):
            encabezado.setSectionResizeMode(columna, QHeaderView.Fixed)
            self.tabla.setColumnWidth(columna, ancho)

        self.lbl_vacio = QLabel("No hay actividades que coincidan con la búsqueda.")
        self.lbl_vacio.setObjectName("vacio")
        self.lbl_vacio.setAlignment(Qt.AlignCenter)
        self.lbl_vacio.setMinimumHeight(120)

        self._pila = QStackedLayout()
        self._pila.addWidget(self.tabla)
        self._pila.addWidget(self.lbl_vacio)
        lay.addLayout(self._pila)
        return marco

    def _crear_pie(self):
        self.lbl_cuenta = QLabel("")
        self.lbl_cuenta.setObjectName("pie_tabla")
        self.lbl_pagina = QLabel("")
        self.lbl_pagina.setObjectName("pie_tabla")
        self.btn_anterior = QPushButton("‹")
        self.btn_siguiente = QPushButton("›")
        for boton, delta in ((self.btn_anterior, -1), (self.btn_siguiente, 1)):
            boton.setObjectName("boton_pagina")
            boton.setFixedSize(30, 28)
            boton.setCursor(Qt.PointingHandCursor)
            boton.clicked.connect(lambda _=False, d=delta: self._mover_pagina(d))
        fila = QHBoxLayout()
        fila.addWidget(self.lbl_cuenta, 1)
        fila.addWidget(self.btn_anterior)
        fila.addSpacing(6)
        fila.addWidget(self.lbl_pagina)
        fila.addSpacing(6)
        fila.addWidget(self.btn_siguiente)
        return fila

    # ======================= datos =======================
    def refrescar(self):
        """Vuelve a pedir los datos y redibuja tarjetas, semana y tabla."""
        for clave, cantidad in controlador.cargar_resumen(self._vista).items():
            self._numeros[clave].setText(str(cantidad))

        self._llenar_semana(controlador.cargar_semana(self._vista))

        datos = controlador.cargar_tabla(self._tipo, self._situacion, self._texto, self._pagina, self._vista)
        self._pagina = datos["pagina"]
        self._llenar_tabla(datos["filas"])

        if datos["total"]:
            self.lbl_cuenta.setText(f'Mostrando {datos["desde"]}–{datos["hasta"]} de {datos["total"]} actividades')
        else:
            self.lbl_cuenta.setText("Sin resultados")
        self.lbl_pagina.setText(f'Página {datos["pagina"]} de {datos["paginas"]}')
        self.btn_anterior.setEnabled(datos["pagina"] > 1)
        self.btn_siguiente.setEnabled(datos["pagina"] < datos["paginas"])
        self._pila.setCurrentIndex(0 if datos["filas"] else 1)

    # ---------- cultos de la semana ----------
    def _llenar_semana(self, tarjetas):
        _vaciar(self.lay_semana)
        for c in tarjetas:
            self.lay_semana.addWidget(self._tarjeta_culto(c), 1)

    def _tarjeta_culto(self, c):
        """Tarjeta de un culto. Si es hoy se resalta; si no existe, ofrece crearlo."""
        tarjeta = QFrame()
        tarjeta.setObjectName("tarjeta_destacada" if c["es_hoy"] else "tarjeta_fija")
        tarjeta.setMinimumHeight(128)
        sufijo = "_blanco" if c["es_hoy"] else ""

        lbl_dia = QLabel(c["dia"])
        lbl_dia.setObjectName("dia_culto" + sufijo)
        lbl_fecha = QLabel(c["fecha_texto"])
        lbl_fecha.setObjectName("fecha_culto" + sufijo)

        boton = None
        if c["creada"] and c["gestionable"]:                    # lo puede editar quien es dueño
            boton = QPushButton()
            boton.setObjectName("boton_icono")
            boton.setFixedSize(30, 30)
            boton.setIcon(icono("lapiz", "#FFFFFF" if c["es_hoy"] else VERDE_OSCURO, tamano=18))
            boton.setIconSize(QSize(18, 18))
            boton.setToolTip("Editar culto")
            boton.clicked.connect(lambda _=False, i=c["id"]: self._editar(i))
        elif c["puede_crear"]:                                  # lo puede crear quien es dueño
            boton = QPushButton("Crear")
            boton.setObjectName("boton_registrar")
            boton.clicked.connect(lambda _=False, f=c["fecha"]: self._nueva(f))
        if boton is not None:
            boton.setCursor(Qt.PointingHandCursor)
        if c["creada"]:
            detalle = f'{c["ambito"]} · {c["hora"]} · {c["lugar"]}'
        elif c["puede_crear"]:
            detalle = f'{c["ambito"]} · todavía no está en el calendario'
        else:
            detalle = f'{c["ambito"]} · lo crea su líder' if c["ambito"] != "General" else "General · sin crear"

        chip = QLabel(c["situacion"])
        chip.setObjectName(CHIPS[c["situacion"]])
        lbl_detalle = QLabel(detalle)
        lbl_detalle.setObjectName("detalle_culto" + sufijo)
        lbl_detalle.setWordWrap(True)

        arriba = QHBoxLayout()
        arriba.addWidget(lbl_dia)
        arriba.addStretch()
        if boton is not None:
            arriba.addWidget(boton)
        fila_chip = QHBoxLayout()
        fila_chip.addWidget(chip)
        fila_chip.addStretch()

        lay = QVBoxLayout(tarjeta)
        lay.setContentsMargins(16, 12, 14, 12)
        lay.setSpacing(2)
        lay.addLayout(arriba)
        lay.addWidget(lbl_fecha)
        lay.addStretch()
        lay.addLayout(fila_chip)
        lay.addWidget(lbl_detalle)
        return tarjeta

    # ---------- tabla ----------
    def _limpiar_tabla(self):
        for fila in range(self.tabla.rowCount()):
            for columna in range(self.tabla.columnCount()):
                celda = self.tabla.cellWidget(fila, columna)
                if celda is not None:
                    self.tabla.removeCellWidget(fila, columna)
                    celda.hide()
                    celda.deleteLater()
        self.tabla.setRowCount(0)

    def _llenar_tabla(self, filas):
        self._limpiar_tabla()
        self.tabla.setRowCount(len(filas))
        for i, f in enumerate(filas):
            self.tabla.setCellWidget(i, 0, self._celda_texto(f["nombre"]))
            self.tabla.setCellWidget(i, 1, self._celda_texto(f["ambito"]))
            self.tabla.setCellWidget(i, 2, self._celda_texto(f["tipo"]))
            self.tabla.setCellWidget(i, 3, self._celda_texto(f["fecha"]))
            self.tabla.setCellWidget(i, 4, self._celda_texto(f["hora"]))
            self.tabla.setCellWidget(i, 5, self._celda_texto(f["lugar"]))
            self.tabla.setCellWidget(i, 6, self._celda_estado(f))
            self.tabla.setCellWidget(i, 7, self._celda_acciones(f))
        # La tabla no se desplaza sola: se ajusta su alto al número de filas
        alto = self.tabla.horizontalHeader().sizeHint().height() + len(filas) * 52 + 4
        self.tabla.setFixedHeight(max(alto, 60))

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

    def _celda_estado(self, fila):
        widget, lay = self._contenedor()
        chip = QLabel(fila["situacion"])
        chip.setObjectName(CHIPS[fila["situacion"]])
        lay.addWidget(chip, alignment=Qt.AlignVCenter)
        lay.addStretch()
        return widget

    def _celda_acciones(self, fila):
        widget, lay = self._contenedor()
        lay.setSpacing(2)
        botones = []
        if fila["gestionable"]:                       # lo que no es suyo, solo se ve
            botones.append(("lapiz", VERDE_OSCURO, "Editar", lambda: self._editar(fila["id"])))
        if fila["se_puede_cancelar"]:
            botones.append(("cerrar", ROJO, "Cancelar actividad", lambda: self._cambiar_estado(fila)))
        elif fila["cancelada"] and fila["gestionable"]:
            botones.append(("reiniciar", VERDE, "Reactivar actividad", lambda: self._cambiar_estado(fila)))
        for nombre_icono, color, ayuda, accion in botones:
            boton = QPushButton()
            boton.setObjectName("boton_icono")
            boton.setFixedSize(30, 30)
            boton.setIcon(icono(nombre_icono, color, tamano=18))
            boton.setIconSize(QSize(18, 18))
            boton.setToolTip(ayuda)
            boton.setCursor(Qt.PointingHandCursor)
            boton.clicked.connect(lambda _=False, f=accion: f())
            lay.addWidget(boton)
        lay.addStretch()
        return widget

    # ======================= eventos =======================
    def _elegir_tipo(self, tipo):
        self._tipo = tipo
        self._pagina = 1
        self.refrescar()

    def _cambio_situacion(self):
        self._situacion = self.cmb_situacion.currentData()
        self._pagina = 1
        self.refrescar()

    def _aplicar_busqueda(self):
        self._texto = self.txt_buscar.text().strip()
        self._pagina = 1
        self.refrescar()

    def _mover_pagina(self, delta):
        self._pagina += delta
        self.refrescar()

    def _nueva(self, fecha=None):
        """Abre el formulario. Si viene una fecha (desde un culto de la semana), es un Culto."""
        tipo = "Culto" if fecha is not None else "Culto"
        if DialogoActividad(self, fecha=fecha, tipo=tipo, vista=self._vista).exec():
            self.refrescar()

    def _editar(self, id_evento):
        DialogoActividad(self, id_evento=id_evento, vista=self._vista).exec()
        self.refrescar()

    def _cambiar_estado(self, fila):
        """Cancela o reactiva directamente (se puede deshacer con el mismo botón)."""
        (controlador.reactivar if fila["cancelada"] else controlador.cancelar)(fila["id"])
        self.refrescar()
