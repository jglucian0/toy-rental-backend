from django.urls import path
from .views import (
    ClienteListCreateAPIView,
    ClienteDetailAPIView,
    ClientesAtivosAPIView,
    BrinquedoListCreateAPIView,
    BrinquedoDetailAPIView,
    LocacoesListCreateAPIView,
    LocacoesDetailAPIView,
    BrinquedosDisponiveisAPIView,
    ContratoFestaPDFView
)

urlpatterns = [
    # Lista todos os clientes ou cria um novo
    path('clientes/', ClienteListCreateAPIView.as_view(),
         name='cliente-list-create'),

    # Detalhes, edição ou exclusão de um cliente específico
    path('clientes/<int:id>/', ClienteDetailAPIView.as_view(), name='cliente-detail'),

    # Lista apenas os clientes com status ativo
    path('clientes/ativos/', ClientesAtivosAPIView.as_view(), name='clientes-ativos'),

    # Lista todos os brinquedos ou cria um novo
    path('brinquedos/', BrinquedoListCreateAPIView.as_view(),
         name='brinquedo-list-create'),

    # Detalhes, edição ou exclusão de um brinquedo específico
    path('brinquedos/<int:id>/', BrinquedoDetailAPIView.as_view(),
         name='brinquedo-detail'),
    
    # Lista todos os brinquedos disponíveis baseado na data
    path('brinquedos/disponiveis/', BrinquedosDisponiveisAPIView.as_view(),
         name='brinquedos-disponiveis'),
    
    # Lista todas as locações ou cria uma nova
    path('locacoes/', LocacoesListCreateAPIView.as_view(),
         name='locacoes-list-create'),
    
    # Detalhes, edição ou exclusão de uma locação específica
    path('locacoes/<int:id>/', LocacoesDetailAPIView.as_view(),
         name='locacoes-detail'),
    
    # Gera o PDF do contrato de locação de festa
    path("locacoes/<int:festa_id>/contrato", ContratoFestaPDFView.as_view(), name="contrato_festa_pdf"),
]
