from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('login'), name='root-redirect'),
    path('salas/', include('apps.reservas.urls')),
    path('usuarios/', include('apps.usuarios.urls')),
]
