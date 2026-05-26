"""
Vistas del módulo de reservas.

Todas las operaciones de datos usan DML SQL puro mediante services.py.
Queda prohibido el uso de métodos ORM como .objects.filter(), .save(), etc.
"""

from typing import Any

from .services import (
    actualizar_evento_sql,
    actualizar_sala_sql,
    buscar_eventos_sql,
    crear_evento_sql,
    crear_sala_sql,
    eliminar_evento_sql,
    eliminar_sala_sql,
    guardar_reporte_sql,
    listar_eventos_para_calendario_sql,
    listar_eventos_semana_sql,
    listar_eventos_sql,
    listar_salas_sql,
    obtener_evento_sql,
    obtener_sala_sql,
    verificar_colision_sala_sql,
    verificar_colision_sql,
)

from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def dashboard_view(request: Any) -> Any:
    """
    Vista principal del sistema.
    Muestra las tarjetas horizontales de estadísticas al principio
    y el calendario de disponibilidad de pantalla completa.
    """
    eventos_semana = listar_eventos_semana_sql()
    salas = listar_salas_sql()

    # Calcular total de eventos hoy sumando los de cada sala
    total_hoy = sum(sala.get("eventos_hoy", 0) for sala in salas)

    return render(
        request,
        "reservas/dashboard.html",
        {
            "eventos_semana": eventos_semana,
            "total_eventos_semana": len(eventos_semana),
            "total_hoy": total_hoy,
            "salas": salas,
        },
    )


@login_required
@require_http_methods(["GET"])
def sala_list_view(request: Any) -> Any:
    """
    Vista para listar todas las salas disponibles.
    """
    salas = listar_salas_sql()
    return render(request, "reservas/sala_list.html", {"salas": salas})


@login_required
@require_http_methods(["GET"])
def sala_detail_view(request: Any, pk: int) -> Any:
    """
    Vista de detalle de una sala individual.
    """
    sala = obtener_sala_sql(pk)
    if not sala:
        raise Http404("Sala no encontrada.")
    return render(request, "reservas/sala_detail.html", {"sala": sala})


@login_required
@require_http_methods(["GET", "POST"])
def sala_create_view(request: Any) -> Any:
    """
    Vista para crear una nueva sala.
    """
    if request.method == "POST":
        numero_sala_raw = request.POST.get("numero_sala", "").strip()
        capacidad_raw = request.POST.get("capacidad", "").strip()

        if not numero_sala_raw or not capacidad_raw:
            return render(
                request,
                "reservas/sala_form.html",
                {"error": "Todos los campos son obligatorios."},
            )

        try:
            numero_sala = int(numero_sala_raw)
            capacidad = int(capacidad_raw)

            if verificar_colision_sala_sql(numero_sala):
                return render(
                    request,
                    "reservas/sala_form.html",
                    {"error": f"Ya existe una sala con el número {numero_sala}."},
                )

            crear_sala_sql(numero_sala, capacidad)
            return redirect("sala-list")
        except ValueError:
            return render(
                request,
                "reservas/sala_form.html",
                {
                    "error": "Los campos de número de sala y capacidad deben ser valores numéricos."
                },
            )

    return render(request, "reservas/sala_form.html")


@login_required
@require_http_methods(["GET", "POST"])
def sala_editar_view(request: Any, pk: int) -> Any:
    """
    Vista para editar una sala existente.
    """
    sala = obtener_sala_sql(pk)
    if not sala:
        raise Http404("Sala no encontrada.")

    if request.method == "POST":
        numero_sala_raw = request.POST.get("numero_sala", "").strip()
        capacidad_raw = request.POST.get("capacidad", "").strip()

        if not numero_sala_raw or not capacidad_raw:
            return render(
                request,
                "reservas/sala_editar.html",
                {"error": "Todos los campos son obligatorios.", "sala": sala},
            )

        try:
            numero_sala = int(numero_sala_raw)
            capacidad = int(capacidad_raw)

            if verificar_colision_sala_sql(numero_sala, excluir_sala_id=pk):
                return render(
                    request,
                    "reservas/sala_editar.html",
                    {
                        "error": f"Ya existe una sala con el número {numero_sala}.",
                        "sala": sala,
                    },
                )

            actualizar_sala_sql(pk, numero_sala, capacidad)
            return redirect("sala-list")
        except ValueError:
            return render(
                request,
                "reservas/sala_editar.html",
                {
                    "error": "Los campos de número de sala y capacidad deben ser valores numéricos.",
                    "sala": sala,
                },
            )

    return render(request, "reservas/sala_editar.html", {"sala": sala})


@login_required
@require_http_methods(["POST"])
def sala_eliminar_view(request: Any, pk: int) -> Any:
    """
    Vista para eliminar una sala.
    """
    sala = obtener_sala_sql(pk)
    if not sala:
        raise Http404("Sala no encontrada.")

    eliminar_sala_sql(pk)
    return redirect("sala-list")


@login_required
@require_http_methods(["GET", "POST"])
def evento_create_view(request: Any) -> Any:
    """
    Vista para crear un nuevo evento.
    GET:  Muestra el formulario con salas desde BD.
    POST: Valida horario mínimo (≥20 min), colisión e inserta.
    """
    salas = listar_salas_sql()

    if request.method == "POST":
        datos = request.POST

        nombre = datos.get("nombre", "").strip()
        fecha = datos.get("fecha", "")
        hora_inicio = datos.get("hora_inicio", "")
        hora_fin = datos.get("hora_fin", "")
        sala_id_raw = datos.get("sala_id", "")
        encargado = datos.get("encargado", "").strip()
        requerimientos: list[str] = datos.getlist("requerimientos")

        asistentes_raw = datos.get("asistentes", "0").strip()
        try:
            asistentes = int(asistentes_raw) if asistentes_raw else 0
            if asistentes <= 0:
                raise ValueError()
        except ValueError:
            return render(
                request,
                "reservas/evento_form.html",
                {
                    "error": "La cantidad de asistentes debe ser un número entero positivo.",
                    "salas": salas,
                },
            )

        # Validar sala seleccionada
        if not sala_id_raw:
            return render(
                request,
                "reservas/evento_form.html",
                {
                    "error": "Debes seleccionar una sala para el evento.",
                    "salas": salas,
                },
            )

        sala_id = int(sala_id_raw)

        # Validar capacidad de la sala seleccionada
        sala = obtener_sala_sql(sala_id)
        if sala and asistentes > sala.get("capacidad", 0):
            return render(
                request,
                "reservas/evento_form.html",
                {
                    "error": f"La cantidad de asistentes ({asistentes}) supera la capacidad máxima de la Sala {sala['numero_sala']} ({sala['capacidad']} personas).",
                    "salas": salas,
                },
            )

        # Validar duración mínima
        if hora_inicio and hora_fin:
            h_ini = int(hora_inicio.split(":")[0]) * 60 + int(hora_inicio.split(":")[1])
            h_fin = int(hora_fin.split(":")[0]) * 60 + int(hora_fin.split(":")[1])
            diferencia = h_fin - h_ini

            if diferencia < 20:
                return render(
                    request,
                    "reservas/evento_form.html",
                    {
                        "error": "La hora de fin debe ser mínimo 20 minutos después de la hora de inicio.",
                        "salas": salas,
                    },
                )

        try:
            hay_colision = verificar_colision_sql(
                sala_id=sala_id,
                fecha=fecha,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
            )
            if hay_colision:
                return render(
                    request,
                    "reservas/evento_form.html",
                    {
                        "error": "⚠️ Conflicto de horario: ya existe un evento en esa sala durante el horario indicado. Selecciona una sala diferente o ajusta el horario.",
                        "salas": salas,
                    },
                )

            crear_evento_sql(
                nombre=nombre,
                fecha=fecha,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                encargado=encargado,
                sala_id=sala_id,
                requerimientos=requerimientos,
                asistentes=asistentes,
            )
            return redirect("dashboard")

        except Exception as excepcion:
            return render(
                request,
                "reservas/evento_form.html",
                {
                    "error": f"Ocurrió un error al guardar el evento: {excepcion}",
                    "salas": salas,
                },
            )

    return render(
        request,
        "reservas/evento_form.html",
        {
            "salas": salas,
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def evento_editar_view(request: Any, pk: int) -> Any:
    """
    Vista para editar un evento existente.
    GET:  Muestra el formulario con datos pre-llenados.
    POST: Valida duración, colisión (excluyendo el evento actual) y actualiza.
    """
    evento = obtener_evento_sql(pk)
    if not evento:
        raise Http404("Evento no encontrado.")

    salas = listar_salas_sql()

    if request.method == "POST":
        datos = request.POST

        nombre = datos.get("nombre", "").strip()
        fecha = datos.get("fecha", "")
        hora_inicio = datos.get("hora_inicio", "")
        hora_fin = datos.get("hora_fin", "")
        sala_id_raw = datos.get("sala_id", "")
        encargado = datos.get("encargado", "").strip()
        requerimientos: list[str] = datos.getlist("requerimientos")

        asistentes_raw = datos.get("asistentes", "0").strip()
        try:
            asistentes = int(asistentes_raw) if asistentes_raw else 0
            if asistentes <= 0:
                raise ValueError()
        except ValueError:
            return render(
                request,
                "reservas/evento_editar.html",
                {
                    "error": "La cantidad de asistentes debe ser un número entero positivo.",
                    "evento": evento,
                    "salas": salas,
                },
            )

        if not sala_id_raw:
            return render(
                request,
                "reservas/evento_editar.html",
                {
                    "error": "Debes seleccionar una sala para el evento.",
                    "evento": evento,
                    "salas": salas,
                },
            )

        sala_id = int(sala_id_raw)

        # Validar capacidad de la sala seleccionada
        sala = obtener_sala_sql(sala_id)
        if sala and asistentes > sala.get("capacidad", 0):
            return render(
                request,
                "reservas/evento_editar.html",
                {
                    "error": f"La cantidad de asistentes ({asistentes}) supera la capacidad máxima de la Sala {sala['numero_sala']} ({sala['capacidad']} personas).",
                    "evento": evento,
                    "salas": salas,
                },
            )

        # Validar duración mínima (≥20 minutos)
        if hora_inicio and hora_fin:
            h_ini = int(hora_inicio.split(":")[0]) * 60 + int(hora_inicio.split(":")[1])
            h_fin = int(hora_fin.split(":")[0]) * 60 + int(hora_fin.split(":")[1])
            diferencia = h_fin - h_ini

            if diferencia < 20:
                return render(
                    request,
                    "reservas/evento_editar.html",
                    {
                        "error": "La hora de fin debe ser mínimo 20 minutos después de la hora de inicio.",
                        "evento": evento,
                        "salas": salas,
                    },
                )

        try:
            hay_colision = verificar_colision_sql(
                sala_id=sala_id,
                fecha=fecha,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                excluir_evento_id=pk,
            )
            if hay_colision:
                return render(
                    request,
                    "reservas/evento_editar.html",
                    {
                        "error": "⚠️ Conflicto de horario: ya existe un evento en esa sala durante el horario indicado. Selecciona una sala diferente o ajusta el horario.",
                        "evento": evento,
                        "salas": salas,
                    },
                )

            actualizar_evento_sql(
                evento_id=pk,
                nombre=nombre,
                fecha=fecha,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                encargado=encargado,
                requerimientos=requerimientos,
                sala_id=sala_id,
                asistentes=asistentes,
            )
            return redirect("dashboard")

        except Exception as excepcion:
            return render(
                request,
                "reservas/evento_editar.html",
                {
                    "error": f"Ocurrió un error al actualizar el evento: {excepcion}",
                    "evento": evento,
                    "salas": salas,
                },
            )

    return render(
        request,
        "reservas/evento_editar.html",
        {
            "evento": evento,
            "salas": salas,
        },
    )


@login_required
@require_http_methods(["POST"])
def evento_eliminar_view(request: Any, pk: int) -> Any:
    """
    Vista para eliminar un evento.
    Solo acepta POST (confirmado desde el modal Bootstrap en evento_editar.html).
    """
    evento = obtener_evento_sql(pk)
    if not evento:
        raise Http404("Evento no encontrado.")

    eliminar_evento_sql(pk)
    return redirect("dashboard")


@login_required
@require_http_methods(["POST"])
def evento_reporte_view(request: Any, pk: int) -> Any:
    """
    Vista para guardar (o actualizar) el reporte de un evento.
    Sobreescribe el texto anterior; un solo reporte por evento.
    Solo accesible para usuarios autenticados (personal permitido).
    """
    evento = obtener_evento_sql(pk)
    if not evento:
        raise Http404("Evento no encontrado.")

    reporte = request.POST.get("reporte", "").strip()
    guardar_reporte_sql(evento_id=pk, reporte=reporte)
    return redirect("evento-detail", pk=pk)


@login_required
@require_http_methods(["GET"])
def reportes_view(request: Any) -> Any:
    """
    Vista de reportes e incidentes por evento.
    """
    return render(
        request,
        "reservas/reportes.html",
        {
            "eventos": listar_eventos_sql(),
        },
    )


@require_http_methods(["GET"])
def eventos_json_view(request: Any) -> Any:
    """
    Endpoint JSON para alimentar FullCalendar en el dashboard.
    Retorna eventos en formato: [{id, title, start, end}, ...]
    """
    eventos = listar_eventos_para_calendario_sql()
    return JsonResponse(eventos, safe=False)


# Lista de requerimientos disponibles para el filtro del buscador
REQUERIMIENTOS_DISPONIBLES: list[str] = [
    "Equipo de Sonido",
    "Cafetería",
    "Video Conferencia",
    "Acomodo de Sillas",
    "Proyector",
]


@require_http_methods(["GET"])
def eventos_lista_view(request: Any) -> Any:
    """
    Vista de la sección Eventos: lista completa con buscador y filtros.

    Acepta los siguientes parámetros GET:
    - q:             Búsqueda parcial por nombre de evento (ILIKE).
    - sala_id:       Filtrar por sala (ID numérico).
    - fecha:         Filtrar por fecha exacta (YYYY-MM-DD).
    - requerimiento: Filtrar por requerimiento específico (array contains).

    Si no se envía ningún parámetro, se muestran todos los eventos.
    """
    # Leer parámetros GET (cadenas vacías → None para que el servicio las ignore)
    nombre = request.GET.get("q", "").strip() or None
    sala_id_raw = request.GET.get("sala_id", "").strip()
    fecha = request.GET.get("fecha", "").strip() or None
    requerimiento = request.GET.get("requerimiento", "").strip() or None

    sala_id: int | None = int(sala_id_raw) if sala_id_raw else None

    # Llamada al servicio DML con filtros combinados
    eventos = buscar_eventos_sql(
        nombre=nombre,
        sala_id=sala_id,
        fecha=fecha,
        requerimiento=requerimiento,
    )

    # Salas para el select de filtro
    salas = listar_salas_sql()

    # Cantidad total de resultados para mostrar en el encabezado
    total = len(eventos)

    # Filtros activos para mostrar etiquetas de "filtro aplicado"
    filtros_activos = {
        "q": nombre or "",
        "sala_id": sala_id_raw,
        "fecha": fecha or "",
        "requerimiento": requerimiento or "",
    }

    return render(
        request,
        "reservas/eventos_lista.html",
        {
            "eventos": eventos,
            "salas": salas,
            "requerimientos_disponibles": REQUERIMIENTOS_DISPONIBLES,
            "filtros_activos": filtros_activos,
            "total": total,
        },
    )


@require_http_methods(["GET"])
def evento_detail_view(request: Any, pk: int) -> Any:
    """
    Vista de detalle de un evento individual.
    Accesible para invitados y administradores.
    """
    evento = obtener_evento_sql(pk)
    if not evento:
        raise Http404("Evento no encontrado.")
    return render(request, "reservas/evento_detail.html", {"evento": evento})
