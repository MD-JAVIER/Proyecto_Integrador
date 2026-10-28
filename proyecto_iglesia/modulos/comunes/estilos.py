"""
estilos.py
----------
Junta los estilos de todas las áreas en uno solo. Lo usan la ventana principal
y las ventanas emergentes, para que todo se vea igual.
"""


def estilo_aplicacion():
    from modulos.dashboard.estilos_dashboard import ESTILO_DASHBOARD
    from modulos.miembros.estilos_miembros import ESTILO_MIEMBROS
    from modulos.finanzas.estilos_finanzas import ESTILO_FINANZAS
    from modulos.actividades.estilos_actividades import ESTILO_ACTIVIDADES
    from modulos.lideres.estilos_lideres import ESTILO_LIDERES
    from modulos.asistencia.estilos_asistencia import ESTILO_ASISTENCIA
    return ESTILO_DASHBOARD + ESTILO_MIEMBROS + ESTILO_FINANZAS + ESTILO_ACTIVIDADES + ESTILO_LIDERES + ESTILO_ASISTENCIA
