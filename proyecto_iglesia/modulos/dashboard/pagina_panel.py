"""
pagina_panel.py
---------------
Contenido del área "Panel": encabezado, tarjetas de resumen, gráficos,
líderes y actividades. Solo dibuja; los datos los pide a controlador_dashboard.

Cada tarjeta es un acceso directo: al hacerle clic emite `ir_a("area")`
y la ventana principal cambia de página.
"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)

from modulos.comunes.logo import cargar_logo
from modulos.dashboard import controlador_dashboard as controlador
from modulos.dashboard.componentes import TarjetaClicable, GraficoPildoras
from modulos.dashboard.estilos_dashboard import VERDE
from modulos.informes.dialogo_informe import DialogoInforme


def _vaciar(layout):
    """Quita todos los elementos de un layout (para volver a llenarlo con datos nuevos)."""
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.setParent(None)            # desaparece de inmediato
            widget.deleteLater()
        elif item.layout():
            _vaciar(item.layout())


class PaginaPanel(QWidget):
    ir_a = Signal(str)   # "miembros", "finanzas", "actividades" o "lideres"

    def __init__(self):
        super().__init__()
        self.setObjectName("pagina")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(14)
        lay.addWidget(self._crear_encabezado())
        lay.addLayout(self._crear_tarjetas_resumen())
        lay.addLayout(self._crear_zona_inferior(), 1)

        self.actualizar()

    # ======================= construcción =======================
    def _crear_encabezado(self):
        marco = QFrame()
        marco.setObjectName("encabezado")
        marco.setMinimumHeight(92)

        titulo = QLabel("Panel")
        titulo.setObjectName("titulo_panel")
        subtitulo = QLabel("Todo lo puedo en Cristo que me fortalece")
        subtitulo.setObjectName("subtitulo_panel")
        textos = QVBoxLayout()
        textos.setSpacing(0)
        textos.addWidget(titulo)
        textos.addWidget(subtitulo)

        btn_f = QPushButton("Informe de ofrendas")
        btn_f.setObjectName("boton_lleno")
        btn_f.clicked.connect(lambda: DialogoInforme(self, "ofrendas").exec())
        btn_m = QPushButton("Informe de miembros")
        btn_m.setObjectName("boton_borde")
        btn_m.clicked.connect(lambda: DialogoInforme(self, "miembros").exec())
        for boton in (btn_f, btn_m):
            boton.setCursor(Qt.PointingHandCursor)

        lay = QHBoxLayout(marco)
        lay.setContentsMargins(24, 12, 24, 12)
        lay.addLayout(textos, 1)
        lay.addWidget(btn_f)
        lay.addWidget(btn_m)
        return marco

    def _tarjeta_numero(self, titulo, destacada=False):
        """Crea una tarjeta con título y número. Devuelve (tarjeta, etiqueta_del_número)."""
        tarjeta = TarjetaClicable()
        tarjeta.setObjectName("tarjeta_destacada" if destacada else "tarjeta")
        sufijo = "_blanco" if destacada else ""

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setObjectName("titulo_tarjeta" + sufijo)
        lbl_numero = QLabel("0")
        lbl_numero.setObjectName("numero_tarjeta" + sufijo)

        lay = QVBoxLayout(tarjeta)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.addWidget(lbl_titulo)
        lay.addWidget(lbl_numero)

        tarjeta.clicked.connect(lambda: self.ir_a.emit("miembros"))   # acceso directo
        return tarjeta, lbl_numero

    def _crear_tarjetas_resumen(self):
        fila = QHBoxLayout()
        fila.setSpacing(14)
        t_total, self.lbl_total = self._tarjeta_numero("Miembros totales", destacada=True)
        t_jov, self.lbl_jovenes = self._tarjeta_numero("Total Jóvenes")
        t_dam, self.lbl_damas = self._tarjeta_numero("Total Damas")
        t_cab, self.lbl_caballeros = self._tarjeta_numero("Total Caballeros")
        for tarjeta in (t_total, t_jov, t_dam, t_cab):
            fila.addWidget(tarjeta, 1)
        return fila

    def _tarjeta_con_titulo(self, titulo, destino):
        """Tarjeta base: título arriba y acceso directo a un área. Devuelve (tarjeta, layout)."""
        tarjeta = TarjetaClicable()
        tarjeta.setObjectName("tarjeta")
        tarjeta.clicked.connect(lambda: self.ir_a.emit(destino))

        lay = QVBoxLayout(tarjeta)
        lay.setContentsMargins(16, 12, 16, 12)
        lbl = QLabel(titulo)
        lbl.setObjectName("titulo_seccion")
        lay.addWidget(lbl)
        return tarjeta, lay

    def _crear_zona_inferior(self):
        zona = QHBoxLayout()
        zona.setSpacing(14)

        izquierda = QVBoxLayout()
        izquierda.setSpacing(14)
        izquierda.addWidget(self._crear_tarjeta_ofrendas(), 3)

        abajo = QHBoxLayout()
        abajo.setSpacing(14)
        abajo.addWidget(self._crear_tarjeta_lideres(), 1)
        abajo.addWidget(self._crear_tarjeta_estado(), 1)
        izquierda.addLayout(abajo, 2)

        zona.addLayout(izquierda, 2)
        zona.addWidget(self._crear_tarjeta_actividades(), 1)
        return zona

    def _crear_tarjeta_ofrendas(self):
        tarjeta, lay = self._tarjeta_con_titulo("Ofrendas mensuales", "finanzas")
        self.grafico_ofrendas = GraficoPildoras(ancho_barra=34)
        lay.addWidget(self.grafico_ofrendas, 1)
        return tarjeta

    def _crear_tarjeta_lideres(self):
        tarjeta, lay = self._tarjeta_con_titulo("Líderes", "lideres")
        self.lay_lideres = QVBoxLayout()
        self.lay_lideres.setSpacing(8)
        lay.addLayout(self.lay_lideres)
        lay.addStretch()
        return tarjeta

    def _crear_tarjeta_estado(self):
        tarjeta, lay = self._tarjeta_con_titulo("P y A", "miembros")
        fila = QHBoxLayout()
        self.grafico_estado = GraficoPildoras(ancho_barra=36)
        fila.addWidget(self.grafico_estado, 1)

        leyenda = QVBoxLayout()
        leyenda.addStretch()
        for nombre_punto, texto in (("punto_activo", "Activo"), ("punto_inactivo", "Inactivo")):
            punto = QLabel("●")
            punto.setObjectName(nombre_punto)
            lbl = QLabel(texto)
            lbl.setObjectName("leyenda")
            linea = QHBoxLayout()
            linea.setSpacing(4)
            linea.addWidget(punto)
            linea.addWidget(lbl)
            leyenda.addLayout(linea)
        fila.addLayout(leyenda)

        lay.addLayout(fila, 1)
        return tarjeta

    def _crear_tarjeta_actividades(self):
        tarjeta = TarjetaClicable()
        tarjeta.setObjectName("tarjeta")
        tarjeta.clicked.connect(lambda: self.ir_a.emit("actividades"))

        lay = QVBoxLayout(tarjeta)
        lay.setContentsMargins(16, 12, 16, 12)

        titulo = QLabel("Actividades")
        titulo.setObjectName("titulo_seccion")
        nuevo = QPushButton("Nuevo")
        nuevo.setObjectName("boton_pequeno")
        nuevo.setCursor(Qt.PointingHandCursor)
        nuevo.clicked.connect(lambda: self.ir_a.emit("actividades"))
        cabecera = QHBoxLayout()
        cabecera.addWidget(titulo)
        cabecera.addStretch()
        cabecera.addWidget(nuevo)
        lay.addLayout(cabecera)

        self.lay_actividades = QVBoxLayout()
        self.lay_actividades.setSpacing(10)
        lay.addSpacing(6)
        lay.addLayout(self.lay_actividades)
        lay.addStretch()
        return tarjeta

    # ======================= datos =======================
    def actualizar(self):
        """Pide los datos al controlador y los pone en pantalla."""
        resumen = controlador.datos_resumen()
        self.lbl_total.setText(str(resumen["total"]))
        self.lbl_jovenes.setText(str(resumen["jovenes"]))
        self.lbl_damas.setText(str(resumen["damas"]))
        self.lbl_caballeros.setText(str(resumen["caballeros"]))

        self.grafico_ofrendas.establecer_datos(controlador.datos_ofrendas())
        self.grafico_estado.establecer_datos(controlador.datos_estado_miembros())

        _vaciar(self.lay_lideres)
        for cargo, _nombre in controlador.datos_lideres():
            avatar = QLabel()
            avatar.setObjectName("avatar_mini")
            avatar.setFixedSize(22, 22)
            lbl = QLabel(cargo)
            lbl.setObjectName("texto_lista")
            fila = QHBoxLayout()
            fila.addWidget(lbl, 1)
            fila.addWidget(avatar)
            self.lay_lideres.addLayout(fila)

        _vaciar(self.lay_actividades)
        icono = cargar_logo(VERDE, 34)
        for nombre, fecha in controlador.datos_actividades():
            lbl_icono = QLabel()
            lbl_icono.setPixmap(icono)
            lbl_nombre = QLabel(nombre)
            lbl_nombre.setObjectName("texto_lista")
            lbl_fecha = QLabel(fecha)
            lbl_fecha.setObjectName("fecha_actividad")
            textos = QVBoxLayout()
            textos.setSpacing(0)
            textos.addWidget(lbl_nombre)
            textos.addWidget(lbl_fecha)
            fila = QHBoxLayout()
            fila.setSpacing(12)
            fila.addWidget(lbl_icono)
            fila.addLayout(textos, 1)
            self.lay_actividades.addLayout(fila)
