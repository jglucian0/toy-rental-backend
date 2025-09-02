from django.contrib import admin
from .models import Cliente, Brinquedo, Locacao, Transacoes, Organization, Profile, Convite
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User


# Define um 'inline' para o modelo Profile
# Isso permite editar o Profile na mesma página do User
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

# Define uma nova classe UserAdmin


class CustomUserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)


# Cancela o registro do modelo User padrão
admin.site.unregister(User)

# Registra o User novamente com nosso CustomUserAdmin
admin.site.register(User, CustomUserAdmin)

# Registra os outros modelos para que apareçam no admin
admin.site.register(Organization)
# Também registramos separadamente para visualização
admin.site.register(Profile)
admin.site.register(Convite)
admin.site.register(Brinquedo)
admin.site.register(Locacao)
admin.site.register(Transacoes)

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "created_at")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "organization")


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
    list_display = ['cliente', 'data_festa', 'data_desmontagem']
    list_filter = ['data_festa', 'data_desmontagem']
    search_fields = ['cliente__nome']
    list_per_page = 20


@admin.register(Transacoes)
class TransacoesAdmin(admin.ModelAdmin):
    list_display = ['data_transacao', 'tipo', 'valor', 'categoria']
    list_filter = ['data_transacao', 'tipo', 'categoria']
    search_fields = ['cliente__nome']
    list_per_page = 20
