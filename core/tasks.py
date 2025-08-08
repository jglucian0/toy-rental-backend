from background_task import background
from datetime import datetime
from django.utils.timezone import make_aware


@background(schedule=60)
def verificar_festas_do_dia():
    from .models import Locacao  # seu model de festas

    agora = make_aware(datetime.now())
    festas_hoje = Locacao.objects.filter(data_festa=agora.date())

    print(f"Festas de hoje: {festas_hoje.count()}")

    # Agora vamos atualizar os status que precisam mudar
    festas_montadas = Locacao.objects.filter(status='montado')

    for festa in festas_montadas:
        dt_desmontagem = datetime.combine(
            festa.data_desmontagem, festa.hora_desmontagem)
        dt_desmontagem = make_aware(dt_desmontagem)  # torna timezone-aware

        if agora >= dt_desmontagem:
            festa.status = 'recolher'
            festa.save()
            print(f"Status da festa {festa.id} atualizado para 'recolher'")
