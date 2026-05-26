"""
URLs raíz del proyecto gestor-salas.
"""

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Raíz -> dashboard (si no está autenticado, las vistas manejan el redirect a login)
    path("", lambda request: redirect("dashboard"), name="root-redirect"),
    path("salas/", include("apps.reservas.urls")),
    path("usuarios/", include("apps.usuarios.urls")),
]
