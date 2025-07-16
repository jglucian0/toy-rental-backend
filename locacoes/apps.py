# locacoes/apps.py

from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.db.utils import OperationalError


class LocacoesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'locacoes'

    def ready(self):
        try:
            User = get_user_model()
            if not User.objects.filter(username="admin").exists():
                User.objects.create_superuser(
                    username="admin",
                    email="admin@email.com",
                    password="admin123"
                )
                print("✅ Superusuário criado: admin / admin123")
        except OperationalError:
            pass
