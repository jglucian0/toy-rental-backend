from django.contrib import admin
from .models import Cliente, Brinquedo, Locacao

admin.site.register(Cliente)
admin.site.register(Brinquedo)
admin.site.register(Locacao)