from datetime import datetime
from typing import Any

from django.contrib.auth.hashers import make_password
from django.db import connection


def crear_usuario_sql(
    username: str, password_raw: str, rol: str, email: str = ""
) -> int:
    """
    Crea un usuario.
    Se utiliza make_password para cumplir con la seguridad de Django (hashing).
    """
    password_hashed = make_password(password_raw)
    ahora = datetime.now()

    with connection.cursor() as cursor:
        query = """
            INSERT INTO usuarios (
                username, password, rol, email,
                is_superuser, is_staff, is_active,
                first_name, last_name, date_joined
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        params = [
            username,
            password_hashed,
            rol,
            email,
            False,  # is_superuser
            False,  # is_staff
            True,  # is_active
            "",  # first_name
            "",  # last_name
            ahora,
        ]
        cursor.execute(query, params)
        row = cursor.fetchone()
        if row:
            return int(row[0])
        raise Exception("Error al insertar usuario")


def obtener_usuario_por_username_sql(username: str) -> dict[str, Any] | None:
    """
    Busca un usuario por su username.
    """
    with connection.cursor() as cursor:
        query = "SELECT id, username, password, rol, is_active FROM usuarios \
        WHERE username = %s;"
        cursor.execute(query, [username])
        row = cursor.fetchone()

        if not row:
            return None

        return {
            "id": row[0],
            "username": row[1],
            "password": row[2],
            "rol": row[3],
            "is_active": row[4],
        }


def listar_usuarios_sql() -> list[dict[str, Any]]:
    """
    Lista todos los usuarios (excepto passwords).
    """
    with connection.cursor() as cursor:
        query = "SELECT id, username, rol, email, date_joined FROM usuarios;"
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row, strict=False)) for row in cursor.fetchall()]
