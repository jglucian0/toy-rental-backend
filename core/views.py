from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Cliente, Brinquedo, Locacao
from .serializers import ClienteSerializer, BrinquedoSerializer, LocacaoSerializer

# Cliente API
# Lista todos os clientes ou cria um novo


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


# Lista só os clientes com status "ativo"
class ClientesAtivosAPIView(APIView):
    def get(self, request):
        clientes = Cliente.objects.filter(status='ativo')
        serializer = ClienteSerializer(clientes, many=True)
        return Response(serializer.data)


# Detalhe, edição e exclusão de cliente específico
class ClienteDetailAPIView(APIView):
    # Função interna pra buscar cliente ou retornar None
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

# Brinquedos
# Lista todos os brinquedos ou cria um novo


class BrinquedoListCreateAPIView(APIView):
    def get(self, request):
        brinquedos = Brinquedo.objects.all()
        serializer = BrinquedoSerializer(brinquedos, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BrinquedoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Detalhe, edição e exclusão de brinquedo específico
class BrinquedoDetailAPIView(APIView):
    # Busca o brinquedo ou retorna None
    def get_object(self, id):
        try:
            return Brinquedo.objects.get(id=id)
        except Brinquedo.DoesNotExist:
            return None

    def get(self, request, id):
        brinquedo = self.get_object(id)
        if not brinquedo:
            return Response({'erro': 'Brinquedo não encontrado'}, status=404)
        serializer = BrinquedoSerializer(brinquedo)
        return Response(serializer.data)

    def put(self, request, id):
        brinquedo = self.get_object(id)
        if not brinquedo:
            return Response({'erro': 'Brinquedo não encontrado'}, status=404)
        serializer = BrinquedoSerializer(brinquedo, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({'erro': 'Dados inválidos'}, status=400)

    def delete(self, request, id):
        brinquedo = self.get_object(id)
        if not brinquedo:
            return Response({'erro': 'Brinquedo não encontrado'}, status=404)
        brinquedo.delete()
        return Response(status=204)


# Locações
# Lista todas as locações ou cria uma nova
class LocacoesListCreateAPIView(APIView):
    def get(self, request):
        locacoes = Locacao.objects.all()
        serializer = LocacaoSerializer(locacoes, many=True)
        return Response(serializer.data)

    def post(self, request):
        locacoes = LocacaoSerializer(data=request.data)
        if locacoes.is_valid():
            locacoes.save()
            return Response(locacoes.data, status=status.HTTP_201_CREATED)
        return Response(locacoes.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LocacoesDetailAPIView(APIView):
    # Busca a locação ou retorna None
    def get_object(self,id):
        festas = Locacao.objects.get(id=id)
        try:
            return festas
        except Locacao.DoesNotExist:
            return None
        
    def get(self, request, id):
        festa = self.get_object(id)
        if not festa:
            return Response({'erro': 'Locação não encontrada'}, status=404)
        serializer = LocacaoSerializer(festa)
        return Response(serializer.data)
    
    def put(self, request, id):
        festa = self.get_object(id)
        if not festa:
            return Response({'erro': 'Locação não encontrada'}, status=404)
        serializer = LocacaoSerializer(festa, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({'erro': 'Dados inválidos'}, status=400)
    
    def delete(self, request, id):
        festa = self.get_object(id=id)
        if not festa:
            return Response({'erro': 'Locação não encontrada'}, status=404)
        festa.delete()
        return Response(status=204)


        
    
    
    