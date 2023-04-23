from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.db.models import F, Sum
from core.models import Dados, Operations, NoPrazo, Atrasados, Obras, Insumos, Indeterminados, DadosAjuCard, DadosRH
from .forms import FiltroForm, UploadForm, AddInsumoForm, UploadRH
from datetime import datetime, timedelta
import pandas as pd
import tempfile, os


# Create your views here.
def calcular_pagar(cpf):
    try:
        # Obtendo os objetos que possuem o mesmo CPF nas duas tabelas
        obj_aju_card = DadosAjuCard.objects.get(cpf=cpf)
        obj_rh = DadosRH.objects.get(cpf=cpf)

        # Calculando o valor a pagar
        mult_valor_dias = ((obj_rh.valor/100) * obj_rh.dias_trabalhados)
        
        sub_valor_dias = (float(mult_valor_dias) - float(obj_aju_card.total))
        pagar = max(sub_valor_dias, 0)

    except (DadosRH.DoesNotExist, DadosAjuCard.DoesNotExist):
        pagar = None

    return pagar

def upload(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            arquivo = request.FILES['arquivo']
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                for chunk in arquivo.chunks():
                    tmp.write(chunk)
            dados_xls = pd.read_excel(tmp.name)
            os.unlink(tmp.name)
            salvar_dados(dados_xls)
            return(redirect('graphic'))

        else:
            return(redirect('upload-page-obras'))
    else:
        return(redirect('upload-page-obras'))

def upload_rh(request):
    if request.method == 'POST':
        form = UploadRH(request.POST, request.FILES)
        if form.is_valid():
            arquivo1 = request.FILES['arquivo1']
            arquivo2 = request.FILES['arquivo2']
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                for chunk in arquivo1.chunks():
                    tmp.write(chunk)
            dados_xls = pd.read_excel(tmp.name, dtype={'CPF': str})
            os.unlink(tmp.name)
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                for chunk in arquivo2.chunks():
                    tmp.write(chunk)
            dados_xls2 = pd.read_excel(tmp.name)
            os.unlink(tmp.name)

            dados_rh(dados_xls, dados_xls2)
            return(redirect('results-rh'))
        else:
            return(redirect('upload-page-rh'))
    else:
        return(redirect('upload-page-rh'))
    
def dados_rh(dados_xls, dados_xls2):
    #dados_xls = planilha Real
    #dados_xls2 = planilha aracajucard
    for index, row in dados_xls.iterrows():
        if str(row['CPF']) != 'nan':
            cpf = row['CPF']
            if str(row['Dias']) != 'nan':
                dias_trabalhados = row['Dias']
            if str(row['Valor']) != 'nan':
                valor = row['Valor']
            if str(row['Nome']) != 'nan':
                nome = row['Nome']
            real_vt = DadosRH(cpf=cpf, dias_trabalhados=dias_trabalhados, valor=valor, nome=nome)
            real_vt.save()
    

    for index, row in dados_xls2.iterrows():
        #1 CPF, 5 Nome, 8 Cartão, 9 SaldoA, 10 Saldo, 12 Total_saldo, 16 Recarga, 19 Total 
        if index > 10:
            if isinstance(row[1], str) and str(row[1]) != 'Total:':
                cpf2 = row[1]
                if isinstance(row[5], str):
                    nome2 = row[5]
                if isinstance(row[8], str):
                    cartao = str(row[8])
                if isinstance(row[9], int) or isinstance(row[9], float) and str(row[9]) != 'nan':
                    saldoA = float(row[9])
                if isinstance(row[10], int) or isinstance(row[10], float) and str(row[10]) != 'nan':
                    saldo = float(row[10])
                if isinstance(row[12], int) or isinstance(row[12], float) and str(row[12]) != 'nan':
                    total_saldo = float(row[12])
                if isinstance(row[16], int) or isinstance(row[16], float) and str(row[16]) != 'nan':
                    recarga = float(row[16])
                if isinstance(row[19], int) or isinstance(row[19], float) and str(row[19]) != 'nan':
                    total = float(row[19])

                dados_aju_card = DadosAjuCard(cpf=cpf2, nome=nome2, cartao=cartao, saldoA=saldoA, saldo=saldo, total_saldo=total_saldo, recarga=recarga, total=total)
                dados_aju_card.save()
                try:
                    dadorh = DadosRH.objects.get(pk=cpf2)
                    dadorh.total = total
                    dadorh.save()
                except DadosRH.DoesNotExist:
                    pass

    dados =DadosRH.objects.all()   
    for dado in dados:
        obj_rh = DadosRH.objects.get(pk=dado.cpf)
        obj_rh.pagar = calcular_pagar(dado.cpf)
        obj_rh.save()
                 
def results_rh(request):
    return render(request, 'results-rh.html', {'reais':DadosRH.objects.all(), 'Ajucards': DadosAjuCard.objects.all()})

def download_table(request):
# Obtenha os dados que deseja incluir na tabela
    reais = DadosRH.objects.all()
    
    # Converta os dados em um dataframe do pandas
    df = pd.DataFrame(list(reais.values('cpf', 'nome', 'dias_trabalhados', 'pagar', 'total')))
    
    # Altere o índice das colunas para nomes mais descritivos
    df.columns = ['CPF', 'Nome', 'Dias', 'Valor a pagar', 'Saldo']
    
    # Crie o arquivo xls
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Planilha VT.xls"'
    
    # Use a biblioteca xlsxwriter para ajustar o tamanho das colunas
    writer = pd.ExcelWriter(response, engine='xlsxwriter')
    df.to_excel(writer, index=False)
    
    worksheet = writer.sheets['Sheet1']  # o nome da planilha pode ser diferente
    
    # iterar sobre cada coluna
    for i, col in enumerate(df.columns):
        # encontre o tamanho máximo de um item na coluna, incluindo o título da coluna
        max_width = max(len(str(col)), df[col].astype(str).map(len).max())
        # ajuste o tamanho da coluna para o tamanho máximo + 1 para uma margem
        worksheet.set_column(i, i, max_width + 1)
    
    writer.save()
    
    return response
    
def download_txt(request):
    
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="Planilha TXT.txt"'

    reais = DadosRH.objects.all()

    response.write('CPF|Dias|Valor a pagar|Saldo|Nome\n\n\n')

    for real in reais:
        response.write('{0}|{1}|{2}|{3}|{4}\n'.format(
            real.cpf,
            real.dias_trabalhados,
            real.pagar,
            real.total,
            real.nome,
        ))

    return response

def format_date(indice):
    if isinstance(indice, str):
        try:
            date = datetime.strptime(indice, "%d/%m/%Y").date()
        except ValueError:
            date = None
    else:
        date = None
    return date

def salvar_dados(dados_xls):
    numero = []    
    insumos = Insumos.objects.all()
    atrasado = []
    noprazo = []
    
    for index, row in dados_xls.iterrows():
        data_prev_final = None
        if index > 5:
            if str(row[0]) != 'nan':
                if isinstance(row[0] , int):
                    item = row[0]
                else:
                    item = None
            else:
                item = None

            if str(row[1]) != 'nan':
                if isinstance(row[1], int):
                    cod_sol_compra = row[1] 
                else:
                    cod_sol_compra = None                    
            else:                
                cod_sol_compra = None
            
            if str(row[2]) != 'nan':
                if isinstance(row[2], int):
                    cod_obra = row[2]
                else:
                    cod_obra = None
            else:
                cod_obra = None

            if str(row[4]) != 'nan':
                if isinstance(row[4], int):
                    cod_insumo = row[4]
                else:
                    cod_insumo = None
            else:
                cod_insumo = None

            if str(row[5]) != 'nan':
                if isinstance(row[5], str):
                    desc_insumo = row[5]
                else:
                    desc_insumo = None
            else:
                desc_insumo = None

            if str(row[8]) != 'nan':
                quant_sol = str(row[8])
            else:
                quant_sol = None
            
            if str(row[10]) != 'nan':
                if isinstance(row[10], str):
                    data_sol = row[10]
                else:
                    data_sol = None
            else:
                data_sol = None

            if str(row[11]) != 'nan':
                if isinstance(row[11], str):
                    data_sol_cheg_obra = row[11]
                else:
                    data_sol_cheg_obra = None
            else:
                data_sol_cheg_obra = None
            
            if str(row[12]) != 'nan':
                if isinstance(row[12], int):
                    num_ped_compra = row[12]
                else:
                    num_ped_compra = None
            else:
                num_ped_compra = None

            
            if str(row[13]) != 'nan':
                if isinstance(row[13], str):
                    data_emissao_pc = row[13]
                else:   
                    data_emissao_pc = None
            else:
                data_emissao_pc = None


            if str(row[14]) != 'nan':
                if isinstance(row[14], str):
                    prev_entrega = row[14]
                else:
                    prev_entrega = None
            else:
                prev_entrega = None


            if str(row[16]) != 'nan':
                quant_entregue = str(row[16])
            else:
                quant_entregue = None

            if str(row[18]) != 'nan':
                saldo = str(row[18])
            else:
                saldo = None

            if str(row[19]) != 'nan':
                if isinstance(row[19], str):
                    data_NF = row[19]
                else:
                    data_NF = None
            else:
                data_NF = None

            if str(row[20]) != 'nan':
                if isinstance(row[20], str):
                    cod_NF = row[20]
                else:
                    cod_NF = None
            else:
                cod_NF = None

            if str(row[21]) != 'nan':
                if isinstance(row[21], str):
                    data_entrada_obra = row[21]
                else:
                     data_entrada_obra = None
            else:
                 data_entrada_obra = None
            
            if str(row[22]) != 'nan':
                if isinstance(row[22], str):
                    data_vencimento = row[22]
                else:
                    data_vencimento =  None
            else:                    
                data_vencimento =  None
            
            if insumos.exists():
                for insumo in insumos:
                    if cod_insumo and data_emissao_pc and insumo.qtd_dias and insumo.codigo_insumo:
                        if insumo.codigo_insumo == cod_insumo:
                            data_prev_final = format_date(data_emissao_pc)+timedelta(days=insumo.qtd_dias)
                        else:
                            data_prev_final = format_date(prev_entrega)
                    else:
                        data_prev_final = format_date(prev_entrega)
            else:
                data_prev_final = format_date(prev_entrega)
            
            dados = Dados(item=item, 
                      cod_sol_compra=cod_sol_compra, 
                      cod_obra=cod_obra, cod_insumo=cod_insumo, 
                      desc_insumo=desc_insumo, 
                      num_ped_compra=num_ped_compra, 
                      data_emissao_pc=(format_date(data_emissao_pc)),
                      quant_sol=quant_sol,
                      data_sol=(format_date(data_sol)),
                      data_sol_cheg_obra=(format_date(data_sol_cheg_obra)),
                      saldo=saldo,
                      data_NF=(format_date(data_NF)),
                      cod_NF=cod_NF,
                      prev_entrega=(format_date(prev_entrega)),
                      quant_entregue=quant_entregue,
                      data_entrada_obra=(format_date(data_entrada_obra)),
                      data_vencimento=(format_date(data_vencimento)),
                      data_prev_final = data_prev_final
                      )

            dados.save()
            obra = Obras(obra6=dados)
            obra.save()
            
            if str(row[1]) != 'nan' and int(row[1]):
                numero.append(row[1])

        if index == 3:
            
            nome_obra = row[3] if str(row[3]) != 'nan' else ""
            dados = Dados(nome_obra=nome_obra)
            dados.save()
            obra = Obras(obra6=dados)
            obra.save()

        if (index == 5) :
            for u in range (23):
                titles = row[u] if str(row[4]) != 'nan' else None
                dados = Dados(titles=titles)
                dados.save()
                obra = Obras(obra6=dados)
                obra.save()

    total_sols_compra = len(numero)   
    dados = Dados(total_sols_compra=total_sols_compra) 
    dados.save()
    itens = Dados.objects.all()
    for iten in itens:
        if iten.nome_obra != None:
            obra = Obras(obra6=dados)
    obra.save()
    Operations.objects.all().delete()
    NoPrazo.objects.all().delete()
    Atrasados.objects.all().delete()

    
    for iten in itens:
        if (iten.data_prev_final != None and iten.data_entrada_obra != None):
            data1 = datetime.strptime(str(iten.data_prev_final), "%Y-%m-%d").date() 
            data2 = datetime.strptime(str(iten.data_entrada_obra), "%Y-%m-%d").date() 
            diferenca = ((data2 - data1).days)
            if diferenca <= 0:
                noprazo.append(diferenca)
                prazo = NoPrazo(item=iten.item, 
                      cod_sol_compra=iten.cod_sol_compra, 
                      cod_obra=iten.cod_obra, 
                      cod_insumo=iten.cod_insumo, 
                      desc_insumo=iten.desc_insumo, 
                      num_ped_compra=iten.num_ped_compra, 
                      data_emissao_pc= iten.data_emissao_pc,
                      quant_sol=iten.quant_sol,
                      data_sol= iten.data_sol,
                      data_sol_cheg_obra= iten.data_sol_cheg_obra,
                      saldo=iten.saldo,
                      data_NF= iten.data_NF,
                      cod_NF=iten.cod_NF,
                      prev_entrega= iten.prev_entrega,
                      quant_entregue=iten.quant_entregue,
                      data_entrada_obra= iten.data_entrada_obra,
                      data_vencimento= iten.data_vencimento,
                      data_prev_final = iten.data_prev_final

                )
                prazo.save()
            else:
                atrasado.append(diferenca)
                prazo = Atrasados(item=iten.item, 
                      cod_sol_compra=iten.cod_sol_compra, 
                      cod_obra=iten.cod_obra, 
                      cod_insumo=iten.cod_insumo, 
                      desc_insumo=iten.desc_insumo, 
                      num_ped_compra=iten.num_ped_compra, 
                      data_emissao_pc= iten.data_emissao_pc,
                      quant_sol=iten.quant_sol,
                      data_sol= iten.data_sol,
                      data_sol_cheg_obra= iten.data_sol_cheg_obra,
                      saldo=iten.saldo,
                      data_NF= iten.data_NF,
                      cod_NF=iten.cod_NF,
                      prev_entrega= iten.prev_entrega,
                      quant_entregue=iten.quant_entregue,
                      data_entrada_obra= iten.data_entrada_obra,
                      data_vencimento= iten.data_vencimento,
                      data_prev_final = iten.data_prev_final
                )
                prazo.save()
        else:
            prazo = Indeterminados(item=iten.item, 
                      cod_sol_compra=iten.cod_sol_compra, 
                      cod_obra=iten.cod_obra, 
                      cod_insumo=iten.cod_insumo, 
                      desc_insumo=iten.desc_insumo, 
                      num_ped_compra=iten.num_ped_compra, 
                      data_emissao_pc= iten.data_emissao_pc,
                      quant_sol=iten.quant_sol,
                      data_sol= iten.data_sol,
                      data_sol_cheg_obra= iten.data_sol_cheg_obra,
                      saldo=iten.saldo,
                      data_NF= iten.data_NF,
                      cod_NF=iten.cod_NF,
                      prev_entrega= iten.prev_entrega,
                      quant_entregue=iten.quant_entregue,
                      data_entrada_obra= iten.data_entrada_obra,
                      data_vencimento= iten.data_vencimento,
                      data_prev_final = iten.data_prev_final
                )
            prazo.save()
                            
    prazo = len(noprazo)
    atrasados = len(atrasado)
    total_atendido = (prazo + atrasados)
    if iten.total_sols_compra != None and iten.total_sols_compra != 0:
            indeterminados = (iten.total_sols_compra - total_atendido)


    atendidos = Operations(prazo=prazo, atrasados=atrasados, total_atendido=total_atendido, indeterminados=indeterminados)
    atendidos.save()
    op = Operations.objects.all()
    for o in op:
        print(o.atrasados, o.prazo, o.total_atendido, o.indeterminados)

def graphic(request):

    return render(request, 'graphic.html', {'dados': Dados.objects.all(), 'prazos': Operations.objects.all(), 'atrasados': Atrasados.objects.all(), 'entregues': NoPrazo.objects.all, 'indeterminados':Indeterminados.objects.all(), 'form': FiltroForm(), 'insumos': Insumos.objects.all()})

def upload_page_obras(request):
    Operations.objects.all().delete()
    Dados.objects.all().delete()
    NoPrazo.objects.all().delete()
    Atrasados.objects.all().delete()
    Obras.objects.all().delete()
    print('Dados excluidos!')
    return render(request, 'upload-page-obras.html')

def upload_page_rh(request):
    DadosRH.objects.all().delete()
    DadosAjuCard.objects.all().delete()
    print('Dados excluidos!')
    return render(request, 'upload-page-rh.html')

def dados_do_modelo(request):
    operations = Operations.objects.all().values()
    return JsonResponse(list(operations), safe=False)

def cadastrar_insumo(request):
    if request.method == 'POST':
        form = AddInsumoForm(request.POST)
        if form.is_valid():
            codigo_insumo = form.cleaned_data['codigo_insumo']
            nome_do_insumo = form.cleaned_data['nome_do_insumo']
            qtd_dias = form.cleaned_data['qtd_dias']
            novo_insumo = Insumos(codigo_insumo=codigo_insumo, nome_do_insumo=nome_do_insumo, qtd_dias=qtd_dias)
            novo_insumo.save()
        return(redirect('graphic'))
    return(redirect('graphic'))
        
def filtrar(request):
    print(Insumos.objects.all())
    if request.method == 'POST':
        form = FiltroForm(request.POST)
        if form.is_valid():
            data_inicial = form.cleaned_data['data_inicial']
            data_final = form.cleaned_data['data_final']
            filtro = form.cleaned_data['filtro']
            if filtro == 'mes_entrega':
                objetos_filtrados = Dados.objects.filter(Q(prev_entrega__gte=data_inicial), Q(prev_entrega__lte=data_final))
            elif filtro == 'mes_emissao_pc':
                objetos_filtrados = Dados.objects.filter(Q(data_emissao_pc__gte=data_inicial), Q(data_emissao_pc__lte=data_final))
            
            obras = Obras.objects.all()
            for obra in obras:
                if obra.obra6.nome_obra:
                    print(obra.obra6.nome_obra)

            context = {'form': form, 'objetos': objetos_filtrados, 'dados': Dados.objects.all(), 'insumos': Insumos.objects.all()}
            return render(request, 'filtro.html', context)
        else:
            return(redirect('graphic'))
    else:
        form = FiltroForm()
    context = {'form': form}
    return render(request, 'filtro.html', context)

def index(request):
    return render(request, 'index.html')

def login(request):
    return render(request, 'login.html')