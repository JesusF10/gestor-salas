from .views import login_view, usuario_list_view

from django.urls import path

urlpatterns = [
    path("login/", login_view, name="login"),
    path("", usuario_list_view, name="usuario-list"),
]
