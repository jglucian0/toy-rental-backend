from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Locacao, Transacoes
from datetime import timedelta
from dateutil.relativedelta import relativedelta


@receiver(post_save, sender=Locacao)
def sync_locacao_to_transacao(sender, instance, created, **kwargs):
    # só cria a primeira vez
    if created:
        # valor por parcela
        qtd_parcelas = instance.qtd_parcelas or 1
        valor_parcela = instance.valor_total / qtd_parcelas

        for i in range(1, qtd_parcelas + 1):
            # calcula data da parcela: pode ser mensal ou igual a data_festa
            data_parcela = instance.data_festa + relativedelta(months=i-1)

            Transacoes.objects.create(
                locacao=instance,
                cliente=instance.cliente,
                origem='locacao',
                data_transacao=data_parcela,
                tipo="entrada",
                valor=valor_parcela,
                categoria="aluguel",
                pagamento=instance.pagamento,
                descricao=f"Parcela {i}/{qtd_parcelas} da locação {instance.id}",
                parcelamento_total=qtd_parcelas,
                parcelamento_num=i,
            )
    else:
        # Atualiza apenas a primeira transação ou todas?
        # Se quiser atualizar todas, percorra:
        transacoes = Transacoes.objects.filter(locacao=instance)
        qtd_parcelas = instance.qtd_parcelas or 1
        valor_parcela = instance.valor_total / qtd_parcelas

        for i, t in enumerate(transacoes, start=1):
            t.data_transacao = instance.data_festa + relativedelta(months=i-1)
            t.valor = valor_parcela
            t.pagamento = instance.pagamento
            t.cliente = instance.cliente
            t.descricao = f"Parcela {i}/{qtd_parcelas} da locação {instance.id}"
            t.save(update_fields=["data_transacao", "valor",
                   "pagamento", "descricao", "cliente"])


@receiver(post_save, sender=Transacoes)
def sync_transacao_to_locacao(sender, instance, created, **kwargs):
    """
    Sempre que uma Transacao de origem 'locacao' for atualizada,
    garante que o pagamento da Locacao acompanhe.
    """
    if instance.origem == 'locacao' and instance.locacao:
        locacao = instance.locacao
        if locacao.pagamento != instance.pagamento:
            locacao.pagamento = instance.pagamento
            locacao.save(update_fields=["pagamento"])


@receiver(pre_delete, sender=Locacao)
def cancelar_transacao_com_locacao(sender, instance, **kwargs):
    """
    Quando uma Locacao for deletada/cancelada,
    marca a Transacao associada como cancelada em vez de sumir.
    """
    transacao = Transacoes.objects.filter(
        locacao=instance, origem="locacao").first()
    if transacao:
        transacao.pagamento = "cancelado"
        transacao.descricao += " (Cancelada junto com a locação)"
        transacao.save(update_fields=["pagamento", "descricao"])
