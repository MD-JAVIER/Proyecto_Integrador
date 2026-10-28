"""
estilos_lideres.py
------------------
Estilos propios del área de Líderes (tarjetas por ministerio y lista de líderes).
Reutiliza los colores del dashboard.
"""
from modulos.dashboard.estilos_dashboard import (
    VERDE, VERDE_OSCURO, BLANCO, NEGRO, TEXTO_SUAVE, FUENTE_SERIF
)

ESTILO_LIDERES = f"""
    QLabel#ministerio_titulo {{
        color: {VERDE_OSCURO};
        font-family: {FUENTE_SERIF};
        font-size: 22px;
    }}
    QLabel#lider_nombre {{
        color: {NEGRO};
        font-size: 14px;
    }}
    QLabel#lider_detalle {{
        color: {TEXTO_SUAVE};
        font-size: 12px;
    }}
    QLabel#sin_lider {{
        color: {TEXTO_SUAVE};
        font-size: 13px;
    }}
    QLabel#aviso_form {{
        color: {TEXTO_SUAVE};
        font-size: 12px;
    }}
    /* el campo de texto dentro de una lista editable no debe llevar un segundo borde */
    QDialog QComboBox QLineEdit {{
        border: none;
        padding: 0px;
        background: transparent;
    }}

    /* cuadros de mensaje: fondo blanco con texto negro (así se leen aunque Windows esté en modo oscuro) */
    QMessageBox {{
        background-color: {BLANCO};
    }}
    QMessageBox QLabel {{
        color: {NEGRO};
        font-size: 13px;
    }}
    QMessageBox QPushButton {{
        background-color: {VERDE};
        color: {BLANCO};
        border: none;
        border-radius: 12px;
        padding: 6px 18px;
        min-width: 90px;
    }}
    QMessageBox QPushButton:hover {{
        background-color: {VERDE_OSCURO};
    }}
"""
