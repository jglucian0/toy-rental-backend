from django.db import models


class Cliente(models.Model):
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

    cep = models.CharField(max_length=9, null=True, blank=True)  # Opcional
    endereco = models.CharField(max_length=100)  # Obrigatório
    numero = models.CharField(max_length=5, null=True, blank=True)  # Opcional
    cidade = models.CharField(
        max_length=100, null=True, blank=True)  # Opcional
    uf = models.CharField(max_length=2, null=True,
                          blank=True)  # Opcional (ex: PR)
    complemento = models.CharField(
        max_length=100, null=True, blank=True)  # Opcional

    def __str__(self):
        return f'{self.nome} - {self.documento}'


class Brinquedo(models.Model):
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
        max_digits=8, decimal_places=2)  # Ex: 120.00
    qtd_total = models.IntegerField()  # Quantos brinquedos no total
    qtd_disponivel = models.IntegerField()  # Quantos disponíveis pra alugar
    status = models.CharField(choices=STATUS_CHOICES, default='ativo')  # Ativo/Inativo

    tamanho = models.CharField(max_length=10)  # Ex: "3x3m"
    voltagem = models.CharField(
        choices=VOLTAGEM_CHOICES, null=True, blank=True)  # Opcional
    energia = models.CharField(
        choices=ENERGIA_CHOICES, null=True, blank=True)  # Usa energia?
    inflavel = models.CharField(
        choices=INFLAVEL_CHOICES, null=True, blank=True)  # É inflável?
    # Texto descritivo (opcional)
    descricao = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.nome} - {self.valor_diaria}'
