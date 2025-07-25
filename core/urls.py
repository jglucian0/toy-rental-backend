from django.urls import path
from .views import ClienteListCreateAPIView, ClienteDetailAPIView, ClientesAtivosAPIView

urlpatterns = [
    path('clientes/', ClienteListCreateAPIView.as_view(),
         name='cliente-list-create'),
    path('clientes/<int:id>/', ClienteDetailAPIView.as_view(),
         name='cliente-detail'),
    path('clientes/ativos/', ClientesAtivosAPIView.as_view(),
         name='clientes-ativos'),
]
