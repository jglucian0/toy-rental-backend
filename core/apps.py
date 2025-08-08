from django.apps import AppConfig
import threading


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        def agendar_task():
            from background_task.models import Task
            from core.tasks import verificar_festas_do_dia
            if not Task.objects.filter(task_name='core.tasks.verificar_festas_do_dia').exists():
                verificar_festas_do_dia(repeat=60)

        threading.Timer(5, agendar_task).start()
