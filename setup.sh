#!/bin/bash

# Script de inicialización para el Gestor de Salas
# Este script configura el entorno, aplica migraciones y puebla datos iniciales.

echo "Iniciando configuración del proyecto..."

# 1. Instalar dependencias
echo "Instalando dependencias con uv..."
uv sync

# 2. Aplicar migraciones (Estructura DDL)
echo "Aplicando migraciones a la base de datos..."
uv run python src/manage.py migrate

# 3. Crear salas iniciales (DML)
echo "Creando salas iniciales (1, 2, 3)..."
uv run python src/manage.py shell -c "from apps.reservas.services import crear_salas_iniciales_sql; crear_salas_iniciales_sql()"

# 4. Crear usuario administrador de forma interactiva
echo "Verificando existencia de usuario administrador..."
# Usamos tail -n 1 para obtener solo la última línea del output (True/False)
ADMIN_EXISTS=$(uv run python src/manage.py shell -c "from apps.usuarios.services import listar_usuarios_sql; print(any(u['rol'] == 'admin' for u in listar_usuarios_sql()))" | tail -n 1 | xargs)

if [ "$ADMIN_EXISTS" == "False" ]; then
    echo "--------------------------------------------------------"
    echo "No se detectó un usuario administrador en la base de datos."
    echo "Por favor, crea las credenciales iniciales:"

    read -p "Nombre de usuario [admin]: " ADMIN_USER
    ADMIN_USER=${ADMIN_USER:-admin}

    # Bucle para asegurar que las contraseñas coincidan
    while true; do
        read -sp "Contraseña: " ADMIN_PASS
        echo ""
        read -sp "Confirma la contraseña: " ADMIN_PASS_CONFIRM
        echo ""

        if [ "$ADMIN_PASS" == "$ADMIN_PASS_CONFIRM" ]; then
            uv run python src/manage.py shell -c "from apps.usuarios.services import crear_usuario_sql; crear_usuario_sql('$ADMIN_USER', '$ADMIN_PASS', 'admin')"
            echo "Usuario '$ADMIN_USER' creado exitosamente."
            break
        else
            echo "Error: Las contraseñas no coinciden. Inténtalo de nuevo."
        fi
    done
    echo "--------------------------------------------------------"
else
    echo "El sistema ya cuenta con un usuario administrador."
fi

echo "Configuración completada con éxito."
echo "Puedes iniciar el servidor con: uv run python src/manage.py runserver"
