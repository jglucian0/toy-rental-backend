from rest_framework import serializers
from .models import Cliente, Brinquedo, Locacao, ContratoAnexo


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
    
    class Meta:
        model = Locacao
        fields = '__all__'

    def get_status_display(self, obj):
        return obj.get_status_display()


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
