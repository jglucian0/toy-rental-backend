from django.db import models
from django.utils.timezone import make_aware
from django.contrib.auth.models import User
from datetime import datetime
from decimal import Decimal
from django.db.models import Sum


class Organization(models.Model):
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_query_name='owned_organizations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile")
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="users")

    def __str__(self):
        return f"{self.user.username} ({self.organization.name})"


class Cliente(models.Model):
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="clientes"
    )
    # Opções pro campo 'status' (usado pra exibir no select e no display)
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
    ]

    nome = models.CharField(max_length=100)  # Obrigatório
    documento = models.CharField(max_length=18)  # CPF ou CNPJ - Obrigatório
    email = models.EmailField(null=True, blank=True)  # Opcional
    telefone = models.CharField(max_length=15)  # Obrigatório
    status = models.CharField(
        # Select (Ativo/Inativo)
        max_length=7, choices=STATUS_CHOICES, default='ativo')

    cep = models.CharField(max_length=9)  # Obrigatório
    endereco = models.CharField(max_length=100)  # Obrigatório
    numero = models.CharField(max_length=5, default='S/N')  # Obrigatório
    cidade = models.CharField(
        max_length=100)  # Obrigatório
    uf = models.CharField(max_length=2)  # Obrigatório
    complemento = models.CharField(
        max_length=100, null=True, blank=True)  # Opcional

    def __str__(self):
        return f'{self.nome} - {self.documento}'


class Brinquedo(models.Model):
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="brinquedos",
        null=True,
        blank=True
    )

    PARCELADO_CHOICES = [
        ('sim', 'Sim'),
        ('nao', 'Não'),
    ]

    # Opções de status do brinquedo
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
    ]

    # Opções de voltagem (aparecem no display também)
    VOLTAGEM_CHOICES = [
        ('110v', '110v'),
        ('220v', '220v'),
        ('bivolt', 'Bivolt'),
    ]

    ENERGIA_CHOICES = [
        ('sim', 'Sim'),
        ('nao', 'Não'),
    ]

    INFLAVEL_CHOICES = [
        ('sim', 'Sim'),
        ('nao', 'Não'),
    ]

    nome = models.CharField(max_length=100)  # Nome do brinquedo
    valor_diaria = models.DecimalField(
        max_digits=10, decimal_places=2)  # Ex: 120.00
    qtd_total = models.IntegerField()  # Quantos brinquedos no total
    qtd_disponivel = models.IntegerField()  # Quantos disponíveis pra alugar
    status = models.CharField(choices=STATUS_CHOICES,
                              default='ativo')  # Ativo/Inativo

    tamanho = models.CharField(max_length=10)  # Ex: "3x3m"
    voltagem = models.CharField(
        choices=VOLTAGEM_CHOICES, null=True, blank=True)  # Opcional
    energia = models.CharField(
        choices=ENERGIA_CHOICES, null=True, blank=True)  # Usa energia?
    inflavel = models.CharField(
        choices=INFLAVEL_CHOICES, null=True, blank=True)  # É inflável?
    # Texto descritivo (opcional)
    descricao = models.TextField(null=True, blank=True)

    # --- Campos de aquisição ---
    valor_compra = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    parcelado = models.CharField(
        choices=PARCELADO_CHOICES, null=True, blank=True)
    qtd_parcelas = models.IntegerField(
        null=True, blank=True)
    data_vencimento = models.DateField(null=True, blank=True)
    data_aquisicao = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.nome} - {self.valor_diaria}'


class Locacao(models.Model):
    DURACAO_CHOICES = [
        ('3h', '3 hora'),
        ('4h', '4 hora'),
        ('5h', '5 horas'),
        ('6h', '6 horas'),
        ('7h', '7 horas'),
        ('8h', '8 horas'),
        ('9h', '9 horas'),
        ('10h', '10 horas'),
    ]

    PAGAMENTO_CHOICES = [
        ('nao_pago', 'Não Pago'),
        ('entrada', 'Entrada Paga'),
        ('pago', 'Pago'),
    ]

    STATUS_CHOICES = [
        ('pendente', 'Pendente'),  # Agendado, mas ainda sem sinal
        ('confirmado', 'Confirmado'),  # Pagamento parcial feito
        ('montado', 'Montado'),  # Brinquedos já estão no local e montados
        ('recolher', 'Recolher'),  # Festa acabou, falta recolher os brinquedos
        ('finalizado', 'Finalizado'),  # Tudo concluído, pagamento total feito
    ]

    METODOS_PAGAMENTO_CHOICES = [
        ('dinheiro', 'Dinheiro'),
        ('debito', 'Débito'),
        ('credito', 'Crédito'),
        ('pix', 'Pix'),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="locacoes"
    )
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    brinquedos = models.ManyToManyField(Brinquedo)
    data_festa = models.DateField()
    hora_festa = models.TimeField()
    duracao = models.CharField(choices=DURACAO_CHOICES, default='8h')
    hora_montagem = models.TimeField()
    data_desmontagem = models.DateField()
    hora_desmontagem = models.TimeField()
    montador = models.CharField(max_length=100)
    valor_entrada = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal("0.00"))
    valor_total = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal("0.00"))
    valor_restante = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal("0.00"))
    acrescimos = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal("0.00"))
    descontos = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal("0.00"))
    pagamento = models.CharField(
        max_length=20, choices=PAGAMENTO_CHOICES, default='nao_pago')
    qtd_parcelas = models.IntegerField(default='1')
    status = models.CharField(choices=STATUS_CHOICES, default='pendente')
    metodo_pagamento = models.CharField(
        choices=METODOS_PAGAMENTO_CHOICES, default='pix')
    descricao = models.TextField(null=True, blank=True)

    # Endereço da locação (caso diferente do cliente)
    cep = models.CharField(max_length=9)  # Obrigatório
    endereco = models.CharField(max_length=100)  # Obrigatório
    numero = models.CharField(max_length=5, default='S/N')  # Obrigatório
    cidade = models.CharField(
        max_length=100)  # Obrigatório
    uf = models.CharField(max_length=2)  # Obrigatório
    complemento = models.CharField(
        max_length=100, null=True, blank=True)  # Opcional

    def save(self, *args, **kwargs):
        """Sempre recalcula o valor_restante baseado no total e entrada."""
        entrada = self.valor_entrada or Decimal("0.00")
        self.valor_restante = (self.valor_total or Decimal("0.00")) - entrada
        super().save(*args, **kwargs)

    @property
    def valor_total_calculado(self):
        """Calcula total em tempo real (sem salvar)."""
        total_brinquedos = sum(b.valor_diaria for b in self.brinquedos.all())
        return total_brinquedos + (self.acrescimos or Decimal('0.00')) - (self.descontos or Decimal('0.00'))

    @property
    def valor_saldo(self):
        if self.pagamento == 'entrada':
            return self.valor_total - self.valor_entrada
        elif self.pagamento == 'pago':
            return Decimal('0.00')
        return self.valor_total

    def __str__(self):
        try:
            brinquedos = ", ".join([b.nome for b in self.brinquedos.all()])
            return f'{self.cliente.nome} - {self.data_festa} a {self.data_desmontagem} - {brinquedos} ({self.get_status_display()})'
        except Exception:
            return f'{self.cliente.nome} - {self.data_festa} a {self.data_desmontagem} - (sem brinquedos) ({self.get_status_display()})'


class ContratoAnexo(models.Model):
    locacao = models.ForeignKey(Locacao, on_delete=models.CASCADE)
    arquivo = models.FileField(upload_to='contratos_anexos/')
    data_upload = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Anexo: {self.arquivo.name} - {self.locacao}'


class Transacoes(models.Model):
    PARCELADO_CHOICES = [
        ('sim', 'Sim'),
        ('nao', 'Não'),
    ]

    STATUS_CHOICES = [
        ('pago', 'Pago'),
        ('entrada', 'Entrada'),
        ('nao_pago', 'Não Pago'),
        ('planejado', 'Planejado'),
        ('cancelado', 'Cancelado'),
    ]

    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('saida', 'Saida'),
    ]

    CATEGORIA_CHOICES = [
        ('aluguel', 'Aluguel'),
        ('manutencao', 'Manutenção'),
        ('salario', 'Salário'),
        ('compra', 'Compra'),
        ('investimento', 'Investimento'),
        ('pagamento', 'Pagamento'),
        ('combustivel', 'Combustível'),
        ('outro', 'Outro'),
    ]

    ORIGEM_CHOICES = [

        ('manual', 'Manual'),
        ('locacao', 'Locação'),
        ("investimento_brinquedo", "Investimento Brinquedo"),
    ]

    FORMA_PAGAMENTO_CHOICES = [
        ('dinheiro', 'Dinheiro'),
        ('debito', 'Débito'),
        ('credito', 'Crédito'),
        ('pix', 'Pix'),
        ('boleto', 'Boleto'),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="transacoes"
    )
    locacao = models.ForeignKey(
        'Locacao', null=True, blank=True, on_delete=models.SET_NULL)
    cliente = models.ForeignKey(
        'Cliente', null=True, blank=True, on_delete=models.SET_NULL)
    brinquedo = models.ForeignKey(
        Brinquedo, null=True, blank=True, on_delete=models.SET_NULL)
    id = models.AutoField(primary_key=True)
    referencia_id = models.IntegerField(null=True, blank=True)
    data_transacao = models.DateField()
    data_vencimento = models.DateField(null=True, blank=True)
    data_aquisicao = models.DateField(null=True, blank=True)
    tipo = models.CharField(max_length=8, choices=TIPO_CHOICES)
    valor = models.DecimalField(max_digits=8, decimal_places=2)
    categoria = models.CharField(max_length=12, choices=CATEGORIA_CHOICES)
    pagamento = models.CharField(max_length=10, choices=STATUS_CHOICES)
    forma_pagamento = models.CharField(
        max_length=20, choices=FORMA_PAGAMENTO_CHOICES, null=True, blank=True)
    descricao = models.TextField(null=True, blank=True)
    parcelado = models.CharField(
        choices=PARCELADO_CHOICES, null=True, blank=True)
    origem = models.CharField(max_length=23, choices=ORIGEM_CHOICES)
    qtd_parcelas = models.IntegerField(null=True, blank=True)
    parcela_atual = models.IntegerField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Transação"
        verbose_name_plural = "Transações"
        ordering = ['-data_transacao', 'id']

    def __str__(self):
        return f'{self.id} - {self.data_transacao} - {self.tipo} - {self.valor} - {self.categoria}'

    @classmethod
    def saldo_ate(cls, data):
        entradas = cls.objects.filter(data_transacao__lte=data, tipo='entrada', status='pago').aggregate(
            Sum('valor'))['valor__sum'] or 0
        saidas = cls.objects.filter(data_transacao__lte=data, tipo='saida', status='pago').aggregate(
            Sum('valor'))['valor__sum'] or 0
        return entradas - saidas

    @property
    def is_parcela(self):
        return self.qtd_parcelas and self.qtd_parcelas > 1
