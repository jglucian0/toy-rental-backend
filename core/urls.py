from django.urls import path
from .views import (
    LoginCreateAPIView,
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
    TransacoesListCreateAPIView,
    TransacoesDetailAPIView,
    DashboardAPIView,
    InviteUserAPIView,
    AcceptInviteAPIView,
)

urlpatterns = [
    # Login do usuário
    path('login/', LoginCreateAPIView, name='login'),

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
         ContratoLocacaoPDFView.as_view(), name="contrato-locacao-pdf"),

    # URL para upload de anexos do contrato
    path('locacoes/<int:locacao_id>/anexos/',
         ContratoAnexoAPIView.as_view(), name="anexo-locacao-pdf"),

    # Lista todas as transações ou cria uma nova
    path('transacoes/', TransacoesListCreateAPIView.as_view(),
         name='transacoes-list-create'),

    # Detalhes, edição ou exclusão de uma transação específica
    path('transacoes/<int:id>/', TransacoesDetailAPIView.as_view(),
         name='transacoes-detail'),

    path('dashboard/', DashboardAPIView.as_view(), name='dashboard-stats'),
]
