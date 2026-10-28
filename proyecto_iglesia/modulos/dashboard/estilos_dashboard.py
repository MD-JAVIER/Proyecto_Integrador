"""
estilos_dashboard.py
--------------------
Colores, fuentes y diseño visual del dashboard (tomados del diseño entregado).
Para cambiar el aspecto solo se edita este archivo.
"""

VERDE = "#227D53"          # tarjeta destacada, botón lleno, bordes
VERDE_OSCURO = "#0E623D"   # títulos y textos
VERDE_CLARO = "#5FBD92"    # barras destacadas
GRIS = "#D9D9D9"           # barras normales
FONDO_HOVER = "#EAF5EF"    # fondo al pasar el mouse
BLANCO = "#FFFFFF"
NEGRO = "#000000"
TEXTO_SUAVE = "#555555"

FUENTE_SERIF = "'Playfair Display', 'Georgia', 'Times New Roman', serif"

ESTILO_DASHBOARD = f"""
    QWidget#raiz, QWidget#contenido, QWidget#pagina {{
        background-color: {BLANCO};
    }}

    /* ---------- menú lateral ---------- */
    QFrame#menu_lateral {{
        background-color: {BLANCO};
        border: 2px solid {VERDE};
        border-radius: 8px;
    }}
    QLabel#nombre_app {{
        color: {VERDE_OSCURO};
        font-family: {FUENTE_SERIF};
        font-size: 26px;
    }}
    QLabel#etiqueta_menu {{
        color: {NEGRO};
        font-size: 12px;
    }}
    QPushButton#boton_menu {{
        background-color: transparent;
        border: none;
        border-radius: 8px;
        color: {VERDE_OSCURO};
        font-family: {FUENTE_SERIF};
        font-size: 22px;
        text-align: left;
        padding: 6px 12px;
    }}
    QPushButton#boton_menu:hover {{
        background-color: {FONDO_HOVER};
    }}
    QPushButton#boton_menu:checked {{
        background-color: {VERDE};
        color: {BLANCO};
    }}

    /* ---------- barra superior ---------- */
    QFrame#barra_superior, QFrame#encabezado, QFrame#tarjeta {{
        background-color: {BLANCO};
        border: 1px solid {VERDE};
        border-radius: 16px;
    }}
    QFrame#tarjeta:hover {{
        background-color: {FONDO_HOVER};
    }}
    QFrame#tarjeta_destacada {{
        background-color: {VERDE};
        border-radius: 18px;
    }}
    QFrame#tarjeta_destacada:hover {{
        background-color: {VERDE_OSCURO};
    }}
    QLabel#avatar {{
        background-color: #111111;
        border-radius: 17px;
    }}
    QLabel#avatar_mini {{
        background-color: #111111;
        border-radius: 11px;
    }}
    QLabel#usuario_nombre {{
        color: {NEGRO};
        font-family: {FUENTE_SERIF};
        font-size: 15px;
    }}
    QLabel#usuario_correo {{
        color: {TEXTO_SUAVE};
        font-size: 11px;
    }}

    /* ---------- encabezado del panel ---------- */
    QLabel#titulo_panel {{
        color: {VERDE_OSCURO};
        font-family: {FUENTE_SERIF};
        font-size: 32px;
    }}
    QLabel#subtitulo_panel {{
        color: {NEGRO};
        font-family: {FUENTE_SERIF};
        font-size: 13px;
    }}
    QPushButton#boton_lleno {{
        background-color: {VERDE};
        color: {BLANCO};
        border: none;
        border-radius: 13px;
        padding: 5px 20px;
        font-family: {FUENTE_SERIF};
        font-size: 14px;
    }}
    QPushButton#boton_lleno:hover {{
        background-color: {VERDE_OSCURO};
    }}
    QPushButton#boton_borde {{
        background-color: {BLANCO};
        color: {VERDE_OSCURO};
        border: 1px solid {VERDE_OSCURO};
        border-radius: 13px;
        padding: 5px 20px;
        font-family: {FUENTE_SERIF};
        font-size: 14px;
    }}
    QPushButton#boton_borde:hover {{
        background-color: {FONDO_HOVER};
    }}
    QPushButton#boton_pequeno {{
        background-color: {BLANCO};
        color: {VERDE_OSCURO};
        border: 1px solid {VERDE_OSCURO};
        border-radius: 9px;
        padding: 2px 12px;
        font-size: 10px;
    }}
    QPushButton#boton_pequeno:hover {{
        background-color: {FONDO_HOVER};
    }}

    /* ---------- tarjetas de resumen ---------- */
    QLabel#titulo_tarjeta {{
        color: {NEGRO};
        font-size: 13px;
    }}
    QLabel#numero_tarjeta {{
        color: {NEGRO};
        font-size: 22px;
        font-weight: bold;
    }}
    QLabel#titulo_tarjeta_blanco {{
        color: {BLANCO};
        font-size: 13px;
    }}
    QLabel#numero_tarjeta_blanco {{
        color: {BLANCO};
        font-size: 22px;
        font-weight: bold;
    }}

    /* ---------- tarjetas con gráficos y listas ---------- */
    QLabel#titulo_seccion {{
        color: {NEGRO};
        font-family: {FUENTE_SERIF};
        font-size: 15px;
    }}
    QLabel#texto_lista {{
        color: {NEGRO};
        font-family: {FUENTE_SERIF};
        font-size: 14px;
    }}
    QLabel#fecha_actividad {{
        color: {TEXTO_SUAVE};
        font-family: {FUENTE_SERIF};
        font-size: 10px;
    }}
    QLabel#leyenda {{
        color: {NEGRO};
        font-size: 10px;
    }}
    QLabel#punto_activo {{
        color: {VERDE_OSCURO};
        font-size: 12px;
    }}
    QLabel#punto_inactivo {{
        color: {VERDE_CLARO};
        font-size: 12px;
    }}

    /* ---------- páginas pendientes ---------- */
    QLabel#titulo_pagina {{
        color: {VERDE_OSCURO};
        font-family: {FUENTE_SERIF};
        font-size: 32px;
    }}
    QLabel#texto_pagina {{
        color: {TEXTO_SUAVE};
        font-size: 14px;
    }}
"""
