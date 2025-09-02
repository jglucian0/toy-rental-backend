
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Cria um superusuário de forma não interativa usando variáveis de ambiente'

    def handle(self, *args, **options):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not all([username, email, password]):
            self.stdout.write(self.style.ERROR(
                'As variáveis de ambiente DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL e DJANGO_SUPERUSER_PASSWORD devem ser definidas.'))
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(
                f"Usuário '{username}' já existe. Nenhuma ação foi tomada."))
        else:
            User.objects.create_superuser(
                username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(
                f"Superusuário '{username}' criado com sucesso!"))
