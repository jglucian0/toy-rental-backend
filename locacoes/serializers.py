from rest_framework import serializers
from .models import Cliente, Brinquedo, Locacao

class ClienteSerializer(serializers.ModelSerializer):
  class Meta:
    model = Cliente
    fields = '__all__'
  
class BrinquedoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brinquedo
        fields = '__all__'
        

class LocacaoSerializer(serializers.ModelSerializer):
    cliente_id = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.all(), source='cliente', write_only=True
    )
    brinquedos_ids = serializers.PrimaryKeyRelatedField(
        queryset=Brinquedo.objects.all(), many=True, source='brinquedos', write_only=True
    )

    cliente = ClienteSerializer(read_only=True)
    brinquedos = BrinquedoSerializer(many=True, read_only=True)

    class Meta:
        model = Locacao
        fields = [
            'id', 'cliente', 'cliente_id',
            'brinquedos', 'brinquedos_ids',
            'data_festa', 'hora_festa', 'duração', 'hora_montagem',
            'data_retirada', 'hora_retirada', 'montador',
            'valor_entrada', 'qtd_parcelas', 'valor_total',
            'descricao', 'metodo_pagamento', 'status',
            'cep', 'rua', 'numero', 'bairro', 'cidade', 'uf', 'pais', 'complemento',
        ]
