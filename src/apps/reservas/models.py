from django.contrib.postgres.fields import ArrayField
from django.db import models


class Encargado(models.Model):
    """
    Modelo para los encargados de los eventos.
    """

    nombre = models.TextField()
    primerapellido = models.TextField()
    segundoapellido = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "encargados"
        verbose_name = "encargado"
        verbose_name_plural = "encargados"

    def __str__(self) -> str:
        return f"{self.nombre} {self.primerapellido}"


class Sala(models.Model):
    """
    Modelo para las salas disponibles.
    """

    numero_sala = models.IntegerField(unique=True)
    capacidad = models.IntegerField(default=40)

    class Meta:
        db_table = "salas"
        verbose_name = "sala"
        verbose_name_plural = "salas"

    def __str__(self) -> str:
        return f"Sala {self.numero_sala} (Capacidad: {self.capacidad})"


class Evento(models.Model):
    """
    Modelo para los eventos programados en las salas.

    Cambios respecto al diseño inicial:
    - encargado: texto libre (nombre directo), ya no FK a la tabla encargados.
    - reporte: texto simple que reemplaza el campo incidentes (array), el
      reporte se puede sobreescribir.
    """

    nombre = models.TextField()
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    # Usando ArrayField de PostgreSQL como se indica en el DBML (text[]). Lo encuentras
    # en docs/database-design/database-design.dbml
    #
    asistentes = ArrayField(models.TextField(), blank=True, default=list)
    requerimientos = ArrayField(models.TextField(), null=True, blank=True)

    # Encargado: texto libre (nombre directo, sin FK)
    encargado = models.TextField(blank=True, default="")

    # Reporte simple: un texto por evento (reemplaza al array de incidentes)
    reporte = models.TextField(blank=True, default="")

    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, db_column="sala_id")

    class Meta:
        db_table = "eventos"
        verbose_name = "evento"
        verbose_name_plural = "eventos"

    def __str__(self) -> str:
        return f"{self.nombre} - {self.fecha} ({self.hora_inicio}-{self.hora_fin})"
