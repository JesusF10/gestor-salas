from .views import login_view, usuario_list_view

from django.contrib.auth import views as auth_views
from django.urls import path

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("", usuario_list_view, name="usuario-list"),
]
