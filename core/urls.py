from django.urls import path
from .views import (
    ClienteListCreateAPIView,
    ClienteDetailAPIView,
    ClientesAtivosAPIView,
    BrinquedoListCreateAPIView,
    BrinquedoDetailAPIView,
    LocacoesListCreateAPIView,
    LocacoesDetailAPIView,
    LocacoesStatusUpdateAPIView,
    BrinquedosDisponiveisAPIView,
    ContratoLocacaoPDFView,
    ContratoAnexoAPIView,
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
    
    # Atualiza o status de uma locação específica
    path('locacoes/<int:id>/status/',
         LocacoesStatusUpdateAPIView.as_view(), name='locacoes-update-status'),
    
    # Gera o PDF do contrato de locação
    path("locacoes/<int:locacao_id>/contrato/",
         ContratoLocacaoPDFView.as_view(), name="contrato_locacao_pdf"),

    # URL para upload de anexos do contrato
    path('locacoes/<int:locacao_id>/anexos/',
         ContratoAnexoAPIView.as_view(), name="anexo_locacao_pdf"),
]
