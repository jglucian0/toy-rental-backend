from django.template.loader import render_to_string
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser
from .models import Cliente, Brinquedo, Locacao, ContratoAnexo
from .serializers import ClienteSerializer, BrinquedoSerializer, LocacaoSerializer, ContratoAnexoSerializer
from xhtml2pdf import pisa
from decimal import Decimal
from datetime import datetime, date

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


# Lista todos os brinquedos disponíveis baseado na data
class BrinquedosDisponiveisAPIView(APIView):
    def get(self, request):
        data_festa = request.GET.get('data_festa')
        data_desmontagem = request.GET.get('data_desmontagem')

        if not data_festa or not data_desmontagem:
            return Response({"erro": "As datas são obrigatórias."}, status=400)

        try:
            data_festa = datetime.strptime(
                data_festa, "%Y-%m-%d").date()
            data_desmontagem = datetime.strptime(
                data_desmontagem, "%Y-%m-%d").date()
        except ValueError:
            return Response({"erro": "Formato de data inválido."}, status=400)

        # Busca os brinquedos que já estão locados nesse período
        locacoes_conflitantes = Locacao.objects.filter(
            data_festa__lte=data_desmontagem,
            data_desmontagem__gte=data_festa
        ).prefetch_related('brinquedos')

        # Coleta os IDs dos brinquedos já locados
        ids_indisponiveis = set()
        for loc in locacoes_conflitantes:
            ids_indisponiveis.update(
                loc.brinquedos.values_list('id', flat=True))

        # Filtra brinquedos que NÃO estão nesses IDs
        brinquedos_disponiveis = Brinquedo.objects.exclude(
            id__in=ids_indisponiveis)
        serializer = BrinquedoSerializer(brinquedos_disponiveis, many=True)
        return Response(serializer.data)


# Locações
# Lista todas as locações ou cria uma nova
class LocacoesListCreateAPIView(APIView):
    def get(self, request):
        locacoes = Locacao.objects.all().order_by('data_festa')
        serializer = LocacaoSerializer(locacoes, many=True)
        return Response(serializer.data)

    def post(self, request):
        locacoes = LocacaoSerializer(data=request.data)
        if locacoes.is_valid():
            locacoes.save()
            return Response(locacoes.data, status=status.HTTP_201_CREATED)
        return Response(locacoes.errors, status=status.HTTP_400_BAD_REQUEST)


# Detalhe, edição e exclusão de locação específico
class LocacoesDetailAPIView(APIView):
    # Busca a locação ou retorna None
    def get_object(self, id):
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


# Atualiza o status da locação ID
class LocacoesStatusUpdateAPIView(APIView):
    def patch(self, request, id):
        try:
            festa = Locacao.objects.get(id=id)
        except Locacao.DoesNotExist:
            return Response({'erro': 'Locação não encontrada'}, status=404)

        novo_status = request.data.get('status')
        if novo_status not in ['pendente', 'confirmado', 'montado', 'recolher', 'finalizado']:
            return Response({'erro': 'Status inválido'}, status=400)

        festa.status = novo_status
        festa.save()
        return Response({"mensagem": "Status atualizado com sucesso"}, status=200)


# Contrato PDF
# Gera o PDF do contrato da locação
class ContratoLocacaoPDFView(APIView):
    def get(self, request, locacao_id):
        try:
            locacao = Locacao.objects.select_related(
                'cliente').get(id=locacao_id)
            brinquedos = locacao.brinquedos.all()
            brinquedo_nomes = ", ".join([b.nome for b in brinquedos])

            # Valores seguros
            acrescimos = locacao.acrescimos or Decimal("0.00")
            descontos = locacao.descontos or Decimal("0.00")

            # Soma dos brinquedos
            valor_brinquedos = sum([b.valor_diaria for b in brinquedos])

            # Total final
            total = valor_brinquedos + acrescimos - descontos

            context = {
                "cliente_nome": locacao.cliente.nome,
                "cliente_cpf": locacao.cliente.documento,
                "brinquedos": brinquedo_nomes,
                "endereco": locacao.endereco,
                "numero": locacao.numero,
                "complemento": locacao.complemento or "",
                "data_evento": locacao.data_festa.strftime("%d/%m/%Y"),

                # Valores formatados
                "valor_brinquedos": f"{valor_brinquedos:.2f}",
                "acrescimos": f"{acrescimos:.2f}",
                "descontos": f"{descontos:.2f}",
                "total": f"{total:.2f}",

                # Parcelas
                "valor_30": f"{total * Decimal('0.3'):.2f}",
                "valor_70": f"{total * Decimal('0.7'):.2f}",
                "data_hoje": date.today().strftime("%d/%m/%Y"),
            }

            html = render_to_string("contrato.html", context)
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="Contrato-{locacao.cliente.nome}.pdf"'

            pisa_status = pisa.CreatePDF(html, dest=response)

            if pisa_status.err:
                return HttpResponse("Erro ao gerar PDF", status=500)
            return response

        except Locacao.DoesNotExist:
            return Response({"erro": "Festa não encontrada"}, status=status.HTTP_404_NOT_FOUND)


# Anexo do contrato de locação
class ContratoAnexoAPIView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser]

    def get(self, request, locacao_id):
        try:
            anexo = ContratoAnexo.objects.get(locacao_id=locacao_id)
            serializer = ContratoAnexoSerializer(
                anexo, context={"request": request})
            return Response(serializer.data)
        except ContratoAnexo.DoesNotExist:
            return Response({"erro": "Anexo não encontrado"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, locacao_id):
        try:
            anexo, created = ContratoAnexo.objects.get_or_create(
                locacao_id=locacao_id)
            arquivo = request.FILES.get("arquivo")
            if not arquivo:
                return Response({"erro": "Arquivo não enviado."}, status=400)
            anexo.arquivo = arquivo
            anexo.save()
            return Response({"mensagem": "Anexo salvo com sucesso"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"erro": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, locacao_id):
        try:
            anexo = ContratoAnexo.objects.get(locacao_id=locacao_id)
            anexo.arquivo.delete()
            anexo.delete()
            return Response({"mensagem": "Anexo excluído com sucesso"}, status=status.HTTP_204_NO_CONTENT)
        except ContratoAnexo.DoesNotExist:
            return Response({"erro": "Anexo não encontrado"}, status=status.HTTP_404_NOT_FOUND)
