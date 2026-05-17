from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado según DBML.
    Roles: admin, operativo.
    """

    ROL_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("admin", "Administrador"),
        ("operativo", "Personal Operativo"),
    ]

    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default="operativo")

    class Meta:
        db_table = "usuarios"
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

    def __str__(self) -> str:
        return f"{self.username} ({self.rol})"
