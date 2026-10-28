"""
pagina_miembros.py
------------------
Área "Miembros": tarjetas de resumen, buscador, filtros, tabla paginada y
acciones (ver, editar, desactivar/reactivar, nuevo miembro).

Solo dibuja y reacciona a los clics; los datos y las reglas los pide a
controlador_miembros.

`ministerio_fijo`: para el rol Líder se le pasará el id de su ministerio y la
pantalla mostrará solo esos miembros (el filtro se aplica en la consulta).
"""
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QComboBox, QButtonGroup, QTableWidget, QHeaderView, QAbstractItemView,
    QStackedLayout
)

from modulos.comunes.iconos import icono
from modulos.dashboard.componentes import TarjetaClicable
from modulos.dashboard.estilos_dashboard import VERDE_OSCURO, VERDE
from modulos.miembros import controlador_miembros as controlador
from modulos.informes.dialogo_informe import DialogoInforme
from modulos.miembros.dialogo_detalle import DialogoDetalle
from modulos.miembros.dialogo_miembro import DialogoMiembro

COLUMNAS = ["Miembro", "Ministerio", "Teléfono", "Última asistencia", "Estado", "Acciones"]
ROJO = "#B3261E"


class PaginaMiembros(QWidget):
    def __init__(self, ministerio_fijo=None, solo_lectura=False):
        """solo_lectura: el líder ve a sus miembros pero no los crea, edita ni desactiva (eso lo hace el pastor)."""
        super().__init__()
        self.setObjectName("pagina")
        self._solo_lectura = solo_lectura
        self._ministerio_fijo = ministerio_fijo
        self._estado = None                 # None = todos, 1 = activos, 0 = inactivos
        self._solo_nuevos = False           # True = solo los que ingresaron este mes
        self._ministerio = ministerio_fijo  # id de ministerio o None
        self._texto = ""
        self._pagina = 1

        # Espera un momento después de escribir para no consultar en cada letra
        self._temporizador = QTimer(self)
        self._temporizador.setSingleShot(True)
        self._temporizador.setInterval(250)
        self._temporizador.timeout.connect(self._aplicar_busqueda)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(14)
        lay.addLayout(self._crear_encabezado())
        lay.addLayout(self._crear_tarjetas())
        lay.addLayout(self._crear_filtros())
        lay.addWidget(self._crear_tabla(), 1)
        lay.addLayout(self._crear_pie())

        self.refrescar()

    # ======================= construcción =======================
    def _crear_encabezado(self):
        titulo = QLabel("Mis miembros" if self._solo_lectura else "Miembros")
        titulo.setObjectName("titulo_pagina")
        subtitulo = QLabel("Los miembros de tu ministerio" if self._solo_lectura
                           else "Todos los miembros de la iglesia")
        subtitulo.setObjectName("subtitulo_pagina")
        textos = QVBoxLayout()
        textos.setSpacing(0)
        textos.addWidget(titulo)
        textos.addWidget(subtitulo)

        btn_importar = QPushButton("Informe de miembros")
        btn_importar.setObjectName("boton_borde")
        btn_importar.clicked.connect(self._informe)
        btn_nuevo = QPushButton("  Nuevo miembro")
        btn_nuevo.setObjectName("boton_lleno")
        btn_nuevo.setIcon(icono("mas", "#FFFFFF", tamano=16))
        btn_nuevo.setIconSize(QSize(16, 16))
        btn_nuevo.clicked.connect(self._nuevo)
        for boton in (btn_importar, btn_nuevo):
            boton.setCursor(Qt.PointingHandCursor)

        fila = QHBoxLayout()
        fila.addLayout(textos, 1)
        if self._solo_lectura:                       # el líder no crea miembros, pero sí entrega su informe
            btn_informe = QPushButton("Informe de mi ministerio")
            btn_informe.setObjectName("boton_lleno")
            btn_informe.setCursor(Qt.PointingHandCursor)
            btn_informe.clicked.connect(
                lambda: DialogoInforme(self, "ministerio", self._ministerio_fijo).exec())
            fila.addWidget(btn_informe)
        else:
            fila.addWidget(btn_importar)
            fila.addSpacing(8)
            fila.addWidget(btn_nuevo)
        return fila

    def _tarjeta(self, titulo, destacada=False, filtro=False):
        """Tarjeta con título y número. Si `filtro` es True, al hacer clic filtra la tabla."""
        tarjeta = TarjetaClicable()
        tarjeta.setObjectName("tarjeta_destacada" if destacada else "tarjeta")
        tarjeta.setMinimumHeight(86)
        if not filtro:
            tarjeta.setCursor(Qt.ArrowCursor)
        sufijo = "_blanco" if destacada else ""
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setObjectName("titulo_tarjeta" + sufijo)
        lbl_numero = QLabel("0")
        lbl_numero.setObjectName("numero_tarjeta" + sufijo)
        lay = QVBoxLayout(tarjeta)
        lay.setContentsMargins(18, 12, 18, 12)
        lay.addWidget(lbl_titulo)
        lay.addWidget(lbl_numero)
        return tarjeta, lbl_numero

    def _crear_tarjetas(self):
        fila = QHBoxLayout()
        fila.setSpacing(14)
        self._numeros = {}
        definicion = [
            ("total", "Total", True, True, None),
            ("activos", "Activos", False, True, 1),
            ("inactivos", "Inactivos", False, True, 0),
            ("nuevos_mes", "Nuevos este mes", False, True, "nuevos"),
        ]
        for clave, titulo, destacada, filtro, estado in definicion:
            tarjeta, lbl = self._tarjeta(titulo, destacada, filtro)
            self._numeros[clave] = lbl
            if filtro:
                tarjeta.clicked.connect(lambda e=estado: self._elegir_estado(e))
            fila.addWidget(tarjeta, 1)
        return fila

    def _crear_filtros(self):
        self.txt_buscar = QLineEdit()
        self.txt_buscar.setObjectName("buscador")
        self.txt_buscar.setPlaceholderText("Buscar por nombre o teléfono")
        self.txt_buscar.setClearButtonEnabled(True)
        self.txt_buscar.textChanged.connect(lambda _: self._temporizador.start())

        # Píldoras: Todos / Activos / Inactivos (solo una marcada a la vez)
        self._grupo_estado = QButtonGroup(self)
        self._grupo_estado.setExclusive(True)
        self._pildoras = {}
        fila = QHBoxLayout()
        fila.setSpacing(8)
        fila.addWidget(self.txt_buscar, 1)
        for estado, texto in ((None, "Todos"), (1, "Activos"), (0, "Inactivos"), ("nuevos", "Nuevos")):
            boton = QPushButton(texto)
            boton.setObjectName("pildora")
            boton.setCheckable(True)
            boton.setCursor(Qt.PointingHandCursor)
            boton.clicked.connect(lambda _=False, e=estado: self._elegir_estado(e))
            self._grupo_estado.addButton(boton)
            self._pildoras[estado] = boton
            fila.addWidget(boton)
        self._pildoras[None].setChecked(True)

        # Filtro por ministerio
        self.cmb_ministerio = QComboBox()
        self.cmb_ministerio.setObjectName("filtro")
        self.cmb_ministerio.addItem("Todos los ministerios", None)
        for id_min, nombre in controlador.cargar_ministerios():
            self.cmb_ministerio.addItem(nombre, id_min)
        if self._ministerio_fijo is not None:       # el Líder no puede cambiar de ministerio
            self.cmb_ministerio.setCurrentIndex(self.cmb_ministerio.findData(self._ministerio_fijo))
            self.cmb_ministerio.setEnabled(False)
        self.cmb_ministerio.currentIndexChanged.connect(self._cambio_ministerio)
        fila.addWidget(self.cmb_ministerio)
        return fila

    def _crear_tabla(self):
        marco = QFrame()
        marco.setObjectName("tarjeta")
        lay = QVBoxLayout(marco)
        lay.setContentsMargins(12, 8, 12, 8)

        self.tabla = QTableWidget(0, len(COLUMNAS))
        self.tabla.setObjectName("tabla")
        self.tabla.setHorizontalHeaderLabels(COLUMNAS)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.verticalHeader().setDefaultSectionSize(56)
        self.tabla.setShowGrid(False)
        self.tabla.setSelectionMode(QAbstractItemView.NoSelection)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.setFocusPolicy(Qt.NoFocus)
        self.tabla.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.tabla.horizontalHeader().setHighlightSections(False)
        encabezado = self.tabla.horizontalHeader()
        encabezado.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        encabezado.setSectionResizeMode(0, QHeaderView.Stretch)
        for columna, ancho in ((1, 140), (2, 105), (3, 175), (4, 95), (5, 105)):
            encabezado.setSectionResizeMode(columna, QHeaderView.Fixed)
            self.tabla.setColumnWidth(columna, ancho)

        self.lbl_vacio = QLabel("No hay miembros que coincidan con la búsqueda.")
        self.lbl_vacio.setObjectName("vacio")
        self.lbl_vacio.setAlignment(Qt.AlignCenter)

        # Se muestra la tabla o, si no hay resultados, el mensaje
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
        """Vuelve a pedir los datos y redibuja tarjetas y tabla."""
        resumen = controlador.cargar_resumen(self._ministerio_fijo)
        for clave, lbl in self._numeros.items():
            lbl.setText(str(resumen[clave]))

        datos = controlador.cargar_tabla(self._estado, self._ministerio, self._texto, self._pagina, self._solo_nuevos)
        self._pagina = datos["pagina"]
        self._llenar_tabla(datos["filas"])

        if datos["total"]:
            self.lbl_cuenta.setText(f'Mostrando {datos["desde"]}–{datos["hasta"]} de {datos["total"]} miembros')
        else:
            self.lbl_cuenta.setText("Sin resultados")
        self.lbl_pagina.setText(f'Página {datos["pagina"]} de {datos["paginas"]}')
        self.btn_anterior.setEnabled(datos["pagina"] > 1)
        self.btn_siguiente.setEnabled(datos["pagina"] < datos["paginas"])
        self._pila.setCurrentIndex(0 if datos["filas"] else 1)

    def _limpiar_tabla(self):
        """Quita las celdas anteriores (se ocultan al instante para que no se superpongan)."""
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
        for i, fila in enumerate(filas):
            self.tabla.setCellWidget(i, 0, self._celda_nombre(fila))
            self.tabla.setCellWidget(i, 1, self._celda_texto(fila["ministerios"]))
            self.tabla.setCellWidget(i, 2, self._celda_texto(fila["telefono"]))
            self.tabla.setCellWidget(i, 3, self._celda_asistencia(fila))
            self.tabla.setCellWidget(i, 4, self._celda_estado(fila))
            self.tabla.setCellWidget(i, 5, self._celda_acciones(fila))

    # ---------- celdas ----------
    def _contenedor(self, direccion=QHBoxLayout):
        widget = QWidget()
        lay = direccion(widget)
        lay.setContentsMargins(8, 0, 6, 0)
        return widget, lay

    def _celda_nombre(self, fila):
        widget, lay = self._contenedor()
        lay.setSpacing(10)
        avatar = QLabel(fila["iniciales"])
        avatar.setObjectName("avatar_miembro" if fila["activo"] else "avatar_miembro_inactivo")
        avatar.setFixedSize(32, 32)
        avatar.setAlignment(Qt.AlignCenter)
        nombre = QLabel(fila["nombre"])
        nombre.setObjectName("texto_tabla")
        lay.addWidget(avatar)
        lay.addWidget(nombre, 1)
        return widget

    def _celda_texto(self, texto):
        widget, lay = self._contenedor()
        lbl = QLabel(texto)
        lbl.setObjectName("texto_tabla")
        lay.addWidget(lbl)
        return widget

    def _celda_asistencia(self, fila):
        widget, lay = self._contenedor(QVBoxLayout)
        lay.setSpacing(0)
        lay.setAlignment(Qt.AlignVCenter)
        lbl = QLabel(fila["ultima"])
        lbl.setObjectName("texto_tabla")
        lay.addWidget(lbl)
        if fila["aviso"]:
            aviso = QLabel("Cerca de quedar inactivo")
            aviso.setObjectName("aviso_asistencia")
            lay.addWidget(aviso)
        return widget

    def _celda_estado(self, fila):
        widget, lay = self._contenedor()
        chip = QLabel("Activo" if fila["activo"] else "Inactivo")
        chip.setObjectName("chip_activo" if fila["activo"] else "chip_inactivo")
        lay.addWidget(chip, alignment=Qt.AlignVCenter)
        lay.addStretch()
        return widget

    def _celda_acciones(self, fila):
        widget, lay = self._contenedor()
        lay.setSpacing(2)
        botones = [
            ("ojo", VERDE_OSCURO, "Ver detalle", lambda: self._ver(fila["id"])),
            ("lapiz", VERDE_OSCURO, "Editar", lambda: self._editar(fila["id"])),
        ]
        if self._solo_lectura:
            botones = botones[:1]                    # solo "Ver detalle"
        elif fila["activo"]:
            botones.append(("encender", ROJO, "Desactivar", lambda: self._cambiar_estado(fila)))
        else:
            botones.append(("encender", VERDE, "Reactivar", lambda: self._cambiar_estado(fila)))
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
    def _elegir_estado(self, estado):
        """estado: None (todos), 1 (activos), 0 (inactivos) o "nuevos" (ingresaron este mes)."""
        self._solo_nuevos = estado == "nuevos"
        self._estado = None if self._solo_nuevos else estado
        self._pildoras[estado].setChecked(True)
        self._pagina = 1
        self.refrescar()

    def _cambio_ministerio(self):
        self._ministerio = self.cmb_ministerio.currentData()
        self._pagina = 1
        self.refrescar()

    def _aplicar_busqueda(self):
        self._texto = self.txt_buscar.text().strip()
        self._pagina = 1
        self.refrescar()

    def _mover_pagina(self, delta):
        self._pagina += delta
        self.refrescar()

    def _informe(self):
        """Genera el Informe general de miembros en Word, con el formato de la institución."""
        DialogoInforme(self, "miembros").exec()

    def _nuevo(self):
        if DialogoMiembro(self, ministerio_fijo=self._ministerio_fijo).exec():
            self.refrescar()

    def _ver(self, id_miembro):
        dialogo = DialogoDetalle(self, id_miembro, self._solo_lectura)
        dialogo.exec()
        if dialogo.accion == "editar":
            self._editar(id_miembro)
        else:
            self.refrescar()

    def _editar(self, id_miembro):
        DialogoMiembro(self, id_miembro, self._ministerio_fijo).exec()
        self.refrescar()

    def _cambiar_estado(self, fila):
        """Desactiva o reactiva directamente (se puede deshacer con el mismo botón)."""
        controlador.cambiar_estado(fila["id"], not fila["activo"])
        self.refrescar()
