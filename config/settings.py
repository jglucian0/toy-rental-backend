import os
from pathlib import Path
from decouple import config
import dj_database_url

from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model


@receiver(post_migrate)
def create_superuser_on_migrate(sender, **kwargs):
    """
    Cria um superusuário automaticamente após as migrações,
    se as variáveis de ambiente estiverem definidas e o usuário não existir.
    """
    # Garante que o sinal só rode para a app 'core' para evitar duplicidade
    if sender.name == 'core':
        User = get_user_model()
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not all([username, email, password]):
            print(
                'Variáveis de ambiente para superusuário não definidas. Pulando criação.')
            return

        if User.objects.filter(username=username).exists():
            print(
                f"Superusuário '{username}' já existe. Nenhuma ação foi tomada.")
        else:
            print(f"Criando superusuário '{username}'...")
            User.objects.create_superuser(
                username=username, email=email, password=password)
            print(f"Superusuário '{username}' criado com sucesso!")


# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Chave secreta
SECRET_KEY = config('SECRET_KEY')

# Ativa modo debug
DEBUG = config('DEBUG', default=False, cast=bool)

# Lista de hosts permitidos
# Pega os hosts permitidos do .env e transforma em uma lista
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1').split(',')
CORS_ALLOWED_ORIGINS = [
    "https://happykidsmr.netlify.app",
    "http://localhost:8080",
]

# Aplicativos instalados
INSTALLED_APPS = [
    'corsheaders',
    'storages',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'background_task',
    'core',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

# Middlewares que processam as requisições/respostas
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Arquivo principal de roteamento
ROOT_URLCONF = 'config.urls'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Configuração dos templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # pode adicionar caminhos de templates aqui
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Aplicação WSGI (interface para servidores)
WSGI_APPLICATION = 'config.wsgi.application'

# Configuração do banco de dados (padrão: SQLite)
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL')
    )
}
#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': BASE_DIR / 'db.sqlite3',
#    }
#}

# Validação de senha
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Se AWS_STORAGE_BUCKET_NAME estiver definido, usa S3. Senão, usa o local.
if config('AWS_STORAGE_BUCKET_NAME', default=None):
    # Configurações AWS
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

    # Dicionário de STORAGES para produção (S3 + WhiteNoise)
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
else:
    # Dicionário de STORAGES para desenvolvimento local
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

# Idioma e fuso horário
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Caminho dos arquivos estáticos (CSS, JS, imagens)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# Tipo de campo de ID padrão para novos modelos
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
