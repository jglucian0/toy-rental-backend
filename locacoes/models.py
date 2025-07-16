from django.db import models
from datetime import timedelta, time

class Cliente(models.Model):
  nome = models.CharField(max_length=100)
  documento = models.CharField(max_length=14, unique=True)
  telefone = models.CharField(max_length=11)
  email = models.EmailField(blank=True, null=None)
  cep = models.CharField(max_length=20, default="85260-000")
  rua = models.CharField(max_length=100)
  numero = models.CharField(max_length=20, default="S/N")
  bairro = models.CharField(max_length=100, blank=True, null=None)
  cidade = models.CharField(max_length=100, default='Manoel Ribas')
  estado = models.CharField(max_length=100, default='Paraná')
  pais = models.CharField(max_length=100, default="Brasil")
  complemento = models.CharField(max_length=255, blank=True, null=None)
  status = models.CharField(max_length=20, default="ativo")
  observacoes = models.TextField(blank=True, null=None)

  def __str__(self):
    return self.nome


class Brinquedo(models.Model):
  nome = models.CharField(max_length=100)
  quantidade = models.CharField(max_length=20, default="1")
  valor_unitario = models.DecimalField(
      max_digits=8, decimal_places=2, default=0.00)

  def __str__(self):
    return f"{self.nome} - {self.quantidade}"


class Locacao(models.Model):
  cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
  brinquedos = models.ManyToManyField(Brinquedo)

  data_festa = models.DateField(null=True, blank=True)
  hora_festa = models.TimeField(null=True, blank=True)
  duração = models.DurationField(default=timedelta(hours=2))
  hora_montagem = models.TimeField(null=True, blank=True)

  data_retirada = models.DateField()
  hora_retirada = models.TimeField(null=True, blank=True)
  montador = models.CharField(max_length=100, blank=True, null=True)

  valor_entrada = models.DecimalField(
      max_digits=10, decimal_places=2, default=0)
  qtd_parcelas = models.PositiveIntegerField(default=1)
  valor_total = models.DecimalField(
      max_digits=10, decimal_places=2, default=0)
  descricao = models.TextField(blank=True, null=True)

  metodo_pagamento = models.CharField(
      max_length=20,
      choices=[
          ('Dinheiro', 'Dinheiro'),
          ('Cartão', 'Cartão'),
          ('Pix', 'Pix'),
      ]
  )

  status = models.CharField(
      max_length=20,
      choices=[
          ('pendente', 'Pendente'),
          ('confirmado', 'Confirmado'),
          ('cancelado', 'Cancelado'),
          ('finalizado', 'Finalizado'),
      ],
      default='Pendente'
  )

  # Endereço da locação (caso diferente do cliente)
  cep = models.CharField(max_length=10, default="85260000")
  rua = models.CharField(max_length=100)
  numero = models.CharField(max_length=10, default="S/N")
  bairro = models.CharField(max_length=100, blank=True, null=True)
  cidade = models.CharField(max_length=100, default="Maneol Ribas")
  uf = models.CharField(max_length=2, default="PR")
  pais = models.CharField(max_length=50, default="Brasil")
  complemento = models.CharField(max_length=100, blank=True, null=True)

  def __str__(self):
    return f"{self.cliente.nome} - {self.data_festa.strftime('%d/%m/%Y')}"

  class Meta:
    ordering = ['-data_festa', '-hora_festa']
