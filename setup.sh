#!/bin/bash

# Script de inicialización para el Gestor de Salas
# Este script configura el entorno, aplica migraciones y registra datos iniciales.

echo "Iniciando configuración del proyecto..."

# 1. Instalar dependencias
echo "Instalando dependencias con uv..."
uv sync --all-groups

# 2. Aplicar migraciones (Estructura DDL)
echo "Aplicando migraciones a la base de datos..."
uv run python src/manage.py migrate

# 3. Poblar salas iniciales (DML)
echo "Poblando salas iniciales (1, 2, 3)..."
uv run python src/manage.py shell -c "from apps.reservas.services import crear_salas_iniciales_sql; crear_salas_iniciales_sql()"


# 4. Crear usuario administrador de prueba
echo "Creando usuario administrador (admin/admin123)..."
uv run python src/manage.py shell -c "from apps.usuarios.services import crear_usuario_sql, obtener_usuario_por_username_sql;
if not obtener_usuario_por_username_sql('admin'):
    crear_usuario_sql('admin', 'admin123', 'admin', 'admin@example.com')
    print('Usuario admin creado exitosamente.')
else:
    print('El usuario admin ya existe.')"

echo "Configuración completada con éxito."
echo "Puedes iniciar el servidor con: uv run python src/manage.py runserver"
