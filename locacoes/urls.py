from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LocacoesHojeView, atualizar_status, brinquedos_disponiveis, LocacaoCreateView, ClienteViewSet, ClienteCreateView, FestaDetailUpdateView, ClienteDetailUpdateView, LocacoesViewSet

router = DefaultRouter()
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'festas', LocacoesViewSet, basename='festa')

urlpatterns = [
    path('locacoes-hoje/', LocacoesHojeView.as_view()),
    path("clientes/novo/", ClienteCreateView.as_view(), name="cliente-create"),
    path("clientes/<int:pk>/", ClienteDetailUpdateView.as_view(), name="cliente-detail"),
    path("festas/nova/", LocacaoCreateView.as_view(), name="festa-create"),
    path('brinquedos/disponiveis/', brinquedos_disponiveis),
    path('locacoes/<int:pk>/status/', atualizar_status, name='atualizar-status'),
    path('', include(router.urls)),
]
