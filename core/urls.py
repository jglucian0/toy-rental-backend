from django.urls import path
from . import views

patterns = [
    path('/', views.proximas_festas, name='proximas_festas'),
]