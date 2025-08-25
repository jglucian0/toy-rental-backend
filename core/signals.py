from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Locacao, Transacoes, Brinquedo
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal


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


@receiver(post_save, sender=Brinquedo)
def sync_brinquedo_to_transacao(sender, instance, created, **kwargs):
    """
    Cria ou atualiza transações do tipo 'investimento' para cada Brinquedo.
    Cada parcela é independente, permitindo controle de pagamento.
    """
    if not instance.valor_compra:
        return  # Não cria transações se não tiver valor de compra

    qtd_parcelas = instance.qtd_parcelas or 1
    valor_total = Decimal(instance.valor_compra)

    if not created:
        old = sender.objects.get(pk=instance.pk)
        if (
            old.valor_compra == instance.valor_compra
            and old.qtd_parcelas == instance.qtd_parcelas
            and old.data_vencimento == instance.data_vencimento
            and old.data_aquisicao == instance.data_aquisicao
            and old.nome == instance.nome
        ):
            return  # nada mudou → não atualiza transações

    # força 2 casas decimais
    valor_parcela = (valor_total / qtd_parcelas).quantize(Decimal("0.01"))

    # Data base da primeira parcela
    data_base = instance.data_vencimento

    # Busca transações já criadas para esse brinquedo
    transacoes_existentes = list(Transacoes.objects.filter(
        origem="investimento_brinquedo",
        parcelamento_total=qtd_parcelas,
        descricao__icontains=f"(ID {instance.id})"
    ).order_by("parcelamento_num"))

    for i in range(1, qtd_parcelas + 1):
        data_parcela = data_base + \
            relativedelta(months=i-1) if data_base else None

        if i <= len(transacoes_existentes):
            # Atualiza parcela existente
            t = transacoes_existentes[i-1]
            t.valor = valor_parcela
            t.data_transacao = data_parcela
            t.descricao = f"Parcela {i}/{qtd_parcelas} do Brinquedo {instance.nome} (ID {instance.id})"
            t.save(update_fields=["valor", "data_transacao", "descricao"])
        else:
            # Cria nova parcela
            Transacoes.objects.create(
                cliente=None,
                brinquedo=instance,
                origem="investimento_brinquedo",
                tipo="saida",
                valor=valor_parcela,
                categoria="investimento",
                pagamento="planejado",
                descricao=f"Parcela {i}/{qtd_parcelas} do Brinquedo {instance.nome} (ID {instance.id})",
                parcelamento_total=qtd_parcelas,
                parcelamento_num=i,
                data_transacao=data_parcela,
            )

@receiver(pre_delete, sender=Brinquedo)
def cancelar_transacao_brinquedo(sender, instance, **kwargs):
    """
    Quando um brinquedo for deletado, marca as transações de investimento como canceladas
    """
    transacoes = Transacoes.objects.filter(
        origem="investimento_brinquedo", descricao__icontains=f"Brinquedo {instance.id}"
    )
    for t in transacoes:
        t.pagamento = "cancelado"
        t.descricao += " (Cancelada junto com o brinquedo)"
        t.save(update_fields=["pagamento", "descricao"])
