from datetime import date, time
from typing import Any

from django.db import connection


def listar_salas_sql() -> list[dict[str, Any]]:
    """
    Lista todas las salas.
    """
    with connection.cursor() as cursor:
        query = "SELECT id, numero_sala, capacidad FROM salas;"
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row, strict=False)) for row in cursor.fetchall()]


def obtener_sala_sql(sala_id: int) -> dict[str, Any] | None:
    """
    Obtiene una sala por ID.
    """
    with connection.cursor() as cursor:
        query = "SELECT id, numero_sala, capacidad FROM salas WHERE id = %s;"
        cursor.execute(query, [sala_id])
        row = cursor.fetchone()

        if not row:
            return None

        columns = [col[0] for col in cursor.description]
        return dict(zip(columns, row, strict=False))


def crear_evento_sql(
    nombre: str,
    fecha: date,
    hora_inicio: time,
    hora_fin: time,
    asistentes: list[str],
    sala_id: int,
    encargado_id: int | None = None,
) -> int:
    """
    Crea un nuevo evento.
    Retorna el ID del evento creado.
    """
    with connection.cursor() as cursor:
        query = """
            INSERT INTO eventos (
                nombre, fecha, hora_inicio, hora_fin, asistentes, sala_id, encargado_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        # Nota: asistentes se pasa como lista, psycopg lo convierte a array de Postgres
        params: list[Any] = [
            nombre,
            fecha,
            hora_inicio,
            hora_fin,
            asistentes,
            sala_id,
            encargado_id,
        ]
        cursor.execute(query, params)
        row = cursor.fetchone()
        if row:
            return int(row[0])
        raise Exception("Error al insertar evento")


def verificar_colision_sql(
    sala_id: int, fecha: date, hora_inicio: time, hora_fin: time
) -> bool:
    """
    Verifica si existe un traslape de horario para una sala en una fecha específica.
    Retorna True si hay colisión, False si está libre.
    """
    with connection.cursor() as cursor:
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


def listar_encargados_sql() -> list[dict[str, Any]]:
    """
    Lista todos los encargados.
    """
    with connection.cursor() as cursor:
        query = "SELECT id, nombre, primerapellido, segundoapellido FROM encargados;"
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row, strict=False)) for row in cursor.fetchall()]


def crear_encargado_sql(
    nombre: str, primerapellido: str, segundoapellido: str | None = None
) -> int:
    """
    Crea un nuevo encargado.
    """
    with connection.cursor() as cursor:
        query = """
            INSERT INTO encargados (nombre, primerapellido, segundoapellido)
            VALUES (%s, %s, %s)
            RETURNING id;
        """
        cursor.execute(query, [nombre, primerapellido, segundoapellido])
        row = cursor.fetchone()
        if row:
            return int(row[0])
        raise Exception("Error al insertar encargado")


def crear_salas_iniciales_sql() -> None:
    """
    Crea las salas iniciales si no existen.
    Salas 1, 2 y 3 con capacidad 40 cada una.
    """
    with connection.cursor() as cursor:
        # Verificar si ya existen
        cursor.execute("SELECT COUNT(*) FROM salas;")
        count = cursor.fetchone()[0]

        if count == 0:
            query = "INSERT INTO salas (numero_sala, capacidad) VALUES (%s, %s);"
            cursor.execute(query, [1, 40])
            cursor.execute(query, [2, 40])
            cursor.execute(query, [3, 40])
