/**
 * calendar.js
 */

document.addEventListener('DOMContentLoaded', function () {

    const calendarEl = document.getElementById('calendar');

    if (!calendarEl) {
        return;
    }

    // Leer estado de autenticación del usuario desde el DOM
    const isUserAuthenticated = calendarEl.getAttribute('data-authenticated') === 'true';

    // Referencias del modal de Bootstrap y del calendario modal
    const modalEl = document.getElementById('dayScheduleModal');
    const bsModal = modalEl ? new bootstrap.Modal(modalEl) : null;
    let modalCalendar = null;

    // Estado del filtro de salas e historial de vistas para evitar bucles infinitos
    let salaFilter = 'all';
    let currentViewType = 'dayGridMonth';

    // Función auxiliar para formatear la fecha a un texto amigable en español
    function formatearFechaEspanol(fechaStr) {
        const opciones = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        // Añadir hora artificial (T12:00:00) para evitar desajustes de zona horaria al parsear
        const fecha = new Date(fechaStr + 'T12:00:00');
        return fecha.toLocaleDateString('es-MX', opciones);
    }

    // Función para abrir el modal flotante diario
    function abrirModalDia(clickedDate) {
        if (!bsModal) return;

        // Título amigable en el modal
        document.getElementById('modal-date-title').textContent = formatearFechaEspanol(clickedDate);

        // Guardar fecha seleccionada en el elemento modal
        modalEl.setAttribute('data-selected-date', clickedDate);

        // Mostrar modal de Bootstrap
        bsModal.show();
    }

    // Calendario Principal (Solo Mes y Semana)
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'es',
        firstDay: 1,
        height: 650,

        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek' // Se remueve la vista diaria 'timeGridDay'
        },

        buttonText: {
            today:   'Hoy',
            month:   'Mes',
            week:    'Semana',
            list:    'Lista',
        },

        moreLinkText: function (num) {
            return '+ ' + num + ' más';
        },

        // Cargar eventos del backend aplicando el filtro de sala activo
        events: function(info, successCallback, failureCallback) {
            fetch('/salas/eventos/json/')
                .then(response => response.json())
                .then(data => {
                    if (salaFilter !== 'all') {
                        data = data.filter(event => String(event.numero_sala) === String(salaFilter));
                    }
                    successCallback(data);
                })
                .catch(error => failureCallback(error));
        },

        // Coloreado dinámico según la sala del evento
        eventDataTransform: function(eventData) {
            const colors = {
                '1': { bg: '#2563eb', border: '#1d4ed8', text: '#ffffff' }, // Sala 1: Azul vibrante
                '2': { bg: '#10b981', border: '#047857', text: '#ffffff' }, // Sala 2: Verde esmeralda
                '3': { bg: '#8b5cf6', border: '#6d28d9', text: '#ffffff' }  // Sala 3: Violeta/Morado
            };
            const config = colors[String(eventData.numero_sala)] || { bg: '#4b5563', border: '#374151', text: '#ffffff' };

            eventData.backgroundColor = config.bg;
            eventData.borderColor = config.border;
            eventData.textColor = config.text;
            return eventData;
        },

        // Redirigir a vista de detalle del evento
        eventClick: function (info) {
            const eventoId = info.event.id;
            if (eventoId) {
                window.location.href = `/salas/eventos/${eventoId}/`;
            }
        },

        // Al hacer clic en un día en vista mensual o semanal, abrir el modal con el horario del día
        dateClick: function(info) {
            const clickedDate = info.dateStr.split('T')[0];
            abrirModalDia(clickedDate);
        },

        eventDisplay: 'block',
        displayEventTime: true,
        dayMaxEvents: 3,
    });

    calendar.render();

    // Lógica para inicializar y renderizar el calendario diario dentro del modal
    if (modalEl) {
        modalEl.addEventListener('shown.bs.modal', function () {
            const selectedDate = modalEl.getAttribute('data-selected-date');
            const modalCalendarEl = document.getElementById('modal-day-calendar');

            if (!modalCalendarEl || !selectedDate) return;

            // Destruir instancia anterior si existe
            if (modalCalendar) {
                modalCalendar.destroy();
            }

            // Crear instancia diaria de FullCalendar dentro del modal
            modalCalendar = new FullCalendar.Calendar(modalCalendarEl, {
                initialView: 'timeGridDay',
                initialDate: selectedDate,
                locale: 'es',
                firstDay: 1,
                height: 500,
                headerToolbar: false, // Ocultar toolbar para diseño limpio
                allDaySlot: false,
                slotMinTime: '07:00:00', // Horario escolar regular
                slotMaxTime: '22:00:00',

                events: function(info, successCallback, failureCallback) {
                    fetch('/salas/eventos/json/')
                        .then(response => response.json())
                        .then(data => {
                            if (salaFilter !== 'all') {
                                data = data.filter(event => String(event.numero_sala) === String(salaFilter));
                            }
                            successCallback(data);
                        })
                        .catch(error => failureCallback(error));
                },

                eventDataTransform: function(eventData) {
                    const colors = {
                        '1': { bg: '#2563eb', border: '#1d4ed8', text: '#ffffff' },
                        '2': { bg: '#10b981', border: '#047857', text: '#ffffff' },
                        '3': { bg: '#8b5cf6', border: '#6d28d9', text: '#ffffff' }
                    };
                    const config = colors[String(eventData.numero_sala)] || { bg: '#4b5563', border: '#374151', text: '#ffffff' };
                    eventData.backgroundColor = config.bg;
                    eventData.borderColor = config.border;
                    eventData.textColor = config.text;
                    return eventData;
                },

                // Click en eventos del modal redirige al detalle
                eventClick: function(info) {
                    const eventoId = info.event.id;
                    if (eventoId) {
                        bsModal.hide();
                        window.location.href = `/salas/eventos/${eventoId}/`;
                    }
                },

                // Selección de horario libre para reservar
                selectable: isUserAuthenticated,
                selectMirror: true,
                select: function(info) {
                    if (isUserAuthenticated) {
                        const start = new Date(info.startStr);
                        const yyyy = start.getFullYear();
                        const mm = String(start.getMonth() + 1).padStart(2, '0');
                        const dd = String(start.getDate()).padStart(2, '0');
                        const fecha = `${yyyy}-${mm}-${dd}`;

                        const hh_ini = String(start.getHours()).padStart(2, '0');
                        const min_ini = String(start.getMinutes()).padStart(2, '0');
                        const hora_inicio = `${hh_ini}:${min_ini}`;

                        const end = new Date(info.endStr);
                        const hh_fin = String(end.getHours()).padStart(2, '0');
                        const min_fin = String(end.getMinutes()).padStart(2, '0');
                        const hora_fin = `${hh_fin}:${min_fin}`;

                        bsModal.hide();
                        window.location.href = `/salas/eventos/crear/?fecha=${fecha}&hora_inicio=${hora_inicio}&hora_fin=${hora_fin}`;
                    }
                },

                eventDisplay: 'block',
                displayEventTime: true
            });

            modalCalendar.render();
        });

        // Limpiar el calendario del modal al cerrarse para liberar memoria
        modalEl.addEventListener('hidden.bs.modal', function () {
            if (modalCalendar) {
                modalCalendar.destroy();
                modalCalendar = null;
            }
        });
    }

    // Lógica para botones de filtrado rápido de salas
    document.querySelectorAll('.btn-filter-sala').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.btn-filter-sala').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            salaFilter = this.getAttribute('data-sala');

            // Actualizar calendario principal
            calendar.refetchEvents();

            // Si el modal está abierto, también actualizar el del modal
            if (modalCalendar) {
                modalCalendar.refetchEvents();
            }
        });
    });

});
