"""
estilos_finanzas.py
-------------------
Estilos propios del área de Finanzas. Reutiliza los colores del dashboard
y los estilos de tabla y ventanas del área de Miembros.
"""
from modulos.dashboard.estilos_dashboard import (
    VERDE, VERDE_OSCURO, VERDE_CLARO, FONDO_HOVER, BLANCO, NEGRO, TEXTO_SUAVE
)

ESTILO_FINANZAS = f"""
    /* tarjeta que no cambia de color al pasar el mouse */
    QFrame#tarjeta_fija {{
        background-color: {BLANCO};
        border: 1px solid {VERDE};
        border-radius: 16px;
    }}
    QLabel#detalle_tarjeta {{
        color: {TEXTO_SUAVE};
        font-size: 12px;
    }}
    QLabel#detalle_tarjeta_blanco {{
        color: #D5EDE0;
        font-size: 12px;
    }}
    QLabel#chip_pendiente {{
        background-color: #FFF1D6;
        color: #9A6A00;
        border-radius: 9px;
        padding: 3px 12px;
        font-size: 12px;
    }}
    QPushButton#boton_lleno:disabled {{
        background-color: #BFD9CC;
        color: {BLANCO};
    }}
    QPushButton#boton_borde:disabled {{
        color: #AAAAAA;
        border: 1px solid #CCCCCC;
    }}
    QPushButton#boton_registrar {{
        background-color: {BLANCO};
        color: {VERDE_OSCURO};
        border: 1px solid {VERDE_OSCURO};
        border-radius: 11px;
        padding: 4px 14px;
        font-size: 12px;
    }}
    QPushButton#boton_registrar:hover {{
        background-color: {FONDO_HOVER};
    }}
    QComboBox#filtro_anio {{
        background-color: {BLANCO};
        color: {NEGRO};
        border: 1px solid {VERDE};
        border-radius: 15px;
        padding: 5px 14px;
        font-size: 13px;
        min-width: 70px;
    }}
    QComboBox#filtro_anio QAbstractItemView, QDialog QComboBox QAbstractItemView {{
        background-color: {BLANCO};
        color: {NEGRO};
        selection-background-color: #DDF1E6;
        selection-color: {NEGRO};
    }}
    QDialog QComboBox, QDoubleSpinBox {{
        background-color: {BLANCO};
        color: {NEGRO};
        border: 1px solid {VERDE};
        border-radius: 8px;
        padding: 7px 10px;
        font-size: 13px;
    }}
    QDialog QComboBox:disabled, QDialog QLineEdit:read-only {{
        background-color: #F3F5F4;
        color: #777777;
    }}
    QDoubleSpinBox:focus {{
        border: 2px solid {VERDE_OSCURO};
    }}
"""
