from django.urls import path
from .views import ClienteListCreateAPIView

urlpatterns = [
    path('clientes/', ClienteListCreateAPIView.as_view(),
         name='cliente-list-create'),
]
