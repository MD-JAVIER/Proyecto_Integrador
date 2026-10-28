"""
estilos_actividades.py
----------------------
Estilos propios del área de Actividades (cultos de la semana, etiquetas y barras de desplazamiento).
Reutiliza los colores del dashboard.
"""
from modulos.dashboard.estilos_dashboard import (
    VERDE, VERDE_OSCURO, BLANCO, NEGRO, TEXTO_SUAVE, FUENTE_SERIF
)

ESTILO_ACTIVIDADES = f"""
    /* ---------- página con desplazamiento ---------- */
    QScrollArea {{
        background: transparent;
        border: none;
    }}
    QWidget#contenido_scroll {{
        background-color: {BLANCO};
    }}
    QScrollBar:vertical {{
        background: transparent;
        width: 10px;
        margin: 2px;
    }}
    QScrollBar::handle:vertical {{
        background: #C9D8CF;
        border-radius: 4px;
        min-height: 30px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    /* ---------- cultos de la semana ---------- */
    QLabel#dia_culto {{
        color: {VERDE_OSCURO};
        font-family: {FUENTE_SERIF};
        font-size: 20px;
    }}
    QLabel#dia_culto_blanco {{
        color: {BLANCO};
        font-family: {FUENTE_SERIF};
        font-size: 20px;
    }}
    QLabel#fecha_culto {{
        color: {NEGRO};
        font-size: 13px;
    }}
    QLabel#fecha_culto_blanco {{
        color: {BLANCO};
        font-size: 13px;
    }}
    QLabel#detalle_culto {{
        color: {TEXTO_SUAVE};
        font-size: 12px;
    }}
    QLabel#detalle_culto_blanco {{
        color: #D5EDE0;
        font-size: 12px;
    }}

    /* ---------- etiquetas de situación ---------- */
    QLabel#chip_programada {{
        background-color: #DDF1E6;
        color: {VERDE_OSCURO};
        border-radius: 9px;
        padding: 3px 12px;
        font-size: 12px;
    }}
    QLabel#chip_realizada {{
        background-color: #EEEEEE;
        color: #555555;
        border-radius: 9px;
        padding: 3px 12px;
        font-size: 12px;
    }}
    QLabel#chip_cancelada {{
        background-color: #FBE3E1;
        color: #9C2A22;
        border-radius: 9px;
        padding: 3px 12px;
        font-size: 12px;
    }}
    QLabel#chip_sin_crear {{
        background-color: #FFF1D6;
        color: #9A6A00;
        border-radius: 9px;
        padding: 3px 12px;
        font-size: 12px;
    }}

    /* ---------- formulario ---------- */
    QTimeEdit {{
        background-color: {BLANCO};
        color: {NEGRO};
        border: 1px solid {VERDE};
        border-radius: 8px;
        padding: 7px 10px;
        font-size: 13px;
    }}
    QTimeEdit:focus {{
        border: 2px solid {VERDE_OSCURO};
    }}
"""
