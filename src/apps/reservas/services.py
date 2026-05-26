"""
Capa de acceso a datos (DML SQL puro) para el módulo de reservas.

REGLA: Todas las operaciones sobre registros se realizan con SQL crudo
usando django.db.connection. Queda prohibido el uso de métodos ORM como
.objects.filter(), .save(), .create(), etc.

Los parámetros dinámicos siempre se pasan como segundo argumento de
cursor.execute() para prevenir inyección SQL.
"""

from datetime import date, time
from typing import Any

from django.db import connection

# =============================================================================
# SALAS
# =============================================================================


def listar_salas_sql() -> list[dict[str, Any]]:
    """
    Lista todas las salas con el conteo de eventos de hoy para el dashboard.
    El campo 'eventos_hoy' sirve para el widget "Eventos de Hoy" del lateral.
    """
    with connection.cursor() as cursor:
        query = """
            SELECT
                s.id,
                s.numero_sala,
                s.capacidad,
                COUNT(e.id) FILTER (WHERE e.fecha = CURRENT_DATE) AS eventos_hoy
            FROM salas s
            LEFT JOIN eventos e ON e.sala_id = s.id
            GROUP BY s.id, s.numero_sala, s.capacidad
            ORDER BY s.numero_sala;
        """
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row, strict=False)) for row in cursor.fetchall()]


def obtener_sala_sql(sala_id: int) -> dict[str, Any] | None:
    """
    Obtiene una sala por su ID.
    Retorna None si no existe.
    """
    with connection.cursor() as cursor:
        query = "SELECT id, numero_sala, capacidad FROM salas WHERE id = %s;"
        cursor.execute(query, [sala_id])
        row = cursor.fetchone()

        if not row:
            return None

        columns = [col[0] for col in cursor.description]
        return dict(zip(columns, row, strict=False))


def crear_sala_sql(numero_sala: int, capacidad: int) -> None:
    """
    Inserta una nueva sala en la base de datos mediante DML SQL puro.
    """
    with connection.cursor() as cursor:
        query = "INSERT INTO salas (numero_sala, capacidad) VALUES (%s, %s);"
        cursor.execute(query, [numero_sala, capacidad])


def actualizar_sala_sql(sala_id: int, numero_sala: int, capacidad: int) -> None:
    """
    Actualiza una sala existente en la base de datos mediante DML SQL puro.
    """
    with connection.cursor() as cursor:
        query = "UPDATE salas SET numero_sala = %s, capacidad = %s WHERE id = %s;"
        cursor.execute(query, [numero_sala, capacidad, sala_id])


def eliminar_sala_sql(sala_id: int) -> None:
    """
    Elimina una sala de la base de datos mediante DML SQL puro.
    """
    with connection.cursor() as cursor:
        query = "DELETE FROM salas WHERE id = %s;"
        cursor.execute(query, [sala_id])


def verificar_colision_sala_sql(
    numero_sala: int, excluir_sala_id: int | None = None
) -> bool:
    """
    Verifica si ya existe una sala con el número indicado.
    """
    with connection.cursor() as cursor:
        if excluir_sala_id is not None:
            query = "SELECT EXISTS(SELECT 1 FROM salas WHERE numero_sala = %s AND id != %s);"
            cursor.execute(query, [numero_sala, excluir_sala_id])
        else:
            query = "SELECT EXISTS(SELECT 1 FROM salas WHERE numero_sala = %s);"
            cursor.execute(query, [numero_sala])
        return cursor.fetchone()[0]


def crear_salas_iniciales_sql() -> None:
    """
    Crea las salas iniciales si no existen.
    Salas 1, 2 y 3 con capacidad 40 cada una.
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM salas;")
        count = cursor.fetchone()[0]

        if count == 0:
            query = "INSERT INTO salas (numero_sala, capacidad) VALUES (%s, %s);"
            cursor.execute(query, [1, 40])
            cursor.execute(query, [2, 40])
            cursor.execute(query, [3, 40])


# =============================================================================
# EVENTOS: CREACIÓN Y VALIDACIÓN
# =============================================================================


def verificar_colision_sql(
    sala_id: int,
    fecha: date,
    hora_inicio: time,
    hora_fin: time,
    excluir_evento_id: int | None = None,
) -> bool:
    """
    Verifica si existe un traslape de horario para una sala en una fecha dada.
    Retorna True si hay colisión, False si el horario está libre.

    El parámetro excluir_evento_id permite ignorar el evento que se está
    editando, evitando que colisione consigo mismo al actualizarse.
    """
    with connection.cursor() as cursor:
        if excluir_evento_id is not None:
            query = """
                SELECT EXISTS (
                    SELECT 1 FROM eventos
                    WHERE sala_id = %s
                    AND fecha = %s
                    AND hora_inicio < %s
                    AND hora_fin > %s
                    AND id != %s
                );
            """
            cursor.execute(
                query, [sala_id, fecha, hora_fin, hora_inicio, excluir_evento_id]
            )
        else:
            query = """
                SELECT EXISTS (
                    SELECT 1 FROM eventos
                    WHERE sala_id = %s
                    AND fecha = %s
                    AND hora_inicio < %s
                    AND hora_fin > %s
                );
            """
            cursor.execute(query, [sala_id, fecha, hora_fin, hora_inicio])

        row = cursor.fetchone()
        return bool(row[0]) if row else False


def crear_evento_sql(
    nombre: str,
    fecha: date,
    hora_inicio: time,
    hora_fin: time,
    encargado: str,
    sala_id: int,
    requerimientos: list[str] | None = None,
    asistentes: int = 0,
) -> int:
    """
    Inserta un nuevo evento en la base de datos.
    El campo encargado es texto libre (nombre directo).
    Retorna el ID del evento creado.
    """
    with connection.cursor() as cursor:
        query = """
            INSERT INTO eventos (
                nombre, fecha, hora_inicio, hora_fin,
                encargado, sala_id, requerimientos,
                asistentes, reporte
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        params: list[Any] = [
            nombre,
            fecha,
            hora_inicio,
            hora_fin,
            encargado,
            sala_id,
            requerimientos or [],
            asistentes,
            "",  # reporte vacío al crear
        ]
        cursor.execute(query, params)
        row = cursor.fetchone()
        if row:
            return int(row[0])
        raise Exception("Error al insertar el evento en la base de datos.")


# =============================================================================
# EVENTOS: CONSULTA
# =============================================================================


def listar_eventos_sql() -> list[dict[str, Any]]:
    """
    Lista todos los eventos con datos de sala.
    Ordenados por fecha descendente para mostrar los más recientes primero.
    El campo 'encargado' es texto directo (sin JOIN a tabla encargados).
    """
    with connection.cursor() as cursor:
        query = """
            SELECT
                e.id,
                e.nombre,
                e.fecha,
                e.hora_inicio,
                e.hora_fin,
                e.encargado,
                e.requerimientos,
                e.reporte,
                e.sala_id,
                e.asistentes,
                s.numero_sala
            FROM eventos e
            INNER JOIN salas s ON e.sala_id = s.id
            ORDER BY e.fecha DESC, e.hora_inicio DESC;
        """
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row, strict=False)) for row in cursor.fetchall()]


def listar_eventos_proximos_sql() -> list[dict[str, Any]]:
    """
    Lista los eventos con fecha >= hoy (eventos futuros o de hoy).
    Ordenados ascendentemente para mostrar los más próximos primero.
    Máximo 10 para el panel lateral del dashboard.
    """
    with connection.cursor() as cursor:
        query = """
            SELECT
                e.id,
                e.nombre,
                e.fecha,
                e.hora_inicio,
                e.hora_fin,
                s.numero_sala
            FROM eventos e
            INNER JOIN salas s ON e.sala_id = s.id
            WHERE e.fecha >= CURRENT_DATE
            ORDER BY e.fecha ASC, e.hora_inicio ASC
            LIMIT 10;
        """
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row, strict=False)) for row in cursor.fetchall()]


def obtener_evento_sql(evento_id: int) -> dict[str, Any] | None:
    """
    Obtiene un evento por su ID junto con los datos de la sala.
    Retorna None si el evento no existe.
    """
    with connection.cursor() as cursor:
        query = """
            SELECT
                e.id,
                e.nombre,
                e.fecha,
                e.hora_inicio,
                e.hora_fin,
                e.encargado,
                e.requerimientos,
                e.reporte,
                e.sala_id,
                e.asistentes,
                s.numero_sala,
                s.capacidad
            FROM eventos e
            INNER JOIN salas s ON e.sala_id = s.id
            WHERE e.id = %s;
        """
        cursor.execute(query, [evento_id])
        row = cursor.fetchone()

        if not row:
            return None

        columns = [col[0] for col in cursor.description]
        return dict(zip(columns, row, strict=False))


# =============================================================================
# EVENTOS: ACTUALIZACIÓN Y ELIMINACIÓN
# =============================================================================


def actualizar_evento_sql(
    evento_id: int,
    nombre: str,
    fecha: date,
    hora_inicio: time,
    hora_fin: time,
    encargado: str,
    requerimientos: list[str],
    sala_id: int,
    asistentes: int,
) -> None:
    """
    Actualiza los datos de un evento existente por su ID.
    El campo reporte NO se modifica aquí (se gestiona por guardar_reporte_sql).
    """
    with connection.cursor() as cursor:
        query = """
            UPDATE eventos
            SET
                nombre         = %s,
                fecha          = %s,
                hora_inicio    = %s,
                hora_fin       = %s,
                encargado      = %s,
                requerimientos = %s,
                sala_id        = %s,
                asistentes     = %s
            WHERE id = %s;
        """
        params: list[Any] = [
            nombre,
            fecha,
            hora_inicio,
            hora_fin,
            encargado,
            requerimientos,
            sala_id,
            asistentes,
            evento_id,
        ]
        cursor.execute(query, params)


def guardar_reporte_sql(evento_id: int, reporte: str) -> None:
    """
    Guarda (sobreescribe) el reporte de un evento.
    Un solo campo de texto por evento; se puede editar y reenviar.
    """
    with connection.cursor() as cursor:
        query = """
            UPDATE eventos
            SET reporte = %s
            WHERE id = %s;
        """
        cursor.execute(query, [reporte, evento_id])


def eliminar_evento_sql(evento_id: int) -> None:
    """
    Elimina un evento de la base de datos por su ID.
    Operación irreversible. Solo se invoca tras confirmación del usuario.
    """
    with connection.cursor() as cursor:
        query = "DELETE FROM eventos WHERE id = %s;"
        cursor.execute(query, [evento_id])


# =============================================================================
# CALENDARIO
# =============================================================================


def listar_eventos_para_calendario_sql() -> list[dict[str, Any]]:
    """
    Retorna los eventos en formato compatible con FullCalendar:
    campos 'id', 'title', 'start', 'end' en formato ISO 8601.
    """
    with connection.cursor() as cursor:
        query = """
            SELECT
                e.id,
                e.nombre        AS title,
                (e.fecha::text || 'T' || e.hora_inicio::text) AS start,
                (e.fecha::text || 'T' || e.hora_fin::text)    AS "end",
                s.numero_sala
            FROM eventos e
            INNER JOIN salas s ON e.sala_id = s.id
            ORDER BY e.fecha ASC, e.hora_inicio ASC;
        """
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row, strict=False)) for row in cursor.fetchall()]


# =============================================================================
# BÚSQUEDA Y FILTRADO DE EVENTOS
# =============================================================================


def buscar_eventos_sql(
    nombre: str | None = None,
    sala_id: int | None = None,
    fecha: str | None = None,
    requerimiento: str | None = None,
) -> list[dict[str, Any]]:
    """
    Busca eventos aplicando filtros opcionales de forma combinada.

    Parámetros:
    - nombre:       Búsqueda parcial (ILIKE) en el nombre del evento.
    - sala_id:      Filtra por sala específica.
    - fecha:        Filtra por fecha exacta (formato 'YYYY-MM-DD').
    - requerimiento: Filtra eventos cuyo array de requerimientos contenga
                    el valor indicado (operador @> de PostgreSQL).

    Los filtros que reciban None o cadena vacía se omiten automáticamente.
    Los parámetros se pasan siempre como valores seguros para evitar
    inyección SQL.
    """
    # Base del query con JOIN a salas
    clausulas_where: list[str] = []
    params: list[Any] = []

    if nombre:
        clausulas_where.append("e.nombre ILIKE %s")
        params.append(f"%{nombre}%")

    if sala_id:
        clausulas_where.append("e.sala_id = %s")
        params.append(sala_id)

    if fecha:
        clausulas_where.append("e.fecha = %s")
        params.append(fecha)

    if requerimiento:
        # El operador @> verifica que el array contenga el elemento dado.
        # Se construye un literal de array de un solo elemento para la comparación.
        clausulas_where.append("e.requerimientos @> ARRAY[%s]::text[]")
        params.append(requerimiento)

    # Construir cláusula WHERE completa (vacía si no hay filtros)
    where_sql = ""
    if clausulas_where:
        where_sql = "WHERE " + " AND ".join(clausulas_where)

    with connection.cursor() as cursor:
        query = f"""
            SELECT
                e.id,
                e.nombre,
                e.fecha,
                e.hora_inicio,
                e.hora_fin,
                e.encargado,
                e.requerimientos,
                e.reporte,
                e.sala_id,
                e.asistentes,
                s.numero_sala,
                s.capacidad
            FROM eventos e
            INNER JOIN salas s ON e.sala_id = s.id
            {where_sql}
            ORDER BY e.fecha DESC, e.hora_inicio DESC;
        """
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row, strict=False)) for row in cursor.fetchall()]


def listar_eventos_semana_sql() -> list[dict[str, Any]]:
    """
    Retorna la lista de eventos programados para la semana en curso (Lunes a Domingo).
    """
    with connection.cursor() as cursor:
        query = """
            SELECT
                e.id,
                e.nombre,
                e.fecha,
                e.hora_inicio,
                e.hora_fin,
                s.numero_sala
            FROM eventos e
            INNER JOIN salas s ON e.sala_id = s.id
            WHERE e.fecha BETWEEN (date_trunc('week', CURRENT_DATE)::date) 
                             AND (date_trunc('week', CURRENT_DATE)::date + 6)
            ORDER BY e.fecha ASC, e.hora_inicio ASC;
        """
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row, strict=False)) for row in cursor.fetchall()]
