from rest_framework import serializers
from .models import Cliente


class ClienteSerializer(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Cliente
        fields = '__all__'

    def get_status_display(self, obj):
        return obj.get_status_display()
