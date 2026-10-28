"""
main.py
-------
Punto de arranque. Ejecutar con:  python main.py

Controla qué ventana se ve en cada momento:
login -> dashboard (si es Administrador) -> login otra vez al cerrar sesión.
"""
import sys
from PySide6.QtWidgets import QApplication

from modulos.login.vista_login import VistaLogin
from modulos.dashboard.ventana_dashboard import VentanaDashboard
from modulos.dashboard.ventana_lider import VentanaLider
from modulos.lideres import controlador_lideres
from modulos.principal.ventana_principal import VentanaPrincipal


class Aplicacion:
    def __init__(self):
        self.ventana = None   # guarda la ventana abierta para que Python no la borre

    def mostrar_login(self):
        login = VistaLogin()
        login.login_exitoso.connect(lambda correo, rol: self.abrir_principal(login, correo, rol))
        self.ventana = login
        login.show()

    def abrir_principal(self, login, correo, rol):
        if rol == "Administrador":
            ventana = VentanaDashboard(correo, rol)
            ventana.sesion_cerrada.connect(self.cerrar_sesion)
        elif rol == "Líder" and controlador_lideres.ministerio_por_correo(correo) is not None:
            # El líder entra directo a su gestión, filtrada por su ministerio
            ventana = VentanaLider(correo, controlador_lideres.ministerio_por_correo(correo))
            ventana.sesion_cerrada.connect(self.cerrar_sesion)
        else:
            ventana = VentanaPrincipal(correo, rol)       # provisional para cualquier otro caso
        self.ventana = ventana
        ventana.show()
        login.close()

    def cerrar_sesion(self):
        anterior = self.ventana
        self.mostrar_login()      # primero se abre el login...
        anterior.close()          # ...y luego se cierra el dashboard


def main():
    app = QApplication(sys.argv)
    aplicacion = Aplicacion()
    aplicacion.mostrar_login()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
