from typing import Any

from .services import (
    crear_encargado_sql,
    crear_evento_sql,
    listar_encargados_sql,
    listar_salas_sql,
    obtener_sala_sql,
    verificar_colision_sql,
)

from django.shortcuts import render
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def sala_list_view(request: Any) -> Any:
    """
    Vista para listar salas.
    """
    salas = listar_salas_sql()
    return render(request, "reservas/sala_list.html", {"salas": salas})


@require_http_methods(["GET"])
def sala_detail_view(request: Any, pk: int) -> Any:
    """
    Vista para ver detalle de una sala.
    """
    sala = obtener_sala_sql(pk)
    if not sala:
        return render(request, "404.html", status=404)
    return render(request, "reservas/sala_detail.html", {"sala": sala})


@require_http_methods(["GET", "POST"])
def evento_create_view(request: Any) -> Any:
    """
    Vista para crear un evento.
    """
    if request.method == "POST":
        data = request.POST
        try:
            # Validación de colisiones
            hay_colision = verificar_colision_sql(
                sala_id=int(data["sala_id"]),
                fecha=data["fecha"],
                hora_inicio=data["hora_inicio"],
                hora_fin=data["hora_fin"],
            )

            if hay_colision:
                return render(
                    request,
                    "reservas/evento_form.html",
                    {
                        "error": "Colisión de horario detectada.",
                        "salas": listar_salas_sql(),
                    },
                )

            crear_evento_sql(
                nombre=data["nombre"],
                fecha=data["fecha"],
                hora_inicio=data["hora_inicio"],
                hora_fin=data["hora_fin"],
                asistentes=data.getlist("asistentes"),
                sala_id=int(data["sala_id"]),
                encargado_id=int(data["encargado_id"])
                if data.get("encargado_id")
                else None,
            )
            return render(request, "reservas/evento_success.html")
        except Exception as e:
            return render(
                request,
                "reservas/evento_form.html",
                {"error": str(e), "salas": listar_salas_sql()},
            )

    return render(request, "reservas/evento_form.html", {"salas": listar_salas_sql()})


@require_http_methods(["GET", "POST"])
def encargado_list_view(request: Any) -> Any:
    """
    Vista para listar y crear encargados.
    """
    if request.method == "POST":
        data = request.POST
        try:
            crear_encargado_sql(
                nombre=data["nombre"],
                primerapellido=data["primerapellido"],
                segundoapellido=data.get("segundoapellido"),
            )
        except Exception:
            pass

    encargados = listar_encargados_sql()
    return render(request, "reservas/encargado_list.html", {"encargados": encargados})
