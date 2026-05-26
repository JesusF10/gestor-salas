"""
URLs del módulo de reservas.
"""

from .views import (
    dashboard_view,
    evento_create_view,
    evento_detail_view,
    evento_editar_view,
    evento_eliminar_view,
    evento_reporte_view,
    eventos_json_view,
    eventos_lista_view,
    reportes_view,
    sala_create_view,
    sala_detail_view,
    sala_editar_view,
    sala_eliminar_view,
    sala_list_view,
)

from django.urls import path

urlpatterns = [
    # Dashboard principal
    path("dashboard/", dashboard_view, name="dashboard"),

    # Salas: CRUD
    path("", sala_list_view, name="sala-list"),
    path("salas/crear/", sala_create_view, name="sala-create"),
    path("<int:pk>/", sala_detail_view, name="sala-detail"),
    path("salas/<int:pk>/editar/", sala_editar_view, name="sala-editar"),
    path("salas/<int:pk>/eliminar/", sala_eliminar_view, name="sala-eliminar"),

    # Sección Eventos con buscador y filtros
    path("eventos/", eventos_lista_view, name="eventos-lista"),
    path("eventos/<int:pk>/", evento_detail_view, name="evento-detail"),

    # Eventos: CRUD completo
    path("eventos/crear/", evento_create_view, name="evento-create"),
    path("eventos/<int:pk>/editar/", evento_editar_view, name="evento-editar"),
    path("eventos/<int:pk>/eliminar/", evento_eliminar_view, name="evento-eliminar"),
    path("eventos/<int:pk>/reporte/", evento_reporte_view, name="evento-reporte"),

    # Endpoint JSON para FullCalendar
    path("eventos/json/", eventos_json_view, name="eventos-json"),

    # Reportes
    path("reportes/", reportes_view, name="reportes"),
]
