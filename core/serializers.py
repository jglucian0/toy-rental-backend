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


# Serializa os anexos do contrato de locação
class ContratoAnexoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContratoAnexo
        fields = ['id', 'arquivo', 'data_upload']
