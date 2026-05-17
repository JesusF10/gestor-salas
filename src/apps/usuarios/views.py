from typing import Any

from .models import Usuario
from .services import (
    crear_usuario_sql,
    listar_usuarios_sql,
    obtener_usuario_por_username_sql,
)

from django.contrib.auth import login as auth_login
from django.contrib.auth.hashers import check_password
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET", "POST"])
def login_view(request: Any) -> Any:
    """
    Vista de login.
    """
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        usuario_data = obtener_usuario_por_username_sql(username) if username else None

        if usuario_data and check_password(password, usuario_data["password"]):
            # Para usar login() de Django, necesitamos una instancia del modelo.
            # Como usamos DML para obtener los datos, obtenemos la instancia por ID vía
            # ORM solo para la sesión.
            try:
                user_obj = Usuario.objects.get(id=usuario_data["id"])
                auth_login(request, user_obj)
                return redirect("sala-list")
            except Usuario.DoesNotExist:
                pass

        return render(
            request, "usuarios/login.html", {"error": "Credenciales inválidas"}
        )

    return render(request, "usuarios/login.html")


@require_http_methods(["GET", "POST"])
def usuario_list_view(request: Any) -> Any:
    """
    Lista y crea usuarios.
    """
    if request.method == "POST":
        data = request.POST
        try:
            crear_usuario_sql(
                username=data["username"],
                password_raw=data["password"],
                rol=data.get("rol", "operativo"),
                email=data.get("email", ""),
            )
        except Exception:
            pass

    usuarios = listar_usuarios_sql()
    return render(request, "usuarios/usuario_list.html", {"usuarios": usuarios})
