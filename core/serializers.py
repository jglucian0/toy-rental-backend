from rest_framework import serializers
from .models import Cliente, Brinquedo, Locacao, ContratoAnexo, Transacoes


# Serializa todos os campos do Cliente + exibe status legível (ex: 'ativo' → 'Ativo')
class ClienteSerializer(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Cliente
        fields = '__all__'  # inclui todos os campos do modelo

    def get_status_display(self, obj):
        return obj.get_status_display()


# Serializa todos os campos do Brinquedo + status e voltagem legíveis
class BrinquedoSerializer(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField()
    voltagem_display = serializers.SerializerMethodField()

    class Meta:
        model = Brinquedo
        fields = '__all__'

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_voltagem_display(self, obj):
        return obj.get_voltagem_display()


# Serializa todos os campos da Locacao + status legível
class LocacaoSerializer(serializers.ModelSerializer):
    brinquedos_ids = serializers.PrimaryKeyRelatedField(
        queryset=Brinquedo.objects.all(), many=True, source='brinquedos', write_only=True
    )

    brinquedos = BrinquedoSerializer(many=True, read_only=True)

    valor_total_calculado = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display', read_only=True
    )

    class Meta:
        model = Locacao
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['valor_total_calculado'] = instance.valor_total_calculado
        return data

    def create(self, validated_data):
        # Remove brinquedos_ids do validated_data para criar Locacao
        brinquedos = validated_data.pop('brinquedos', [])
        locacao = super().create(validated_data)
        locacao.brinquedos.set(brinquedos)

        # Cria a transação automática
        Transacoes.objects.create(
            data_transacao=locacao.data_festa,  # ou data_inicio/data_transacao que você usar
            tipo='entrada',
            valor=locacao.valor_total,
            categoria='aluguel',
            status='pago',
            descricao=f'Transação automática da locação {locacao.id}',
            origem='locacao',
            referencia_id=locacao.id,
            parcelamento_total=1,
            parcelamento_num=1,
        )
        return locacao

    def update(self, instance, validated_data):
        brinquedos = validated_data.pop('brinquedos', None)
        locacao = super().update(instance, validated_data)
        if brinquedos is not None:
            locacao.brinquedos.set(brinquedos)

        # Atualiza ou cria transação automática
        transacao, created = Transacoes.objects.get_or_create(
            referencia_id=locacao.id,
            origem='locacao',
            defaults={
                "data_transacao": locacao.data_festa,
                "tipo": "entrada",
                "valor": locacao.valor_total,
                "categoria": "aluguel",
                "status": "pago",
                "descricao": f"Transação automática da locação {locacao.id}",
                "parcelamento_total": 1,
                "parcelamento_num": 1,
            }
        )

        if not created:  # já existia, então atualiza
            transacao.data_transacao = locacao.data_festa
            transacao.valor = locacao.valor_total
            transacao.status = "pago"
            transacao.descricao = f"Transação automática da locação {locacao.id}"
            transacao.save()

        return locacao

    def cancelar_transacao_automaticamente(self, instance):
        transacao = Transacoes.objects.filter(
            referencia_id=instance.id,
            origem='locacao'
        ).first()
        if transacao:
            transacao.status = 'cancelado'
            transacao.descricao += " (Cancelada junto com a locação)"
            transacao.save()
        return transacao


# Serializa o anexo do contrato de locação
class ContratoAnexoSerializer(serializers.ModelSerializer):
    tem_anexo = serializers.SerializerMethodField()

    class Meta:
        model = ContratoAnexo
        fields = ['id', 'arquivo', 'tem_anexo']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get('request')
        if instance.arquivo and hasattr(instance.arquivo, 'url'):
            rep['arquivo'] = request.build_absolute_uri(instance.arquivo.url)
        else:
            rep['arquivo'] = None
        return rep

    def get_tem_anexo(self, obj):
        return bool(obj.arquivo)


# Serializa as transações
class TransacoesSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(
        source='get_status_display', read_only=True)
    tipo_display = serializers.CharField(
        source='get_tipo_display', read_only=True)
    categoria_display = serializers.CharField(
        source='get_categoria_display', read_only=True)
    origem_display = serializers.CharField(
        source='get_origem_display', read_only=True)

    class Meta:
        model = Transacoes
        fields = '__all__'
        extra_fields = ['status_display', 'tipo_display',
                        'categoria_display', 'origem_display']
