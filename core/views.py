from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Cliente
from .serializers import ClienteSerializer


class ClienteListCreateAPIView(APIView):
    def get(self, request):
        clientes = Cliente.objects.all()
        serializer = ClienteSerializer(clientes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ClienteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClientesAtivosAPIView(APIView):
    def get(self, request):
        clientes = Cliente.objects.filter(status='ativo')
        serializer = ClienteSerializer(clientes, many=True)
        return Response(serializer.data)


class ClienteDetailAPIView(APIView):
    def get_object(self, id):
        try:
            return Cliente.objects.get(id=id)
        except Cliente.DoesNotExist:
            return None

    def get(self, request, id):
        cliente = self.get_object(id)
        if not cliente:
            return Response({'erro': 'Cliente não encontrado'}, status=404)
        serializer = ClienteSerializer(cliente)
        return Response(serializer.data)

    def put(self, request, id):
        cliente = self.get_object(id)
        if not cliente:
            return Response({'erro': 'Cliente não encontrado'}, status=404)
        serializer = ClienteSerializer(cliente, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, id):
        cliente = self.get_object(id)
        if not cliente:
            return Response({'erro': 'Cliente não encontrado'}, status=404)
        cliente.delete()
        return Response(status=204)
