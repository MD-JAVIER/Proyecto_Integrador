"""
estilos_miembros.py
-------------------
Estilos propios del área de Miembros (tabla, filtros y ventanas).
Reutiliza los colores del dashboard para que todo se vea como una sola aplicación.
"""
from modulos.dashboard.estilos_dashboard import (
    VERDE, VERDE_OSCURO, VERDE_CLARO, FONDO_HOVER, BLANCO, NEGRO, TEXTO_SUAVE, FUENTE_SERIF
)

VERDE_SUAVE = "#DDF1E6"   # fondo de etiquetas y avatares
GRIS_SUAVE = "#EEEEEE"
AVISO = "#9A6A00"
ROJO = "#C62828"

ESTILO_MIEMBROS = f"""
    QLabel#subtitulo_pagina {{
        color: {TEXTO_SUAVE};
        font-size: 13px;
    }}

    /* ---------- buscador y filtros ---------- */
    QLineEdit#buscador {{
        background-color: {BLANCO};
        color: {NEGRO};
        border: 1px solid {VERDE};
        border-radius: 17px;
        padding: 8px 16px;
        font-size: 13px;
    }}
    QLineEdit#buscador:focus {{
        border: 2px solid {VERDE_OSCURO};
    }}
    QPushButton#pildora {{
        background-color: {BLANCO};
        color: {VERDE_OSCURO};
        border: 1px solid {VERDE};
        border-radius: 15px;
        padding: 6px 18px;
        font-size: 13px;
    }}
    QPushButton#pildora:hover {{
        background-color: {FONDO_HOVER};
    }}
    QPushButton#pildora:checked {{
        background-color: {VERDE};
        color: {BLANCO};
    }}
    QComboBox#filtro {{
        background-color: {BLANCO};
        color: {NEGRO};
        border: 1px solid {VERDE};
        border-radius: 15px;
        padding: 6px 14px;
        font-size: 13px;
        min-width: 160px;
    }}
    QComboBox#filtro QAbstractItemView {{
        background-color: {BLANCO};
        color: {NEGRO};
        selection-background-color: {VERDE_SUAVE};
        selection-color: {NEGRO};
    }}

    /* ---------- tabla ---------- */
    QTableWidget#tabla {{
        background-color: {BLANCO};
        border: none;
        outline: 0;
    }}
    QHeaderView::section {{
        background-color: {BLANCO};
        color: {TEXTO_SUAVE};
        border: none;
        border-bottom: 1px solid {VERDE_CLARO};
        padding: 10px 8px;
        font-size: 12px;
        text-align: left;
    }}
    QLabel#texto_tabla {{
        color: {NEGRO};
        font-size: 13px;
    }}
    QLabel#avatar_miembro {{
        background-color: {VERDE_SUAVE};
        color: {VERDE_OSCURO};
        border-radius: 16px;
        font-size: 12px;
        font-weight: bold;
    }}
    QLabel#avatar_miembro_inactivo {{
        background-color: {GRIS_SUAVE};
        color: #666666;
        border-radius: 16px;
        font-size: 12px;
        font-weight: bold;
    }}
    QLabel#chip_activo {{
        background-color: {VERDE_SUAVE};
        color: {VERDE_OSCURO};
        border-radius: 9px;
        padding: 3px 12px;
        font-size: 12px;
    }}
    QLabel#chip_inactivo {{
        background-color: {GRIS_SUAVE};
        color: #555555;
        border-radius: 9px;
        padding: 3px 12px;
        font-size: 12px;
    }}
    QLabel#aviso_asistencia {{
        color: {AVISO};
        font-size: 11px;
    }}
    QLabel#vacio {{
        color: {TEXTO_SUAVE};
        font-size: 14px;
    }}
    QPushButton#boton_icono {{
        background-color: transparent;
        border: none;
        border-radius: 15px;
    }}
    QPushButton#boton_icono:hover {{
        background-color: {FONDO_HOVER};
    }}
    QLabel#pie_tabla {{
        color: {TEXTO_SUAVE};
        font-size: 12px;
    }}
    QPushButton#boton_pagina {{
        background-color: {BLANCO};
        color: {VERDE_OSCURO};
        border: 1px solid {VERDE};
        border-radius: 14px;
        font-size: 14px;
    }}
    QPushButton#boton_pagina:hover {{
        background-color: {FONDO_HOVER};
    }}
    QPushButton#boton_pagina:disabled {{
        color: #BBBBBB;
        border: 1px solid #DDDDDD;
    }}

    /* ---------- ventanas (formulario y detalle) ---------- */
    QDialog {{
        background-color: {BLANCO};
    }}
    QLabel#titulo_dialogo {{
        color: {VERDE_OSCURO};
        font-family: {FUENTE_SERIF};
        font-size: 24px;
    }}
    QLabel#etiqueta_form {{
        color: {TEXTO_SUAVE};
        font-size: 12px;
    }}
    QDialog QLineEdit, QDateEdit {{
        background-color: {BLANCO};
        color: {NEGRO};
        border: 1px solid {VERDE};
        border-radius: 8px;
        padding: 7px 10px;
        font-size: 13px;
    }}
    QDialog QLineEdit:focus, QDateEdit:focus {{
        border: 2px solid {VERDE_OSCURO};
    }}
    QCheckBox {{
        color: {NEGRO};
        font-size: 13px;
        spacing: 8px;
    }}
    QLabel#error_form {{
        color: {ROJO};
        font-size: 12px;
    }}
    QLabel#dato_etiqueta {{
        color: {TEXTO_SUAVE};
        font-size: 12px;
    }}
    QLabel#dato_valor {{
        color: {NEGRO};
        font-size: 14px;
    }}
    QLabel#avatar_grande {{
        background-color: {VERDE_SUAVE};
        color: {VERDE_OSCURO};
        border-radius: 32px;
        font-size: 22px;
        font-weight: bold;
    }}
    QLabel#avatar_grande_inactivo {{
        background-color: {GRIS_SUAVE};
        color: #666666;
        border-radius: 32px;
        font-size: 22px;
        font-weight: bold;
    }}
    QPushButton#boton_texto {{
        background-color: transparent;
        color: {TEXTO_SUAVE};
        border: none;
        font-size: 13px;
        padding: 8px 14px;
    }}
    QPushButton#boton_texto:hover {{
        color: {NEGRO};
    }}
"""
