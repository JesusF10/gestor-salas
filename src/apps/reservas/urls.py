from .views import (
    encargado_list_view,
    evento_create_view,
    sala_detail_view,
    sala_list_view,
)

from django.urls import path

urlpatterns = [
    path('', sala_list_view, name='sala-list'),
    path('<int:pk>/', sala_detail_view, name='sala-detail'),
    path('eventos/crear/', evento_create_view, name='evento-create'),
    path('encargados/', encargado_list_view, name='encargado-list'),
]
