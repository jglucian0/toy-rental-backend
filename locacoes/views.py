from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework import viewsets, generics
from rest_framework.response import Response
from datetime import date, datetime
from .models import Locacao, Cliente, Brinquedo
from .serializers import LocacaoSerializer, ClienteSerializer, BrinquedoSerializer
from django.db.models import Count


@api_view(["PATCH"])
def atualizar_status(request, pk):
    try:
        locacao = Locacao.objects.get(pk=pk)
    except Locacao.DoesNotExist:
        return Response({"erro": "Locação não encontrada"}, status=404)

    novo_status = request.data.get("status")
    if novo_status not in ["pendente", "confirmado", "finalizado"]:
        return Response({"erro": "Status inválido"}, status=400)

    locacao.status = novo_status
    locacao.save()

    return Response({"mensagem": "Status atualizado com sucesso"})

@api_view(['GET'])
def brinquedos_disponiveis(request):
    data_festa = request.GET.get('data_festa')
    data_retirada = request.GET.get('data_retirada')

    if not data_festa or not data_retirada:
        return Response({"erro": "datas obrigatórias"}, status=400)

    data_festa = datetime.strptime(data_festa, "%Y-%m-%d").date()
    data_retirada = datetime.strptime(data_retirada, "%Y-%m-%d").date()

    # Locações que conflitam com as datas fornecidas
    locacoes_conflitantes = Locacao.objects.filter(
        data_festa__lte=data_retirada,
        data_retirada__gte=data_festa
    )

    # IDs de brinquedos já alugados nesse período
    brinquedos_ocupados_ids = locacoes_conflitantes.values_list(
        'brinquedos__id', flat=True)

    # Filtrar os brinquedos disponíveis
    brinquedos_disponiveis = Brinquedo.objects.exclude(
        id__in=brinquedos_ocupados_ids)

    serializer = BrinquedoSerializer(brinquedos_disponiveis, many=True)
    brinquedos = Brinquedo.objects.all()
    data = [
        {
            "id": b.id,
            "nome": b.nome,
            "quantidade": b.quantidade,
            "valor_unitario": float(b.valor_unitario),  # <-- Adicionado aqui
        }
        for b in brinquedos
    ]
    return Response(serializer.data)


class LocacoesHojeView(APIView):
    def get(self, request):
        queryset = Locacao.objects.all()
        serializer = LocacaoSerializer(queryset, many=True)
        return Response(serializer.data)
    
class LocacoesViewSet(viewsets.ModelViewSet):
    queryset = Locacao.objects.all().order_by('data_festa')
    serializer_class = LocacaoSerializer
    

class LocacaoCreateView(generics.CreateAPIView):
    queryset = Locacao.objects.all()
    serializer_class = LocacaoSerializer
    

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    

class ClienteCreateView(generics.CreateAPIView):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    

class ClienteDetailUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    

class FestaDetailUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
  
