from django.db import models


class Cliente(models.Model):
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
    ]

    nome = models.CharField(max_length=100)  # Orbigatório
    documento = models.CharField(max_length=18)  # Orbigatório
    email = models.EmailField(null=True, blank=True)
    telefone = models.CharField(max_length=15)  # Orbigatório
    status = models.CharField(
        max_length=7, choices=STATUS_CHOICES, default='ativo')  # Orbigatório
    cep = models.CharField(max_length=9, null=True, blank=True)
    endereco = models.CharField(max_length=100)  # Orbigatório
    numero = models.CharField(max_length=5, null=True, blank=True)
    cidade = models.CharField(max_length=100, null=True, blank=True)
    uf = models.CharField(max_length=2, null=True, blank=True)
    complemento = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f'{self.nome} - {self.documento}'
