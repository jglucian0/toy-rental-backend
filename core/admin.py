from django.contrib import admin
from .models import Cliente, Brinquedo, Locacao


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'documento', 'telefone', 'email']
    list_filter = ['cidade', 'uf']
    search_fields = ['nome', 'documento', 'email']
    list_per_page = 20


@admin.register(Brinquedo)
class BrinquedoAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']
    list_per_page = 20


@admin.register(Locacao)
class LocacaoAdmin(admin.ModelAdmin):
    list_display = ['cliente','data_festa', 'data_desmontagem']
    list_filter = ['data_festa', 'data_desmontagem']
    search_fields = ['cliente__nome']
    list_per_page = 20
