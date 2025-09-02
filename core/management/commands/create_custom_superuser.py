
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Cria um superusuário de forma não interativa usando variáveis de ambiente'

    def handle(self, *args, **options):
        username = os.environ.get('jgluciano ')
        email = os.environ.get('jgluciano.luz@gmail.com')
        password = os.environ.get('@Agbdlcid10')

        if not all([username, email, password]):
            self.stdout.write(self.style.ERROR(
                'As variáveis de ambiente jgluciano, jgluciano.luz@gmail.com e @Agbdlcid10 devem ser definidas.'))
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(
                f"Usuário '{username}' já existe. Nenhuma ação foi tomada."))
        else:
            User.objects.create_superuser(
                username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(
                f"Superusuário '{username}' criado com sucesso!"))
