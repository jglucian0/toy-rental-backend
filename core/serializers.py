from rest_framework import serializers
from .models import Cliente, Brinquedo


class ClienteSerializer(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Cliente
        fields = '__all__'

    def get_status_display(self, obj):
        return obj.get_status_display()


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
