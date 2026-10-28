"""
estilos_asistencia.py
---------------------
Estilos propios del área de Asistencia (mensaje de guardado y selector de culto).
"""
from modulos.dashboard.estilos_dashboard import VERDE, VERDE_OSCURO, BLANCO, NEGRO, TEXTO_SUAVE

ESTILO_ASISTENCIA = f"""
    QLabel#estado_guardado {{
        color: {VERDE_OSCURO};
        background-color: #DDF1E6;
        border-radius: 10px;
        padding: 5px 14px;
        font-size: 13px;
    }}
    QLabel#contador_asistencia {{
        color: {TEXTO_SUAVE};
        font-size: 13px;
    }}
    QComboBox#selector_culto {{
        background-color: {BLANCO};
        color: {NEGRO};
        border: 1px solid {VERDE};
        border-radius: 15px;
        padding: 6px 14px;
        font-size: 13px;
        min-width: 340px;
    }}
    QComboBox#selector_culto QAbstractItemView {{
        background-color: {BLANCO};
        color: {NEGRO};
        selection-background-color: #DDF1E6;
        selection-color: {NEGRO};
    }}
"""
