"""
vista_login.py
--------------
Solo el formulario: campos, botón y mensajes. Sin colores escritos aquí
(están en estilos_login.py) y sin lógica de datos (está en controlador_login.py).
"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QPushButton
)

from modulos.login.estilos_login import ESTILO_LOGIN
from modulos.login.panel_imagen import PanelImagen
from modulos.login import controlador_login


class VistaLogin(QWidget):
    # Se emite cuando el ingreso es correcto: (correo, rol)
    login_exitoso = Signal(str, str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ekklesia – Inicio de sesión")
        self.resize(1000, 620)
        self.setMinimumSize(760, 500)
        self.setStyleSheet(ESTILO_LOGIN)

        principal = QHBoxLayout(self)
        principal.setContentsMargins(0, 0, 0, 0)
        principal.setSpacing(0)

        principal.addWidget(PanelImagen(), 1)          # izquierda (1/3)
        principal.addWidget(self._crear_formulario(), 2)  # derecha (2/3)

    # ---------- construcción del formulario ----------
    def _crear_formulario(self):
        panel = QWidget()
        panel.setObjectName("panel_derecho")

        col = QVBoxLayout()
        col.setSpacing(6)

        titulo = QLabel("Bienvenido A Ekklesia")
        titulo.setObjectName("titulo")
        titulo.setAlignment(Qt.AlignCenter)

        subtitulo = QLabel("Gestiona miembros, ministerios, eventos y asistencia\n"
                           "de tu iglesia en un solo lugar.")
        subtitulo.setObjectName("subtitulo")
        subtitulo.setAlignment(Qt.AlignCenter)

        self.txt_correo = QLineEdit()
        self.txt_correo.setPlaceholderText("pastor@iglesia.org")

        self.txt_clave = QLineEdit()
        self.txt_clave.setPlaceholderText("Contraseña")
        self.txt_clave.setEchoMode(QLineEdit.Password)

        self.lbl_error = QLabel("")
        self.lbl_error.setObjectName("error")
        self.lbl_error.setAlignment(Qt.AlignCenter)
        self.lbl_error.setWordWrap(True)

        self.btn_ingresar = QPushButton("Ingresar")
        self.btn_ingresar.setObjectName("boton_ingresar")
        self.btn_ingresar.setCursor(Qt.PointingHandCursor)

        col.addWidget(titulo)
        col.addWidget(subtitulo)
        col.addSpacing(26)
        col.addWidget(self._etiqueta("Email"))
        col.addWidget(self.txt_correo)
        col.addSpacing(10)
        col.addWidget(self._etiqueta("Contraseña"))
        col.addWidget(self.txt_clave)
        col.addWidget(self.lbl_error)
        col.addSpacing(8)
        col.addWidget(self.btn_ingresar)

        # Contenedor de ancho limitado, centrado en el panel blanco
        contenedor = QWidget()
        contenedor.setMaximumWidth(400)
        contenedor.setLayout(col)

        exterior = QVBoxLayout(panel)
        exterior.setAlignment(Qt.AlignCenter)
        exterior.addWidget(contenedor)

        # Eventos
        self.btn_ingresar.clicked.connect(self._ingresar)
        self.txt_correo.returnPressed.connect(self._ingresar)
        self.txt_clave.returnPressed.connect(self._ingresar)
        return panel

    def _etiqueta(self, texto):
        lbl = QLabel(texto)
        lbl.setObjectName("etiqueta")
        return lbl

    # ---------- comportamiento ----------
    def _ingresar(self):
        ok, mensaje, rol = controlador_login.validar_login(
            self.txt_correo.text(),
            self.txt_clave.text(),
        )
        if ok:
            self.lbl_error.setText("")
            self.login_exitoso.emit(self.txt_correo.text().strip(), rol)
        else:
            self.lbl_error.setText(mensaje)
            self.txt_clave.clear()
            self.txt_clave.setFocus()
