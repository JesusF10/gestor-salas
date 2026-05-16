---
title: "Propuesta de Proyecto: Sistema Gestor de Salas"
date: \today
geometry: margin=1in
lang: es
header-includes: |
  \usepackage{fontspec}
---

<!--
Genera el documento PDF con Pandoc:
pandoc propuesta.md -o propuesta.pdf --from markdown --template eisvogel --pdf-engine=lualatex

Requisitos:
- Tener instalado Pandoc
- Tener instalado algún motor de compilación de LaTeX:
    - XeLaTeX
    - LuaLaTeX
    - Etc.

-->

# Propuesta de Proyecto: Sistema Gestor de Salas

**Materia:** Bases de Datos I  
**Cliente:** Lic. Cecilia Chávez  
**Estado:** Propuesta Inicial

## 1. El Problema

Actualmente, la gestión, reserva y organización de las salas se realiza de manera manual mediante la
dependencia de un archivo de Excel. Este flujo de trabajo rudimentario genera errores críticos de
forma constante, entre los cuales destacan:

- **Traslapes de horarios:** Agendar múltiples eventos en el mismo espacio, fecha y hora de forma
  simultánea.
- **Falta de espacios:** Ineficiencia en la distribución y conocimiento real de las salas libres.
- **Incumplimiento de requerimientos técnicos:** Olvidos o confusiones al momento de preparar los
  insumos específicos que cada evento solicita.

## 2. La Solución

Se propone el desarrollo de una **aplicación web** dedicada a automatizar y centralizar el control
del Sistema Gestor de Salas. Los pilares fundamentales de la solución son:

- **Control de disponibilidad en tiempo real:** Consulta inmediata del estado de cada espacio
  físico.
- **Validación automática:** Algoritmia en el backend que impide de forma absoluta el registro de
  agendas duplicadas en la misma hora y lugar.
- **Calendario interactivo:** Interfaz gráfica intuitiva para visualizar de forma rápida la
  ocupación diaria, semanal o mensual de las salas.

## 3. Stakeholders (Roles de Usuario)

El sistema segmentará las responsabilidades y accesos a través de dos perfiles principales:

### A. Administrador

- Gestión integral de los eventos (creación, edición, reasignación y cancelación).
- Control total sobre el catálogo de salas y sus características.
- Supervisión de la agenda global.

### B. Personal Operativo

- Revisión de los requerimientos técnicos y logísticos de cada sala.
- Preparación de los espacios físicos con anticipación.
- Consulta de la agenda para coordinar las actividades de soporte.

## 4. Características Clave del Sistema

Para cumplir con las expectativas de la cliente, el sistema priorizará las siguientes
funcionalidades:

1. **Gestión de Eventos:** Alta prioridad en la capacidad de agendar, modificar y dar seguimiento a
   las reuniones o eventos programados.
2. **Prevención de Colisiones:** Validación automática en la base de datos para evitar traslapes de
   horarios en un mismo espacio físico.
3. **Visualización Interactiva:** Despliegue de un calendario dinámico que facilite la lectura de la
   disponibilidad.
4. **Manejo de Requerimientos Adicionales:** Control y asignación de insumos específicos solicitados
   para cada evento (por ejemplo: cantidad de sillas, equipo de sonido, proyectores, café, entre
   otros).
