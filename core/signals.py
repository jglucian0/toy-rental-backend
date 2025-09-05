from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Locacao, Transacoes, Brinquedo
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from django.db.models.signals import m2m_changed
from django.contrib.auth.models import User
from .models import Profile, Organization


@receiver(post_save, sender=Transacoes)
def criar_parcelas_manuais(sender, instance, created, **kwargs):
    """
    Cria as parcelas restantes para uma transação MANUAL recém-criada de forma segura.
    """
    if not created:
        return

    # Roda apenas se for uma transação MANUAL, PARCELADA e com mais de 1 parcela
    if not (
        instance.origem == 'manual' and
        instance.parcelado == 'sim' and
        instance.qtd_parcelas and
        instance.qtd_parcelas > 1
    ):
        return

    # PREVENÇÃO DE LOOP INFINITO:
    # Age apenas sobre a primeira parcela criada pelo usuário.
    if instance.parcela_atual != 1:
        return

    # Dados base da primeira parcela
    descricao_base = instance.descricao.split(' (Parcela')[0]
    valor_total = instance.valor * instance.qtd_parcelas
    valor_parcela = (
        valor_total / instance.qtd_parcelas).quantize(Decimal("0.01"))

    # Loop para criar as parcelas restantes (da 2ª em diante)
    for i in range(2, instance.qtd_parcelas + 1):
        data_nova_parcela = instance.data_transacao + relativedelta(months=i-1)

        # Cria um objeto completamente novo em vez de "clonar" o existente
        Transacoes.objects.create(
            # Copia os campos relevantes da primeira parcela
            organization=instance.organization,
            locacao=instance.locacao,
            cliente=instance.cliente,
            brinquedo=instance.brinquedo,
            tipo=instance.tipo,
            categoria=instance.categoria,
            pagamento=instance.pagamento,  # ou 'planejado' se preferir
            origem=instance.origem,
            parcelado=instance.parcelado,
            referencia_id=instance.referencia_id,

            # Define os campos específicos desta nova parcela
            valor=valor_parcela,
            qtd_parcelas=instance.qtd_parcelas,
            parcela_atual=i,
            data_transacao=data_nova_parcela,
            descricao=f"{descricao_base} (Parcela {i}/{instance.qtd_parcelas})"
        )


@receiver(m2m_changed, sender=Locacao.brinquedos.through)
def atualizar_valores(sender, instance, action, **kwargs):
    if action in ["post_add", "post_remove", "post_clear"]:
        total_brinquedos = sum(
            b.valor_diaria for b in instance.brinquedos.all())
        instance.valor_total = total_brinquedos + \
            (instance.acrescimos or Decimal('0.00')) - \
            (instance.descontos or Decimal('0.00'))

        # Se não foi informado entrada, sugere 30%
        if not instance.valor_entrada or instance.valor_entrada == Decimal("0.00"):
            instance.valor_entrada = instance.valor_total * Decimal("0.3")

        instance.valor_restante = instance.valor_total - instance.valor_entrada
        instance.save()


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
                organization=instance.organization,
                locacao=instance,
                cliente=instance.cliente,
                origem='locacao',
                data_transacao=data_parcela,
                tipo="entrada",
                valor=valor_parcela,
                categoria="aluguel",
                pagamento=instance.pagamento,
                descricao=f"Parcela {i}/{qtd_parcelas} da locação {instance.id}",
                qtd_parcelas=qtd_parcelas,
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
            t.organization = instance.organization
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
    # Adicione a condição "instance.pagamento != 'cancelado'"
    if (
        instance.origem == 'locacao' and
        instance.locacao and
        instance.pagamento != 'cancelado'  # <<-- AQUI ESTÁ A MUDANÇA
    ):
        locacao = instance.locacao
        if locacao.pagamento != instance.pagamento:
            locacao.pagamento = instance.pagamento
            locacao.save(update_fields=["pagamento"])


@receiver(pre_delete, sender=Locacao)
def cancelar_transacao_com_locacao(sender, instance, **kwargs):
    """
    Quando uma Locacao for deletada/cancelada,
    marca TODAS as Transacoes associadas como canceladas.
    """
    # Mude de .first() para .filter() para pegar todas as transações
    transacoes = Transacoes.objects.filter(locacao=instance, origem="locacao")

    # Percorra todas as transações e cancele uma por uma
    for transacao in transacoes:
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
    org = instance.organization

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
        qtd_parcelas=qtd_parcelas,
        descricao__icontains=f"(ID {instance.id})"
    ).order_by("parcela_atual"))

    for i in range(1, qtd_parcelas + 1):
        data_parcela = data_base + \
            relativedelta(months=i-1) if data_base else None

        if i <= len(transacoes_existentes):
            # Atualiza parcela existente
            t = transacoes_existentes[i-1]
            t.organization = org
            t.valor = valor_parcela
            t.data_transacao = data_parcela
            t.descricao = f"Parcela {i}/{qtd_parcelas} do Brinquedo {instance.nome} (ID {instance.id})"
            t.save(update_fields=["valor", "data_transacao", "descricao"])
        else:
            # Cria nova parcela
            Transacoes.objects.create(
                organization=org,
                cliente=None,
                brinquedo=instance,
                origem="investimento_brinquedo",
                tipo="saida",
                valor=valor_parcela,
                categoria="investimento",
                pagamento="planejado",
                descricao=f"Parcela {i}/{qtd_parcelas} do Brinquedo {instance.nome} (ID {instance.id})",
                qtd_parcelas=qtd_parcelas,
                parcela_atual=i,
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
