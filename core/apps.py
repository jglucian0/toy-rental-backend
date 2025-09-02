from django.apps import AppConfig
import threading
from django.db import connection


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        import core.signals

        def agendar_task():
            from background_task.models import Task
            from core.tasks import verificar_festas_do_dia
            if 'background_task' in connection.introspection.table_names():
                if not Task.objects.filter(task_name='core.tasks.verificar_festas_do_dia').exists():
                    verificar_festas_do_dia(repeat=60)

        threading.Timer(5, agendar_task).start()
