from urllib import request as url_request
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from .models import Cliente, Brinquedo, Locacao, ContratoAnexo, Transacoes
from .serializers import ClienteSerializer, BrinquedoSerializer, LocacaoSerializer, ContratoAnexoSerializer, TransacoesSerializer
from xhtml2pdf import pisa
from decimal import Decimal
from datetime import datetime, date
from django.utils.text import slugify
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Sum, Count, F, Q, DecimalField, CharField
from django.db.models.functions import Coalesce, TruncMonth
from dateutil.relativedelta import relativedelta
from .models import Convite, Profile
from .serializers import ConviteSerializer

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def LoginCreateAPIView(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'error': 'Email e senha são obrigatórios'}, status=400)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Usuário ou senha inválidos'}, status=401)

    user = authenticate(username=user.username, password=password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        # pega a organização do profile do usuário
        organization_id = user.profile.organization.id
        return Response({
            'token': token.key,
            'organization_id': organization_id
        })

    return Response({'error': 'Usuário ou senha inválidos'}, status=401)


class InviteUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Garante que apenas um admin pode convidar
        if not request.user.profile or request.user.profile.role != 'admin':
            return Response(
                {"erro": "Apenas administradores podem convidar usuários."},
                status=status.HTTP_403_FORBIDDEN
            )

        email = request.data.get('email')
        if not email:
            return Response({"erro": "O email é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

        # Verifica se já existe um usuário com este email
        User = get_user_model()
        if User.objects.filter(email=email).exists():
            return Response({"erro": "Um usuário com este email já existe."}, status=status.HTTP_400_BAD_REQUEST)

        organization = request.user.profile.organization

        # Cria o convite
        convite = Convite.objects.create(
            email=email, organization=organization)

        # TODO: Enviar um e-mail para o usuário convidado
        # Aqui você adicionaria a lógica para enviar um e-mail com o link do convite.
        # Exemplo do link: https://happykidsmr.netlify.app/registrar-convite/{convite.token}
        print(
            f"Link do convite para {email}: /registrar-convite/{convite.token}")

        return Response(
            {"sucesso": "Convite enviado com sucesso.", "token": convite.token},
            status=status.HTTP_201_CREATED
        )


# NOVA VIEW PARA O NOVO USUÁRIO ACEITAR O CONVITE E SE CADASTRAR
class AcceptInviteAPIView(APIView):
    permission_classes = [AllowAny]  # Permite acesso para usuários não logados

    def post(self, request, *args, **kwargs):
        token = request.data.get('token')
        username = request.data.get('username')
        password = request.data.get('password')

        if not all([token, username, password]):
            return Response(
                {"erro": "Token, username e password são obrigatórios."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Encontra o convite
        try:
            convite = Convite.objects.get(token=token, aceito=False)
        except Convite.DoesNotExist:
            return Response({"erro": "Convite inválido ou já utilizado."}, status=status.HTTP_404_NOT_FOUND)

        # Cria o novo usuário
        User = get_user_model()
        if User.objects.filter(username=username).exists():
            return Response({"erro": "Este nome de usuário já está em uso."}, status=status.HTTP_400_BAD_REQUEST)

        novo_usuario = User.objects.create_user(
            username=username,
            email=convite.email,
            password=password
        )

        # O signal 'create_user_profile' já criou o Profile. Agora vamos atualizá-lo.
        profile = novo_usuario.profile
        profile.organization = convite.organization
        profile.role = 'membro'
        profile.save()

        # Marca o convite como utilizado
        convite.aceito = True
        convite.save()

        return Response({"sucesso": "Usuário registrado com sucesso!"}, status=status.HTTP_201_CREATED)


# Cliente API
# Lista todos os clientes ou cria um novo
class ClienteListCreateAPIView(APIView):
    def get(self, request):
        org = request.user.profile.organization
        clientes = Cliente.objects.filter(organization=org)
        serializer = ClienteSerializer(clientes, many=True)
        return Response(serializer.data)

    def post(self, request):
        org = request.user.profile.organization
        serializer = ClienteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(organization=org)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Lista só os clientes com status "ativo"
class ClientesAtivosAPIView(APIView):
    def get(self, request):
        org = request.user.profile.organization
        clientes = Cliente.objects.filter(status='ativo', organization=org)
        serializer = ClienteSerializer(clientes, many=True)
        return Response(serializer.data)


# Detalhe, edição e exclusão de cliente específico
class ClienteDetailAPIView(APIView):
    def get(self, request, id):
        cliente = get_object_or_404(
            Cliente, id=id, organization=request.user.profile.organization)
        serializer = ClienteSerializer(cliente)
        return Response(serializer.data)

    def put(self, request, id):
        org = request.user.profile.organization
        cliente = get_object_or_404(
            Cliente, id=id, organization=request.user.profile.organization)
        serializer = ClienteSerializer(cliente, data=request.data)
        if serializer.is_valid():
            serializer.save(organization=org)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        cliente = get_object_or_404(
            Cliente, id=id, organization=request.user.profile.organization)
        cliente.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Brinquedos
# Lista todos os brinquedos ou cria um novo
class BrinquedoListCreateAPIView(APIView):
    def get(self, request):
        org = request.user.profile.organization
        brinquedos = Brinquedo.objects.filter(organization=org)
        serializer = BrinquedoSerializer(brinquedos, many=True)
        return Response(serializer.data)

    def post(self, request):
        org = request.user.profile.organization
        serializer = BrinquedoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(organization=org)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Detalhe, edição e exclusão de brinquedo específico
class BrinquedoDetailAPIView(APIView):
    def get(self, request, id):
        brinquedo = get_object_or_404(
            Brinquedo, id=id, organization=request.user.profile.organization)
        serializer = BrinquedoSerializer(brinquedo)
        return Response(serializer.data)

    def put(self, request, id):
        org = request.user.profile.organization
        brinquedo = get_object_or_404(
            Brinquedo, id=id, organization=request.user.profile.organization)
        serializer = BrinquedoSerializer(brinquedo, data=request.data)
        if serializer.is_valid():
            serializer.save(organization=org)
            return Response(serializer.data)
        return Response({"erro": "Dados inválidos"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        brinquedo = get_object_or_404(
            Brinquedo, id=id, organization=request.user.profile.organization)
        brinquedo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
        org = request.user.profile.organization
        locacoes_conflitantes = Locacao.objects.filter(
            organization=org,
            data_festa__lte=data_desmontagem,
            data_desmontagem__gte=data_festa
        ).prefetch_related('brinquedos')

        # Coleta os IDs dos brinquedos já locados
        ids_indisponiveis = set()
        for loc in locacoes_conflitantes:
            ids_indisponiveis.update(
                loc.brinquedos.values_list('id', flat=True))

        # Filtra brinquedos que NÃO estão nesses IDs
        brinquedos_disponiveis = Brinquedo.objects.filter(
            organization=org
        ).exclude(id__in=ids_indisponiveis)
        serializer = BrinquedoSerializer(brinquedos_disponiveis, many=True)
        return Response(serializer.data)


# Locações
# Lista todas as locações ou cria uma nova
class LocacoesListCreateAPIView(APIView):
    def get(self, request):
        org = request.user.profile.organization
        locacoes = Locacao.objects.filter(
            organization=org).order_by('data_festa')
        serializer = LocacaoSerializer(locacoes, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.data.get("data_festa") > request.data.get("data_desmontagem"):
            return Response({"erro": "A data da festa não pode ser posterior à data de desmontagem."}, status=400)

        org = request.user.profile.organization
        serializer = LocacaoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(organization=org)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_destroy(self, instance):
        # Cancela ou exclui a transação associada antes de excluir a locação
        transacao = Transacoes.objects.filter(
            locacao=instance,
            origem="locacao"
        ).first()
        if transacao:
            # opção 1: cancelar a transação
            transacao.status = "cancelado"
            transacao.descricao += " (Cancelada junto com a locação)"
            transacao.save()

            # opção 2 (se preferir excluir a transação):
            # transacao.delete()

        # agora remove a locação
        instance.delete()


# Detalhe, edição e exclusão de locação específico
class LocacoesDetailAPIView(APIView):
    # Busca a locação ou retorna None
    def get_object(self, id):
        try:
            return Locacao.objects.get(id=id, organization=self.request.user.profile.organization)
        except Locacao.DoesNotExist:
            return None

    def get(self, request, id):
        locacao = self.get_object(id)
        if not locacao:
            return Response({'erro': 'Locação não encontrada'}, status=404)
        serializer = LocacaoSerializer(locacao)
        return Response(serializer.data)

    def put(self, request, id):
        org = request.user.profile.organization
        locacao = self.get_object(id)
        if not locacao:
            return Response({'erro': 'Locação não encontrada'}, status=404)
        serializer = LocacaoSerializer(locacao, data=request.data)
        if serializer.is_valid():
            serializer.save(organization=org)
            return Response(serializer.data)
        return Response({'erro': 'Dados inválidos'}, status=400)

    def patch(self, request, id):
        org = request.user.profile.organization
        locacao = self.get_object(id)
        if not locacao:
            return Response({'erro': 'Locação não encontrada'}, status=404)

        # Pega dados recebidos
        data = request.data.copy()

        novo_pagamento = data.get("pagamento")
        status_atual = locacao.status

        # Regras de atualização de status com base no pagamento
        if novo_pagamento == "nao_pago":
            data["status"] = "pendente"
        elif novo_pagamento in ["entrada", "pago"]:
            if status_atual == "pendente":
                data["status"] = "confirmado"
            else:
                data["status"] = status_atual  # mantém o mesmo

        # Usa partial=True para não exigir todos os campos obrigatórios
        serializer = LocacaoSerializer(locacao, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(organization=org)
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, id):
        locacao = self.get_object(id=id)
        if not locacao:
            return Response({'erro': 'Locação não encontrada'}, status=404)

        # Aqui é o lugar certo para cancelar a transação automática
        transacao = Transacoes.objects.filter(
            locacao=locacao,
            origem='locacao'
        ).first()
        if transacao:
            # Opção 1: marcar como cancelado
            transacao.status = 'cancelado'
            transacao.descricao += " (Cancelada junto com a locação)"
            transacao.save()

            # Opção 2 (menos recomendada): deletar a transação
            # transacao.delete()

        # Deleta a locação
        locacao.delete()
        return Response(status=204)

# Atualiza o status da locação ID


class LocacoesStatusUpdateAPIView(APIView):
    def patch(self, request, id):
        try:
            locacao = Locacao.objects.get(
                id=id, organization=self.request.user.profile.organization)
        except Locacao.DoesNotExist:
            return Response({'erro': 'Locação não encontrada'}, status=404)

        novo_status = request.data.get('status')
        if novo_status not in ['pendente', 'confirmado', 'montado', 'recolher', 'finalizado']:
            return Response({'erro': 'Status inválido'}, status=400)

        locacao.status = novo_status
        locacao.save()
        return Response({"mensagem": "Status atualizado com sucesso"}, status=200)


# Contrato PDF
# Gera o PDF do contrato da locação
class ContratoLocacaoPDFView(APIView):
    def get(self, request, locacao_id):
        try:
            locacao = Locacao.objects.select_related(
                'cliente').get(id=locacao_id, organization=request.user.profile.organization)
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
            response['Content-Disposition'] = f'attachment; filename="Contrato-{slugify(locacao.cliente.nome)}.pdf"'

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


# Transações
class TransacoesListCreateAPIView(APIView):
    def get(self, request):
        org = request.user.profile.organization
        transacoes = Transacoes.objects.filter(
            organization=org).order_by('-data_transacao')
        serializer = TransacoesSerializer(transacoes, many=True)
        return Response(serializer.data)

    def post(self, request):
        org = request.user.profile.organization
        data = request.data.copy()
        data["organization"] = org.id
        parcelado = data.get("parcelado", "nao")
        qtd_parcelas = int(data.get("qtd_parcelas") or 1)

        # Caso parcelado = sim → cria várias
        if parcelado == "sim" and qtd_parcelas > 1:
            valor_total = Decimal(data["valor"])
            valor_parcela = (
                valor_total / qtd_parcelas).quantize(Decimal("0.01"))

            primeira_data = datetime.strptime(
                data["data_transacao"], "%Y-%m-%d").date()
            referencia_id = None
            transacoes_criadas = []

            for i in range(1, qtd_parcelas + 1):
                data_parcela = primeira_data + relativedelta(months=i-1)

                transacao = Transacoes.objects.create(
                    organization=org,
                    cliente_id=data.get("cliente"),
                    locacao_id=data.get("locacao"),
                    brinquedo_id=data.get("brinquedo"),
                    data_transacao=data_parcela,
                    tipo=data["tipo"],
                    valor=valor_parcela,
                    categoria=data["categoria"],
                    pagamento=data["pagamento"],
                    forma_pagamento=data.get("forma_pagamento"),
                    descricao=f"{data.get('descricao', '')} - Parcela {i}/{qtd_parcelas}",
                    parcelado="sim",
                    origem=data.get("origem", "manual"),
                    qtd_parcelas=qtd_parcelas,
                    parcela_atual=i,
                    referencia_id=referencia_id
                )

                # define referencia_id na primeira e atualiza
                if referencia_id is None:
                    referencia_id = transacao.id
                    transacao.referencia_id = referencia_id
                    serializer.save(organization=org)

                transacoes_criadas.append(transacao)

            return Response(
                {"message": "Transações parceladas criadas com sucesso",
                 "ids": [t.id for t in transacoes_criadas]},
                status=status.HTTP_201_CREATED
            )

        # Caso comum (não parcelado)
        serializer = TransacoesSerializer(data=data)
        if serializer.is_valid():
            serializer.save(organization=org)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransacoesDetailAPIView(APIView):
    def get(self, request, id):
        transacao = get_object_or_404(
            Transacoes, id=id, organization=request.user.profile.organization)
        serializer = TransacoesSerializer(transacao)
        return Response(serializer.data)

    def put(self, request, id):
        transacao = get_object_or_404(
            Transacoes, id=id, organization=request.user.profile.organization)
        serializer = TransacoesSerializer(transacao, data=request.data)
        if serializer.is_valid():
            serializer.save(organization=request.user.profile.organization)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        transacao = get_object_or_404(Transacoes, id=id, organization=request.user.profile.organization)
        transacao.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DashboardAPIView(APIView):
    """
    Endpoint único que calcula e retorna todas as estatísticas
    necessárias para o dashboard.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        org = request.user.profile.organization
        hoje = date.today()

        # --- SEÇÃO 1: CÁLCULOS GERAIS PARA OS STAT CARDS ---
        investimento_total = Brinquedo.objects.filter(organization=org).aggregate(
            total=Coalesce(Sum('valor_compra'), Decimal(
                '0.00'), output_field=DecimalField())
        )['total']

        receita_acumulada = Transacoes.objects.filter(
            organization=org, tipo='entrada', pagamento__in=['pago', 'entrada']
        ).aggregate(
            total=Coalesce(Sum('valor'), Decimal('0.00'),
                           output_field=DecimalField())
        )['total']

        despesa_total = Transacoes.objects.filter(
            organization=org, tipo='saida', pagamento='pago'
        ).aggregate(
            total=Coalesce(Sum('valor'), Decimal('0.00'),
                           output_field=DecimalField())
        )['total']

        roi_global = Decimal('0.00')
        if investimento_total > 0:
            lucro = receita_acumulada - despesa_total
            roi_global = (lucro / investimento_total) * 100

        # --- SEÇÃO 2: CÁLCULOS POR BRINQUEDO (PARA AS DUAS TABELAS) ---
        roi_por_brinquedo = []
        previsao_break_even = []  # Lista para a segunda tabela

        brinquedos = Brinquedo.objects.filter(organization=org)
        for brinquedo in brinquedos:
            # --- Bloco de cálculo para ROI ---
            receita_brinquedo = Transacoes.objects.filter(
                locacao__brinquedos=brinquedo, tipo='entrada', pagamento__in=['pago', 'entrada']
            ).aggregate(total=Coalesce(Sum('valor'), Decimal('0.00')))['total']

            manutencao_brinquedo = Transacoes.objects.filter(
                brinquedo=brinquedo, tipo='saida', categoria='manutencao', pagamento='pago'
            ).aggregate(total=Coalesce(Sum('valor'), Decimal('0.00')))['total']

            investimento = brinquedo.valor_compra or Decimal('0.00')
            custo_total_brinquedo = investimento + manutencao_brinquedo

            roi_brinquedo = Decimal('0.00')
            if custo_total_brinquedo > 0:
                lucro_brinquedo = receita_brinquedo - custo_total_brinquedo
                roi_brinquedo = (lucro_brinquedo / custo_total_brinquedo) * 100

            roi_por_brinquedo.append({
                'id': brinquedo.id, 'nome': brinquedo.nome, 'valor_compra': investimento,
                'manutencao_acumulada': manutencao_brinquedo, 'receita_acumulada': receita_brinquedo,
                'roi_percentual': roi_brinquedo, 'status': brinquedo.get_status_display(),
            })

            # --- Bloco de cálculo para BREAK-EVEN ---
            primeira_locacao = Locacao.objects.filter(
                brinquedos=brinquedo).order_by('data_festa').first()
            receita_mensal_media = Decimal('0.00')
            if primeira_locacao:
                meses_operacao = (hoje.year - primeira_locacao.data_festa.year) * \
                    12 + hoje.month - primeira_locacao.data_festa.month + 1
                if meses_operacao > 0:
                    receita_mensal_media = receita_brinquedo / meses_operacao

            previsao_payback_str = "N/A"
            if custo_total_brinquedo > receita_brinquedo:
                if receita_mensal_media > 0:
                    valor_faltante = custo_total_brinquedo - receita_brinquedo
                    meses_faltantes = valor_faltante / receita_mensal_media
                    previsao_payback_str = f"{meses_faltantes:.1f} meses"
                else:
                    previsao_payback_str = "Nunca (sem receita)"
            else:
                previsao_payback_str = "Já pago"

            previsao_break_even.append({
                'id': brinquedo.id, 'nome': brinquedo.nome, 'investimento_total': custo_total_brinquedo,
                'receita_mensal_media': receita_mensal_media, 'receita_acumulada_atual': receita_brinquedo,
                'previsao_payback': previsao_payback_str,
            })

        # --- SEÇÃO 3: CÁLCULOS PARA OS GRÁFICOS ---

        # Gráfico 'Receita x Despesa'
        transacoes_por_mes = Transacoes.objects.filter(
            organization=org, pagamento__in=['pago', 'entrada']
        ).annotate(mes=TruncMonth('data_transacao')).values('mes').annotate(
            receita=Coalesce(Sum('valor', filter=Q(
                tipo='entrada')), Decimal('0.00')),
            despesa=Coalesce(
                Sum('valor', filter=Q(tipo='saida')), Decimal('0.00'))
        ).order_by('mes')
        chart_receita_despesa = [{'mes': i['mes'].strftime('%b/%Y'), 'Receita': float(
            i['receita']), 'Despesa': float(i['despesa'])} for i in transacoes_por_mes]

        # Gráfico 'Brinquedos mais alugados'
        ranking_brinquedos = Brinquedo.objects.filter(organization=org).annotate(
            total_alugueis=Count('locacao')).filter(total_alugueis__gt=0).order_by('-total_alugueis')[:5]
        chart_ranking_brinquedos = [
            {'nome': b.nome, 'Aluguéis': b.total_alugueis} for b in ranking_brinquedos]

        # Gráfico 'Despesas por categoria'
        despesas_por_categoria = Transacoes.objects.filter(organization=org, tipo='saida', pagamento='pago').values(
            'categoria').annotate(total=Sum('valor')).order_by('-total')
        categoria_choices = dict(Transacoes.CATEGORIA_CHOICES)
        chart_despesas_categoria = [{'name': categoria_choices.get(
            i['categoria'], i['categoria']), 'value': float(i['total'])} for i in despesas_por_categoria]

        # Gráfico 'Saldo acumulado'
        transacoes_ordenadas = Transacoes.objects.filter(
            organization=org, pagamento__in=['pago', 'entrada']).order_by('data_transacao')
        saldo_atual, saldo_por_mes = Decimal('0.00'), {}
        for transacao in transacoes_ordenadas:
            saldo_atual += transacao.valor if transacao.tipo == 'entrada' else -transacao.valor
            saldo_por_mes[transacao.data_transacao.strftime(
                '%Y-%m')] = saldo_atual
        chart_saldo_acumulado = [{'mes': date(int(mes_ano.split('-')[0]), int(mes_ano.split('-')[1]), 1).strftime(
            '%b/%Y'), 'Saldo': float(saldo)} for mes_ano, saldo in sorted(saldo_por_mes.items())]

        # Gráfico 'Receita por brinquedo'
        receita_por_brinquedo_query = Brinquedo.objects.filter(organization=org).annotate(
            total_receita=Coalesce(Sum('locacao__transacoes__valor', filter=Q(
                locacao__transacoes__tipo='entrada', locacao__transacoes__pagamento__in=['pago', 'entrada'])), Decimal('0.00'))
        ).filter(total_receita__gt=0).order_by('-total_receita')[:10]
        chart_receita_brinquedo = [{'nome': b.nome, 'Receita': float(
            b.total_receita)} for b in receita_por_brinquedo_query]

        # --- SEÇÃO 4: MONTAR RESPOSTA FINAL ---
        data = {
            'stat_cards': {
                'investimento_total': investimento_total,
                'receita_acumulada': receita_acumulada,
                'roi_global': roi_global,
            },
            'tabela_roi_brinquedo': roi_por_brinquedo,
            'tabela_break_even': previsao_break_even,  # Adicionada!
            'chart_receita_despesa': chart_receita_despesa,
            'chart_ranking_brinquedos': chart_ranking_brinquedos,
            'chart_despesas_categoria': chart_despesas_categoria,
            'chart_saldo_acumulado': chart_saldo_acumulado,
            'chart_receita_brinquedo': chart_receita_brinquedo,
        }

        return Response(data)
