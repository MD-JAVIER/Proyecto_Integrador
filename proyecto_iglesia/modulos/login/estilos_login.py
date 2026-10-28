"""
estilos_login.py
----------------
Todos los colores, fuentes y el diseño visual del login, separados de la ventana.
Para cambiar el diseño solo se edita este archivo.
"""

VERDE = "#0E623D"          # botón "Ingresar"
VERDE_OSCURO = "#0A4A2E"   # botón al pasar el mouse
VERDE_BORDE = "#4A896D"    # borde de los campos
BLANCO = "#FFFFFF"
NEGRO = "#000000"
GRIS_TEXTO = "#444444"
ROJO_ERROR = "#C62828"

# Fuente con serifa (como el diseño). Si no está instalada, usa la siguiente.
FUENTE_SERIF = "'Playfair Display', 'Georgia', 'Times New Roman', serif"

ESTILO_LOGIN = f"""
    QWidget#panel_derecho {{
        background-color: {BLANCO};
    }}

    QLabel#titulo {{
        color: {NEGRO};
        font-family: {FUENTE_SERIF};
        font-size: 30px;
    }}

    QLabel#subtitulo {{
        color: {GRIS_TEXTO};
        font-size: 12px;
    }}

    QLabel#etiqueta {{
        color: {GRIS_TEXTO};
        font-size: 11px;
    }}

    QLabel#error {{
        color: {ROJO_ERROR};
        font-size: 12px;
    }}

    QLineEdit {{
        background-color: {BLANCO};
        color: {NEGRO};
        border: 1px solid {VERDE_BORDE};
        border-radius: 4px;
        padding: 9px;
        font-size: 13px;
    }}

    QLineEdit:focus {{
        border: 2px solid {VERDE};
    }}

    QPushButton#boton_ingresar {{
        background-color: {VERDE};
        color: {BLANCO};
        border: none;
        border-radius: 14px;
        padding: 9px;
        font-size: 13px;
        font-weight: bold;
    }}

    QPushButton#boton_ingresar:hover {{
        background-color: {VERDE_OSCURO};
    }}
"""

# Panel izquierdo (foto con texto encima)
ESTILO_PANEL_IMAGEN = f"""
    QLabel#logo {{
        color: {BLANCO};
        font-family: {FUENTE_SERIF};
        font-size: 26px;
        background: transparent;
    }}

    QLabel#versiculo {{
        color: {BLANCO};
        font-family: {FUENTE_SERIF};
        font-size: 24px;
        background: transparent;
    }}

    QLabel#cita {{
        color: {BLANCO};
        font-family: {FUENTE_SERIF};
        font-size: 15px;
        background: transparent;
    }}
"""
