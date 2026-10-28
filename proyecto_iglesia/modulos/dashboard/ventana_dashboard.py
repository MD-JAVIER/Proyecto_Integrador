"""
ventana_dashboard.py
--------------------
Ventana principal del Administrador (pastor). Une las piezas:
menú lateral + barra superior + páginas intercambiables (QStackedWidget).

Navegación: el menú y las tarjetas emiten "quiero ir a X"; esta ventana
es la única que cambia de página.
"""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget

from modulos.dashboard import controlador_dashboard as controlador
from modulos.dashboard.barra_superior import BarraSuperior
from modulos.dashboard.estilos_dashboard import ESTILO_DASHBOARD
from modulos.actividades.pagina_actividades import PaginaActividades
from modulos.comunes.estilos import estilo_aplicacion
from modulos.finanzas.pagina_finanzas import PaginaFinanzas
from modulos.lideres.pagina_lideres import PaginaLideres
from modulos.miembros import controlador_miembros
from modulos.miembros.pagina_miembros import PaginaMiembros
from modulos.dashboard.menu_lateral import MenuLateral
from modulos.dashboard.pagina_panel import PaginaPanel
from modulos.dashboard.pagina_pendiente import PaginaPendiente


class VentanaDashboard(QWidget):
    sesion_cerrada = Signal()

    def __init__(self, correo, rol):
        super().__init__()
        self.setObjectName("raiz")
        self.setWindowTitle("Ekklesia")
        self.resize(1180, 760)
        self.setMinimumSize(1000, 640)
        self.setStyleSheet(estilo_aplicacion())

        nombre, correo = controlador.obtener_nombre_y_correo(correo)
        controlador_miembros.revisar_inactividad()      # regla de los 15 días sin asistir

        # Páginas: cada clave del menú tiene su página
        self.paginas = QStackedWidget()
        self._paginas = {
            "panel": PaginaPanel(),
            "miembros": PaginaMiembros(),
            "finanzas": PaginaFinanzas(correo),
            "actividades": PaginaActividades(),
            "lideres": PaginaLideres(),
        }
        for pagina in self._paginas.values():
            self.paginas.addWidget(pagina)

        self.menu = MenuLateral()
        self.barra = BarraSuperior(nombre, correo)

        # Lado derecho: barra arriba y páginas abajo
        derecha = QVBoxLayout()
        derecha.setSpacing(14)
        derecha.addWidget(self.barra)
        derecha.addWidget(self.paginas, 1)

        principal = QHBoxLayout(self)
        principal.setContentsMargins(14, 14, 14, 14)
        principal.setSpacing(14)
        principal.addWidget(self.menu)
        principal.addLayout(derecha, 1)

        # Conexiones de navegación
        self.menu.pagina_seleccionada.connect(self.ir_a)
        self.menu.cerrar_sesion.connect(self.sesion_cerrada.emit)
        self._paginas["panel"].ir_a.connect(self.ir_a)

        self.ir_a("panel")

    def ir_a(self, clave):
        """Muestra la página indicada y marca su botón en el menú."""
        self.paginas.setCurrentWidget(self._paginas[clave])
        self.menu.marcar(clave)
        if clave in ("panel", "miembros"):
            controlador_miembros.revisar_inactividad()    # mantiene al día quién está activo
        if clave == "panel":
            self._paginas["panel"].actualizar()   # refresca los datos al volver
        elif clave == "miembros":
            self._paginas["miembros"].refrescar()
        elif clave == "finanzas":
            self._paginas["finanzas"].refrescar()
        elif clave == "actividades":
            self._paginas["actividades"].refrescar()
        elif clave == "lideres":
            self._paginas["lideres"].refrescar()
