"""
ventana_lider.py
----------------
Ventana del LÍDER de un ministerio (Jóvenes, Damas o Caballeros).

No tiene dashboard con gráficos: entra directo a su gestión, con un menú corto:
    Asistencia   -> marca quién asistió a cada culto
    Mis miembros -> solo consulta (el pastor crea, edita y desactiva)
    Actividades  -> los cultos generales (solo ve) y las de su ministerio (gestiona)

Todo lo que ve está filtrado por SU ministerio.
"""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget

from modulos.actividades.pagina_actividades import PaginaActividades
from modulos.asistencia.pagina_asistencia import PaginaAsistencia
from modulos.comunes.estilos import estilo_aplicacion
from modulos.dashboard.barra_superior import BarraSuperior
from modulos.dashboard.menu_lateral import MenuLateral
from modulos.lideres import controlador_lideres
from modulos.miembros import controlador_miembros
from modulos.miembros.pagina_miembros import PaginaMiembros

OPCIONES_LIDER = [
    ("asistencia", "Asistencia"),
    ("miembros", "Mis miembros"),
    ("actividades", "Actividades"),
]


class VentanaLider(QWidget):
    sesion_cerrada = Signal()

    def __init__(self, correo, id_ministerio):
        super().__init__()
        self._id_ministerio = id_ministerio
        ministerio = controlador_lideres.nombre_ministerio(id_ministerio)
        nombre = controlador_lideres.nombre_por_correo(correo) or "Líder"

        self.setObjectName("raiz")
        self.setWindowTitle(f"Ekklesia – Líder de {ministerio}")
        self.resize(1180, 760)
        self.setMinimumSize(1000, 640)
        self.setStyleSheet(estilo_aplicacion())

        controlador_miembros.revisar_inactividad()       # regla de los 15 días sin asistir

        # Páginas: todas filtradas por el ministerio del líder
        self.paginas = QStackedWidget()
        self._paginas = {
            "asistencia": PaginaAsistencia(id_ministerio),
            "miembros": PaginaMiembros(ministerio_fijo=id_ministerio, solo_lectura=True),
            "actividades": PaginaActividades(id_ministerio),
        }
        for pagina in self._paginas.values():
            self.paginas.addWidget(pagina)

        self.menu = MenuLateral(OPCIONES_LIDER)
        self.barra = BarraSuperior(nombre, f"Líder de {ministerio} · {correo}")

        derecha = QVBoxLayout()
        derecha.setSpacing(14)
        derecha.addWidget(self.barra)
        derecha.addWidget(self.paginas, 1)

        principal = QHBoxLayout(self)
        principal.setContentsMargins(14, 14, 14, 14)
        principal.setSpacing(14)
        principal.addWidget(self.menu)
        principal.addLayout(derecha, 1)

        self.menu.pagina_seleccionada.connect(self.ir_a)
        self.menu.cerrar_sesion.connect(self.sesion_cerrada.emit)

        self.ir_a("asistencia")

    def ir_a(self, clave):
        """Muestra la página indicada, marca su botón y la actualiza."""
        controlador_miembros.revisar_inactividad()
        self.paginas.setCurrentWidget(self._paginas[clave])
        self.menu.marcar(clave)
        self._paginas[clave].refrescar()
