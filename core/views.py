from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum
from core.models import Dados, Operations, Insumos, DadosAjuCard, DadosRH, Totais, DadosComercial,ClientesComercial, DadosVT
from .forms import FiltroForm, UploadForm, AddInsumoForm, UploadRH
from datetime import datetime, timedelta
import tempfile, os, math, time, locale, numero_por_extenso, collections
import pandas as pd
import numpy as np
from random import randint

#calcula o valor a ser pago no VT
def calcular_pagar(cpf):
    try:
        # Obtendo os objetos que possuem o mesmo CPF nas duas tabelas
        obj_aju_card = DadosAjuCard.objects.get(cpf=cpf)
        obj_rh = DadosRH.objects.get(cpf=cpf)

        # Calculando o valor a pagar
        mult_valor_dias = ((obj_rh.valor/100) * obj_rh.dias_trabalhados)
        sub_valor_dias = (float(mult_valor_dias) - float(obj_aju_card.total_atualizado))
        pagar = max(sub_valor_dias, 0)
        if pagar / 9 != int:
            if ((math.ceil(pagar / 9))*9) < 45 and ((math.ceil(pagar / 9))*9) != 0 :
                pagar = 45
            else:
                pagar = ((math.ceil(pagar / 9))*9)
        

    except (DadosRH.DoesNotExist, DadosAjuCard.DoesNotExist):
        obj_rh = DadosRH.objects.get(cpf=cpf)
        pagar = ((obj_rh.valor/100) * obj_rh.dias_trabalhados)

    return pagar
#Upload dos arquivos de SC
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
            dados_obras(dados_xls, request)
            return(redirect('graphic'))

        else:
            return(redirect('upload-page-obras'))
    else:
        return(redirect('upload-page-obras'))
#Upload dos arquivos para analise de VT
def upload_rh(request):
    if request.method == 'POST':
        form = UploadRH(request.POST, request.FILES)
        if form.is_valid():
            arquivo1 = request.FILES['arquivo1']
            arquivo2 = request.FILES['arquivo2']
            dias_uteis = request.POST['diasUteis']
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

            dados_rh(dados_xls, dados_xls2, (int(dias_uteis)))
            return(redirect('results-rh'))
        else:
            return(redirect('upload-page-rh'))
    else:
        return(redirect('upload-page-rh'))
#Define e salva os dados dos arquivos de VT    
def dados_rh(dados_xls, dados_xls2, dias_uteis):
    start = time.time()
    nome_obra = str(dados_xls2.iloc[8, 1])
    data = str(dados_xls2.iloc[1, 17])
    formato = '%Y-%m-%d %H:%M:%S'
    data_sem_horas = str(datetime.strptime(data, formato).date())
    lista_real = []
    lista_aju = []
    dados_rh_update = []

    
    

    for index, row in dados_xls.iterrows():
        
        cpf = (row[0])
        if not pd.isna(cpf):
                cpf = cpf.zfill(11)
            #if str(row[6]) == 'OPERACIONAL DE OBRA':
                dias_trabalhados = row[1] if not pd.isna(row[1]) else None
                valor = row[2] if not pd.isna(row[2]) else None
                nome = row[3] if not pd.isna(row[3]) else None
                lista_real.append(DadosRH(cpf=cpf, dias_trabalhados=dias_trabalhados, valor=valor, nome=nome, nome_obra=nome_obra))
    DadosRH.objects.bulk_create(lista_real) 
    

    for index, row in dados_xls2.iterrows():
        if index == 1:
            data = str(row[17])
            formato = '%Y-%m-%d %H:%M:%S'
            data_sem_horas = str(datetime.strptime(data, formato).date())
        elif index == 8:
            nome_obra = str(row[1])
        elif index > 10 and isinstance(row[1], str) and str(row[1]) != 'Total:':
            cpf2 = row[1]
            nome2 = str(row[5]) if isinstance(row[5], str) else None
            cartao = str(row[8]) if isinstance(row[8], str) else None
            saldoA = float(row[9]) if isinstance(row[9], (int, float)) and not np.isnan(row[9]) else None
            saldo = float(row[10]) if isinstance(row[10], (int, float)) and not np.isnan(row[10]) else None
            total_saldo = float(row[12]) if isinstance(row[12], (int, float)) and not np.isnan(row[12]) else None
            recarga = float(row[16]) if isinstance(row[16], (int, float)) and not np.isnan(row[16]) else None
            total = float(row[19]) if isinstance(row[19], (int, float)) and not np.isnan(row[19]) else None
            if total is not None and ((total - (dias_uteis * 9)) >= 0):
                total_atualizado = (total - (dias_uteis * 9))
            else:
                total_atualizado = 0
            lista_aju.append(DadosAjuCard(cpf=cpf2, nome=nome2, cartao=cartao, 
                                          saldoA=saldoA, saldo=saldo, total_saldo=total_saldo, 
                                          recarga=recarga, total=total, total_atualizado=total_atualizado, 
                                          data_planilha=data_sem_horas, nome_obra=nome_obra))
            
            dados_rh_update.append(DadosRH(pk=cpf2, total=total, total_atualizado=total_atualizado))

    DadosRH.objects.bulk_update(dados_rh_update, ['total', 'total_atualizado'])
    DadosAjuCard.objects.bulk_create(lista_aju) 
    salario_base = 2000
    dados = DadosRH.objects.filter(nome_obra=nome_obra)   
    ctrl_total = int(0)
    ctrl_total_pagar = int(0)
    dias_list = []
    for dado in dados:
        obj_rh = DadosRH.objects.get(pk=dado.cpf)
        obj_rh.pagar = calcular_pagar(dado.cpf)
        if obj_rh.pagar is not None:
            if obj_rh.pagar != 0:
                dias_contabilizados=(obj_rh.pagar/9)
                desconto_vt = (salario_base*0.06)
                porcentagem = (dias_contabilizados/obj_rh.dias_trabalhados)
                valor_desconto_colaborador = math.ceil((desconto_vt*porcentagem)*10)/10
                dias_list.append(DadosRH(pk=dado.cpf, pagar=obj_rh.pagar, dias_contabilizados=dias_contabilizados))
            else: 
                valor_desconto_colaborador = int(0)
                dias_list.append(DadosRH(pk=dado.cpf, pagar=obj_rh.pagar, dias_contabilizados=int(0)))
            print(valor_desconto_colaborador)
        ctrl_total += obj_rh.dias_trabalhados
        if obj_rh.pagar:
            ctrl_total_pagar += obj_rh.pagar

    ctrl_total = (ctrl_total*9)
    total = formatar_real(ctrl_total)
    total_pagar = formatar_real(ctrl_total_pagar)
    total_descontos = formatar_real(ctrl_total - ctrl_total_pagar)
    
    DadosRH.objects.bulk_update(dias_list, ['pagar','dias_contabilizados'])
    salvar = Totais(total=total, total_descontos=total_descontos, total_pagar=total_pagar, nome_obra=nome_obra)
    salvar.save()

    end = time.time()
    print(f"Tempo total de leitura: {end - start}")
#Formata os valores para uma string em Real
def formatar_real(value):
    try:
        formatar = '{:,.2f}'.format(value).replace(',', 'X').replace('.', ',').replace('X', '.')
        total = (f'R${formatar}')
        return total
    except TypeError:
        return None
#Renderiza a página de resultados do VT
def results_rh(request):
    dados = Totais.objects.all()
    data = DadosAjuCard.objects.all().first()
    nome_obra = str(data.nome_obra)

    reais = DadosRH.objects.all()
    obras = []
    anterior = None
    for real in reais:
        if real.nome_obra is not None and anterior != real.nome_obra:
            obras.append(real.nome_obra)
            anterior = real.nome_obra

    for dado in dados:
        total = dado.total
        total_pagar = dado.total_pagar
        total_descontos = dado.total_descontos
    
    #dado = DadosAjuCard.objects.all().first()
    #calcular_dias_uteis(dado.data_planilha)  
    return render(request, 'results-rh.html', {'reais':DadosRH.objects.all(), 'Ajucards': DadosAjuCard.objects.all(), 
                                                   'total': total, 'total_pagar': total_pagar, 'total_descontos': total_descontos, 
                                                   'data_planilha': data.data_planilha, 'nome_obra': nome_obra, 'obras': obras,})
#Cria e disponibiliza para download o arquivo Excel com os dados do VT
def download_table(request, nome_obra):
    reais = DadosRH.objects.all()
    dados = Totais.objects.all()
    totais = (list(dados.values('total', 'total_pagar', 'total_descontos')))
    data = DadosAjuCard.objects.all().first()
    date_string = str(data.data_planilha)
    date_object = datetime.strptime(date_string, '%Y-%m-%d')
    new_date = date_object.strftime('%d-%m-%Y')
    nome_obra = str(data.nome_obra)
    df = pd.DataFrame(list(reais.values('cpf', 'nome', 'dias_trabalhados', 'dias_contabilizados', 'pagar', 'total', 'total_atualizado')))
    
    
    df.columns = ['CPF', 'Nome', 'Dias', 'Dias 2', 'Valor a pagar', 'Saldo', 'Saldo Atualizado']
    
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{nome_obra}.xls"'
    
    writer = pd.ExcelWriter(response, engine='xlsxwriter')
    df.to_excel(writer, index=False, startrow=6)
    
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']  
    center_format = workbook.add_format({'align': 'center'})

    red_format = workbook.add_format({'font_color': 'white', 'bg_color': 'red', 'align': 'center'})
    blue_format = workbook.add_format({'font_color': 'white','bg_color': 'blue', 'align': 'center'})
    green_format = workbook.add_format({'font_color': 'white', 'bg_color': 'green', 'align': 'center'})
    black_format = workbook.add_format({'font_color': 'white', 'bg_color': 'black', 'align': 'center'})
    worksheet.write('B2', f"Total: {totais[0]['total']}", blue_format, )
    worksheet.write('B3', f"Total a pagar: {totais[0]['total_pagar']}", red_format, )
    worksheet.write('B4', f"Total descontos: {totais[0]['total_descontos']}", green_format, )
    worksheet.write('D5', f"Data: {new_date}", )
    worksheet.write('B6', nome_obra, black_format, )
    
    for i, col in enumerate(df.columns):
        max_width = max(len(str(col)), df[col].astype(str).map(len).max())
        worksheet.set_column(i, i, max_width + 1, center_format)
    
    writer.close()
    
    return response
#Cria e disponibiliza para download o arquivo TXT com os dados do VT  
def download_txt(request, nome_obra):
    
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="{nome_obra}.txt"'

    reais = DadosRH.objects.all()
    response.write('0200\n')
    for real in reais:
        if real.dias_contabilizados:
            if real.dias_contabilizados > 0:
                response.write('{0}|{1}|{2}|{3}\n'.format(
                    real.cpf,
                    real.dias_contabilizados,
                    '900',
                    real.nome,
                ))

    return response
#Formata os valores de datas para salvar no DB 
def format_date(indice):
    if isinstance(indice, str):
        try:
            date = datetime.strptime(indice, "%d/%m/%Y").date()
        except ValueError:
            date = None
    else:
        date = None
    return date
#Define e salva os dados dos arquivos de SC
def dados_obras(dados_xls, request):
    start = time.time()
    numero = []    
    insumos = Insumos.objects.all()
    atrasado = []
    noprazo = []
    bulk_list = []
    nome_obra = str(dados_xls.iloc[3, 3])
    
    for index, row in dados_xls.iterrows():
        data_prev_final = None
        
        if index < 5:
            continue

            
        item = None if pd.isna(row[0]) else int(row[0]) if isinstance(row[0], (int, float)) else None
        cod_sol_compra = None if pd.isna(row[1]) else int(row[1]) if isinstance(row[1], (int, float)) else None
        cod_obra = None if pd.isna(row[2]) else int(row[2]) if isinstance(row[2], (int, float)) else None
        cod_insumo = None if pd.isna(row[4]) else int(row[4]) if isinstance(row[4], (int, float)) else None
        desc_insumo = None if pd.isna(row[5]) else row[5] if isinstance(row[5], str) else None
        quant_sol = None if pd.isna(row[8]) else str(row[8])    
        data_sol = None if pd.isna(row[10]) else row[10] if isinstance(row[10], str) else None
        data_sol_cheg_obra = None if pd.isna(row[11]) else row[11] if isinstance(row[11], str) else None
        num_ped_compra = None if pd.isna(row[12]) else int(row[12]) if isinstance(row[12], (int, float)) else None
        data_emissao_pc = None if pd.isna(row[13]) else row[13] if isinstance(row[13], str) else None
        prev_entrega = None if pd.isna(row[14]) else row[14] if isinstance(row[14], str) else None
        quant_entregue = None if pd.isna(row[16]) else str(row[16])
        saldo = None if pd.isna(row[18]) else str(row[18])
        data_NF = None if pd.isna(row[19]) else row[19] if isinstance(row[19], str) else None
        cod_NF = None if pd.isna(row[20]) else row[20] if isinstance(row[20], str) else None
        data_entrada_obra = None if pd.isna(row[21]) else row[21] if isinstance(row[21], str) else None
        data_vencimento = None if pd.isna(row[22]) else row[22] if isinstance(row[22], str) else None
        status = 'Total'
        if cod_insumo == 5444:
            print(cod_insumo)
        insumos = Insumos.objects.filter(codigo_insumo=cod_insumo)
        if insumos.exists() and data_emissao_pc:
            insumo = insumos.first()
            data_prev_final = format_date(data_emissao_pc) + timedelta(days=insumo.qtd_dias) if insumo.qtd_dias else None
        else:
            data_prev_final = format_date(prev_entrega)

        data_entrada_obra = format_date(data_entrada_obra)
        if data_prev_final and data_entrada_obra:
            data_prev_final = datetime.strptime(str(data_prev_final), "%Y-%m-%d").date()
            data_entrada_obra = datetime.strptime(str(data_entrada_obra), "%Y-%m-%d").date()
            diferenca = (data_entrada_obra - data_prev_final).days
            if diferenca <= 0:
                status = 'NoPrazo'
                noprazo.append(diferenca)
            else:
                status = 'Atrasado'
                atrasado.append(diferenca)
        else:
            status = 'Indeterminado'

        bulk_list.append(Dados(item=item,
                  id=index, 
                  cod_sol_compra=cod_sol_compra, 
                  cod_obra=cod_obra, cod_insumo=cod_insumo, 
                  desc_insumo=desc_insumo, 
                  num_ped_compra=num_ped_compra, 
                  data_emissao_pc=(format_date(data_emissao_pc)),
                  quant_sol=quant_sol,
                  data_sol=(format_date(data_sol)),
                  data_sol_cheg_obra=(format_date(data_sol_cheg_obra)),
                  saldo=saldo,
                  nome_obra=nome_obra,
                  status = status,
                  data_NF=(format_date(data_NF)),
                  cod_NF=cod_NF,
                  prev_entrega=(format_date(prev_entrega)),
                  quant_entregue=quant_entregue,
                  data_entrada_obra=(data_entrada_obra),
                  data_vencimento=(format_date(data_vencimento)),
                  data_prev_final = data_prev_final
                  ))
        
        

        if isinstance(row[1], int):
            numero.append(row[1])
    Dados.objects.bulk_create(bulk_list)      
    total_sols_compra = len(numero)   
    iten = Dados.objects.all().first()
    iten.total_sols_compra = total_sols_compra 
    iten.nome_obra = nome_obra
    print(iten.nome_obra)
    iten.save()

    Operations.objects.all().delete()

     
    prazo = len(noprazo)
    atrasados = len(atrasado)
    total_atendido = (prazo + atrasados)
    if iten.total_sols_compra != None and iten.total_sols_compra != 0:
            indeterminados = (iten.total_sols_compra - total_atendido)

    atendidos = Operations(prazo=prazo, atrasados=atrasados, total_atendido=total_atendido, indeterminados=indeterminados)
    atendidos.save()
    end = time.time()
    print(f"Tempo total de leitura: {end - start}")
    return render(request, 'graphic.html', {'nome_obra': nome_obra, 
    'dados': Dados.objects.all(), 
    'prazos': Operations.objects.all(), 
    'atrasados': Dados.objects.filter(status='Atrasado'), 
    'entregues': Dados.objects.filter(status='NoPrazo'), 
    'indeterminados':Dados.objects.filter(status='Indeterminado'), 
    'form': FiltroForm(), 
    'insumos': Insumos.objects.all()})
#Renderiza a página de resultados de SC
def graphic(request):
    iten = Dados.objects.all().first()
    nome_obra = iten.nome_obra
    #dados_obras = Dados.objects.all()
    #obras = []
    #anterior = None
    #
    ##################################################################
    #for real in dados_obras:
    #    if real.nome_obra is not None and anterior != real.nome_obra:
    #        obras.append(real.nome_obra)
    #        anterior = real.nome_obra
    ##################################################################


    return render(request, 'graphic.html', {'nome_obra': nome_obra, 
    'dados': Dados.objects.all(), 
    'prazos': Operations.objects.all(), 
    'atrasados': Dados.objects.filter(status='Atrasado'), 
    'entregues': Dados.objects.filter(status='NoPrazo'), 
    'indeterminados':Dados.objects.filter(status='Indeterminado'), 
    'form': FiltroForm(), 
    'insumos': Insumos.objects.all()})
#Renderiza a página de upload dos arquivos de SC
def upload_page_obras(request):

        Dados.objects.all().delete()
        Operations.objects.all().delete()

        print('Dados excluidos!')
        return render(request, 'upload-page-obras.html')
#Renderiza a página de upload dos arquivos de analise de VT
def upload_page_rh(request):
    DadosRH.objects.all().delete()
    DadosAjuCard.objects.all().delete()
    Totais.objects.all().delete()
    print('Dados excluidos!')
    return render(request, 'upload-page-rh.html')
#Retorna os valores das quantidades de SC em atraso, no prazo e indeterminadas para gerar o gráfico
def dados_do_modelo(request):
    operations = Operations.objects.all().values()
    return JsonResponse(list(operations), safe=False)
#Cadastrar novos insumos no banco de dados para o calculo de previsão de entrega
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
#Filtra os dados dos resultados de SC por datas        
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
            
            #obras = Obras.objects.all()
            #for obra in obras:
            #    if obra.obra6.nome_obra:
            #        print(obra.obra6.nome_obra)

            context = {'form': form, 'objetos': objetos_filtrados, 'dados': Dados.objects.all(), 'insumos': Insumos.objects.all()}
            return render(request, 'filtro.html', context)
        else:
            return(redirect('graphic'))
    else:
        form = FiltroForm()
    context = {'form': form}
    return render(request, 'filtro.html', context)
#Retorna Index.html
def index(request):
    return render(request, 'index.html')
#Retorna página de login
def login(request):
    return render(request, 'login.html')
#Salva os dados
def save_data(request):
    if request.method == 'POST':
        data = DadosAjuCard.objects.all().first()
        nome_obra = data.nome_obra
        dados_rh = DadosRH.objects.all()
        anterior = None
        for dado in dados_rh:
            if dado.nome_obra is not None and anterior != dado.nome_obra:
                print(dado.nome_obra)
                anterior = dado.nome_obra

        return HttpResponse('success')
#Renderiza a página de upload dos arquivos de importação de VT
def upload_import_vt(request):
    DadosVT.objects.all().delete()
    print('Dados Excluídos!')
    return render(request, 'upload-import-vt.html')
#Upload dos arquivos de importação de VT
def upload_vt(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            arquivo = request.FILES['arquivo']
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                for chunk in arquivo.chunks():
                    tmp.write(chunk)
            dados_xls = pd.read_excel(tmp.name)
            os.unlink(tmp.name)
            dados_vt(dados_xls, request)
            return(redirect('import-vt'))
        else:
            return(redirect('upload-import-vt'))
    else:
        return(redirect('upload-import-vt'))
#Define e salva os dados dos arquivos de importação de VT 
def dados_vt(dados_xls, request):
    start = time.time()
    lista_vt = []
    for index, row in dados_xls.iterrows():
        empresa = row['Empresa']
        admissao = row['Admissão']
        nome = row['Nome do Funcionário']
        cpf = str(row['CPF']).zfill(11)
        print(cpf)
        id = row['Identidade']
        mae = row['Mãe']
        nasc = row['Nascimento']
        cep = row['CEP']
        endereco = row['Endereço'] 
        numero_endereco = row['Número Endereço'] if not pd.isna(row['Número Endereço']) else None
        cidade = row['Cidade']
        bairro = row['Bairro']
        lista_vt.append(DadosVT( empresa =  empresa ,admissao =  admissao ,nome =  nome ,cpf =  cpf ,id =  id ,mae =  mae ,nasc =  nasc ,cep =  cep ,endereco =  endereco ,numero_endereco =  numero_endereco ,cidade =  cidade ,bairro =  bairro ))    
    DadosVT.objects.bulk_create(lista_vt)
    end = time.time()
    print(f"Tempo total de leitura: {end - start}")
#Renderiza a página de resultados de importação de VT
def import_vt(request):
    return render(request, 'import-vt.html', {'dados': DadosVT.objects.all()})
#Cria e disponibiliza para download o arquivo TXT com os dados de importação do VT
def download_txt_vt(request):
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="Resultado da Consulta.txt"'

    dados = DadosVT.objects.all()
    response.write(' 0700\n')
    for dado in dados:
        id_numbers = [int(num)for num in dado.id.split() if num.isdigit()]
        id_str = ','.join(map(str, id_numbers))
        cpf = dado.cpf.ljust(26)
        nome = dado.nome.ljust(100)
        nasc = (str(dado.nasc.strftime("%d/%m/%Y"))).ljust(31)
        mae = dado.mae.ljust(50)
        zero = '0000000000'.ljust(23)
        endereco = f'SE{dado.endereco.upper()}'.ljust(202)
        numero_endereco = str(dado.numero_endereco).ljust(65)
        bairro = dado.bairro.ljust(100)
        cidade = dado.cidade.ljust(100)
        cep_id = f'{dado.cep.replace("-", "")}{id_str}'.ljust(29)
        print(cep_id)
        linha = f'{cpf}{nome}{nasc}{mae}{zero}{endereco}{numero_endereco}{bairro}{cidade}{cep_id} 04'.ljust(729)
        response.write(linha + '\n')

    return response
#Renderiza a página de upload dos arquivos de importação de Comercial
def upload_page_comercial(request):
    DadosComercial.objects.all().delete()
    ClientesComercial.objects.all().delete()
    print('Dados excluidos!')
    return render(request, 'upload-page-comercial.html')
#Calcula os dados de parcelas do comercial
def calcular_parcelas(lista, valor, texto, vencimentos):

    contagem = collections.Counter(lista)

    parcelas = []
    for valor, qtd in contagem.items():
        valor_extenso = numero_por_extenso.monetario(valor)
        valor_formatado = formatar_real(valor)
        data_vencimento = vencimentos[0]  
        if texto == 'MENSAL' or texto == 'SEMESTRAL' or texto == 'INTERMEDIÁRIA' or texto == 'INTERMEDIÁRIA 2' or texto == 'CARTÃO DE CREDITO' or texto == 'ANUAL':
            parcela = f" {texto}: {qtd} ({numero_por_extenso.real(qtd)}) parcela(s) de {valor_formatado} ({valor_extenso}), com primeiro vencimento em {data_vencimento} sem juros e com reajuste a partir da data desse instrumento."
        elif texto == 'SINAL ATO' or texto == 'TRANSFERENCIA DE CREDITO':
            parcela = f" {texto}: {qtd} ({numero_por_extenso.real(qtd)}) parcela(s) de {valor_formatado} ({valor_extenso}), com primeiro vencimento em {data_vencimento} sem juros e sem reajuste a partir da data desse instrumento."
        elif texto == 'BIMESTRAL' or texto == 'CHAVESL' or texto == 'RESIDUO':
            parcela = f" {texto}: {qtd} ({numero_por_extenso.real(qtd)}) parcela(s) de {valor_formatado} ({valor_extenso}), com primeiro vencimento em {data_vencimento} a ser acrescido de juros a partir da data do Habite-se e com reajuste a partir da data desse instrumento."
        elif texto == 'MENSAL 2':
            parcela = f" {texto}: {qtd} ({numero_por_extenso.real(qtd)}) parcela(s) de {valor_formatado} ({valor_extenso}), com primeiro vencimento em {data_vencimento} a ser acrescido de juros a partir da data do Habite-se e com correção monetária a partir da data desse instrumento."
        elif texto == 'SINAL' or texto == 'SINAL CARTÃO' or texto == 'PARCELA CARTÃO' or texto == 'FINANCIAMENTO ASSOCIATIVO' or texto == 'FINANCIAMENTO':
            parcela = f" {texto}: {qtd} ({numero_por_extenso.real(qtd)}) parcela(s) de {valor_formatado} ({valor_extenso}), com primeiro vencimento em {data_vencimento} sem juros e sem reajuste."
        elif texto == 'FINANCIAMENTO':
            parcela = f" {texto}: {qtd} ({numero_por_extenso.real(qtd)}) parcela(s) de {valor_formatado} ({valor_extenso}), com vencimento em {data_vencimento} sem juros e sem reajuste."
        elif texto == 'FGTS':
            parcela = f" {texto}: {valor_formatado} ({valor_extenso}), com primeiro vencimento em {data_vencimento} sem juros e sem reajuste."
        for u in range (qtd):
            vencimentos.pop(0) 
        parcelas.append(parcela)
    return (parcelas)
#Define e salva os dados do arquivo Comercial 
def dados_comercial(dados_xls, request):
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    lista_vcto_mensal = []
    lista_vcto_ato = []
    lista_vcto_mensal2 = []
    lista_vcto_intermediaria = []
    lista_vcto_intermediaria2 = []
    lista_vcto_anual = []
    lista_vcto_sinal = []
    lista_vcto_financiamento = []
    lista_vcto_finass = []
    lista_vcto_semestral = []
    lista_vcto_bimestral = []
    lista_vcto_chaves = []
    lista_vcto_residuo = []
    lista_vcto_sincart = []
    lista_vcto_parcart = []
    lista_vcto_cartaocred = []
    lista_vcto_transcred = []
    lista_vcto_fgts = []
    condicoes = []    
    lista_comercial = []
    Financiamento = []
    Semestrais = []
    Bimestral = []
    Chaves = []
    Residuo = []
    Parc_inter = []
    Parc_interm2 = []
    Sinal_cart = []
    Parcela_cart = []
    cartao_cred = []
    trans_cred = []
    Anual = []
    Fgts = []
    Mensal = []
    Mensal2 = []
    Sinal = []
    Ato = []
    FinAss = []
    par2 = []
    debitos = []
    lista_comercial_condicoes = []
    empresa = str(dados_xls.iloc[3, 5])
    centro_custo = str(dados_xls.iloc[4, 5])
    try:
        titulo_cliente = int(dados_xls.iloc[4, 25])
    except ValueError:
        titulo_cliente = int(dados_xls.iloc[4, 27])
    cliente = str(dados_xls.iloc[7, 5])
    data_emissao = format_date(str(dados_xls.iloc[5, 5]))
    limite_correcao = format_date(str(dados_xls.iloc[6, 5]))
    try:
        ultimo_reajuste = format_date(str(dados_xls.iloc[6, 25]))
    except ValueError:
        ultimo_reajuste = format_date(str(dados_xls.iloc[6,27]))
    documento = str(dados_xls.iloc[8, 5])
    if str(dados_xls.iloc[8, 25]) != 'nan':
        unidades = str(dados_xls.iloc[8, 25])
    else:
        unidades = str(dados_xls.iloc[8,27]) 

    for index, row in dados_xls.iterrows():
        if index == 11:
            for x in range (len(row)):
                if row[x] and row[x] == 'Par':
                    i_par = x
                elif row[x] and row[x] == 'Data vcto.':
                    i_data_vcto = x    
                elif row[x] and row[x] == 'Tipo Condição':
                    i_tipo_condicao = x
                elif row[x] and row[x] == 'Id':
                    i_id = x
                elif row[x] and row[x] == 'Vl. original':
                    i_vl_original = x
                elif row[x] and row[x] == 'Ind. dt base':
                    i_ind_dt_base = x
                elif row[x] and row[x] == 'Ind. dt calc':
                    i_ind_dt_calc = x
                elif row[x] and row[x] == 'Correção':
                    i_correcao = x
                elif row[x] and row[x] == 'Juro contr.%':
                    i_porc_juro_contr = x
                elif row[x] and row[x] == 'Dt. base juro':
                    i_dt_base_juro = x
                elif row[x] and row[x] == 'Dt. calc juro':
                    i_dt_calc_juro = x
                elif row[x] and row[x] == 'Juro contr.':
                    i_juro_contr = x
                elif row[x] and row[x] == '% Multa':
                    i_porc_multa = x
                elif row[x] and row[x] == '% Juros':
                    i_porc_juros = x
                elif row[x] and row[x] == '% Pró-rata':
                    i_porc_pro_rata = x
                elif row[x] and row[x] == 'Multa':
                    i_multa = x
                elif row[x] and row[x] == 'Juros':
                    i_juros = x
                elif row[x] and row[x] == 'Pró-rata':
                    i_pro_rata = x
                elif row[x] and row[x] == 'Total':
                    i_total = x
                elif row[x] and row[x] == 'Valor devido':
                    i_valor_devido = x
                elif row[x] and row[x] == 'Dias':
                    i_dias = x
                elif row[x] and row[x] == 'Dt. recto.':
                    i_dt_recto = x
                elif row[x] and row[x] == 'Valor pago':
                    i_valor_pago = x
        
        if 11 < index:
            try:    
                par = str(row[i_par]) if isinstance(row[i_data_vcto], str) else None
                id = int(row[i_id]) if str(row[i_dias]) != 'nan' else None 
                total_lanc = row[9] if str(row[0]) == 'Total lanc.'  and not np.isnan(row[9])else None
                total_debitos = row[i_valor_devido] if str(row[0]) == 'Total lanc.'  and not np.isnan(row[i_valor_devido])else None
                data_vcto = format_date(str(row[i_data_vcto])) if isinstance(row[i_data_vcto], str) and str(row[i_data_vcto]) != 'nan' else None
                tipo_condicao = str(row[i_tipo_condicao]) if isinstance(row[i_tipo_condicao], str) and str(row[i_tipo_condicao]) != 'nan' else None
                vl_original = float(row[i_vl_original]) if isinstance(row[i_vl_original], (int, float)) and not np.isnan(row[i_vl_original]) else None
                ind_dt_base = float(row[i_ind_dt_base]) if isinstance(row[i_ind_dt_base], (int, float)) and not np.isnan(row[i_ind_dt_base]) else None
                ind_dt_calc = float(row[i_ind_dt_calc]) if isinstance(row[i_ind_dt_calc], (int, float)) and not np.isnan(row[i_ind_dt_calc]) else None
                correcao = float(row[i_correcao]) if isinstance(row[i_correcao], (int, float)) and not np.isnan(row[i_correcao]) else None
                porc_juro_contr = float(row[i_porc_juro_contr]) if isinstance(row[i_porc_juro_contr], (int, float)) and not np.isnan(row[i_porc_juro_contr]) else 0
                dt_base_juro = float(row[i_dt_base_juro]) if isinstance(row[i_dt_base_juro], (int, float)) and not np.isnan(row[i_dt_base_juro]) else 0
                dt_calc_juro = float(row[i_dt_calc_juro]) if isinstance(row[i_dt_calc_juro], (int, float)) and not np.isnan(row[i_dt_calc_juro]) else 0
                juro_contr = float(row[i_juro_contr]) if isinstance(row[i_juro_contr], (int, float)) and not np.isnan(row[i_juro_contr]) else None
                porc_multa = float(row[i_porc_multa]) if isinstance(row[i_porc_multa], (int, float)) and not np.isnan(row[i_porc_multa]) else None
                porc_juros = float(row[i_porc_juros]) if isinstance(row[i_porc_juros], (int, float)) and not np.isnan(row[i_porc_juros]) else None
                porc_pro_rata = float(row[i_porc_pro_rata]) if isinstance(row[i_porc_pro_rata], (int, float)) and not np.isnan(row[i_porc_pro_rata]) else None
                multa = float(row[i_multa]) if isinstance(row[i_multa], (int, float)) and not np.isnan(row[i_multa]) else None
                juros = float(row[i_juros]) if isinstance(row[i_juros], (int, float)) and not np.isnan(row[i_juros]) else None
                pro_rata = float(row[i_pro_rata]) if isinstance(row[i_pro_rata], (int, float)) and not np.isnan(row[i_pro_rata]) else None
                total = (row[i_total]) if isinstance(row[i_total], (int, float)) and not np.isnan(row[i_total]) else None
                valor_devido = float(row[i_valor_devido]) if isinstance(row[i_valor_devido], (int, float)) and not np.isnan(row[i_valor_devido]) else None
                dias = row[i_dias] if str(row[i_dias]) != 'nan' else None
                dt_recto = format_date(str(row[i_dt_recto])) if isinstance(row[i_dt_recto], str) else None
                valor_pago = float(row[i_valor_pago]) if isinstance(row[i_valor_pago], (int, float)) and not np.isnan(row[i_valor_pago]) else None
                reparcelamento = True if str(row[i_dt_recto]) == '*** Reparcelamento ***' else False

                if par is not None:
                    par2 = par
                if tipo_condicao is not None:
                    ti_co = tipo_condicao
                
                if total_debitos is not None:
                    debitos.append(total_debitos)
                if valor_devido and valor_devido > 0:
                    if tipo_condicao == "Parcela Mensais 2":
                        Mensal2.append(valor_devido)
                        VctoMensais2 = data_vcto.strftime("%d/%m/%Y")
                        lista_vcto_mensal2.append(VctoMensais2)
                        ValorMensais2 = valor_devido

                    elif tipo_condicao == "Ato":
                        Ato.append(valor_devido)
                        VctoAto = data_vcto.strftime("%d/%m/%Y")
                        lista_vcto_ato.append(VctoAto)
                        ValorAto = valor_devido

                    elif tipo_condicao == "Parcelas Mensais":
                        Mensal.append(valor_devido)
                        VctoMensal = data_vcto.strftime("%d/%m/%Y")
                        lista_vcto_mensal.append(VctoMensal)
                        ValorMensal = valor_devido

                    elif tipo_condicao == "Parcelas Semestrais":
                        Semestrais.append(valor_devido)
                        VctoSemestrais = data_vcto.strftime("%d/%m/%Y")
                        lista_vcto_semestral.append(VctoSemestrais)
                        ValorSemestrais = valor_devido

                    elif tipo_condicao == "Parcelas Bimestrais":
                        Bimestral.append(valor_devido)
                        VctoBimestral = data_vcto.strftime("%d/%m/%Y")
                        lista_vcto_bimestral.append(VctoBimestral)
                        ValorBimestral = valor_devido

                    elif tipo_condicao == "Entrega das chaves":
                        Chaves.append(valor_devido)
                        VctoChaves = data_vcto.strftime("%d/%m/%Y")
                        lista_vcto_chaves.append(VctoChaves)
                        ValorChaves = valor_devido

                    elif tipo_condicao == "Resíduo":
                        Residuo.append(valor_devido)
                        VctoResiduo = data_vcto.strftime("%d/%m/%Y")
                        lista_vcto_residuo.append(VctoResiduo)
                        ValorResiduo = valor_devido

                    elif tipo_condicao == "Sinal":
                        Sinal.append(valor_devido)
                        VctoSinal = data_vcto.strftime("%d/%m/%Y")
                        lista_vcto_sinal.append(VctoSinal)
                        ValorSinal = valor_devido

                    elif tipo_condicao == "Parcelas Intermediária":
                        Parc_inter.append(valor_devido)
                        VctoIntermediaria = data_vcto.strftime("%d/%m/%Y")
                        lista_vcto_intermediaria.append(VctoIntermediaria)
                        ValorIntermediaria = valor_devido

                    elif tipo_condicao == "Parcelas Intermediária 2":
                        Parc_interm2.append(valor_devido)
                        VctoIntermediaria2 = data_vcto.strftime("%d/%m/%Y")
                        lista_vcto_intermediaria2.append(VctoIntermediaria2)
                        ValorIntermediaria2 = valor_devido

                    elif tipo_condicao == "Sinal Cartão":
                        Sinal_cart.append(valor_devido)
                        VctoSinalCartao = data_vcto.strftime("%d/%m/%Y")
                        lista_vcto_sincart.append(VctoSinalCartao)
                        ValorSinalCartao = valor_devido

                    elif tipo_condicao == "Parcela Cartão":
                        Parcela_cart.append(valor_devido)
                        VctoParcelaCartao = data_vcto.strftime("%d/%m/%Y")
                        lista_vcto_parcart.append(VctoParcelaCartao)
                        ValorParcelaCartao = valor_devido

                    elif tipo_condicao == "Carta de Crédito":
                        cartao_cred.append(valor_devido)
                        VctoCartaoCredito = data_vcto.strftime("%d/%m/%Y")
                        lista_vcto_cartaocred.append(VctoCartaoCredito)
                        ValorCartaoCredito = valor_devido

                    elif tipo_condicao == "Transferencia Crédito":
                        trans_cred.append(valor_devido)
                        VctoTransferenciaCredito = data_vcto.strftime("%d/%m/%Y")
                        lista_vcto_transcred.append(VctoTransferenciaCredito)
                        ValorTransferenciaCredito = valor_devido

                    elif tipo_condicao == "Financiamento Associativo":
                        FinAss.append(valor_devido)
                        VctoFinanciamentoAss = data_vcto.strftime("%d/%m/%Y")
                        lista_vcto_finass.append(VctoFinanciamentoAss)
                        ValorFinanciamentoAss = valor_devido

                    elif tipo_condicao == "Anual":
                        Anual.append(valor_devido)
                        VctoAnual = data_vcto.strftime("%d/%m/%Y")
                        lista_vcto_anual.append(VctoAnual)
                        ValorAnual = valor_devido

                    elif tipo_condicao == "FGTS":
                        Fgts.append(valor_devido)
                        VctoFgts = data_vcto.strftime("%d/%m/%Y")
                        lista_vcto_fgts.append(VctoFgts)
                        ValorFgts = valor_devido

                    elif tipo_condicao == "Financiamento":
                        Financiamento.append(valor_devido)
                        VctoFinanciamento = data_vcto.strftime("%d/%m/%Y")
                        lista_vcto_financiamento.append(VctoFinanciamento)
                        ValorFinanciamento = valor_devido
                
                if index < (len(dados_xls)-1) and str(dados_xls.iloc[index+1, i_tipo_condicao]) == 'nan' and str(dados_xls.iloc[index+1, i_valor_pago]) != 'nan' or par is None and valor_pago is not None and dt_recto is not None:
                    if (dados_xls.iloc[index+1, 0]) != '(C) - Parcela enviada para a cobrança escritural.' :
                        par = par2
                        tipo_condicao = ti_co

                if total_lanc is not None:
                    lista_comercial.append(DadosComercial(total_lanc = total_lanc))
                if (par is not None and str(row[0]) != 'Total lanc.'):
                    if str(row[0]) != '(C) - Parcela enviada para a cobrança escritural.' :
                        lista_comercial.append(DadosComercial(par=par, data_vcto = data_vcto, tipo_condicao = tipo_condicao, 
                                                          id = id, vl_original = vl_original, ind_dt_base = ind_dt_base, 
                                                          ind_dt_calc = ind_dt_calc, correcao = correcao, 
                                                          porc_juro_contr = porc_juro_contr, dt_base_juro = dt_base_juro, 
                                                          dt_calc_juro = dt_calc_juro, juro_contr = juro_contr, porc_multa = porc_multa,
                                                           porc_juros = porc_juros, porc_pro_rata = porc_pro_rata, multa = multa, 
                                                          juros = juros, pro_rata = pro_rata, total = total, valor_devido = valor_devido, 
                                                          dias = dias, dt_recto = dt_recto, valor_pago = valor_pago, empresa = empresa, 
                                                          centro_custo = centro_custo, titulo_cliente = titulo_cliente, cliente = cliente, 
                                                          data_emissao = data_emissao, limite_correcao = limite_correcao, 
                                                          ultimo_reajuste = ultimo_reajuste, documento = documento, 
                                                          unidades = unidades, total_lanc = total_lanc, reparcelamento=reparcelamento))

            except ValueError:
                pass
    if len(Ato) > 0:
        
        parcelas = (calcular_parcelas(Ato, ValorAto,  'SINAL ATO', lista_vcto_ato))   
        for parcela in parcelas:
            condicoes.append(parcela)
    if len(Mensal) > 0:
        parcelas = (calcular_parcelas(Mensal, ValorMensal,   'MENSAL', lista_vcto_mensal))
        for parcela in parcelas:
            condicoes.append(parcela)
    if len(Semestrais) > 0:
        
        parcelas = (calcular_parcelas(Semestrais, ValorSemestrais,   "SEMESTRAL", lista_vcto_semestral))
        for parcela in parcelas:
            condicoes.append(parcela)
    if len(Bimestral) > 0:
        
        parcelas = (calcular_parcelas(Bimestral, ValorBimestral,  "BIMESTRAL", lista_vcto_bimestral ))
        for parcela in parcelas:
            condicoes.append(parcela)
    if len(Chaves) > 0:
        
        parcelas = (calcular_parcelas(Chaves, ValorChaves,   'CHAVESL', lista_vcto_chaves))
        for parcela in parcelas:
            condicoes.append(parcela)
    if len(Residuo) > 0:
        
        parcelas = ( calcular_parcelas(Residuo,ValorResiduo, "RESIDUO", lista_vcto_residuo ))
        for parcela in parcelas:
            condicoes.append(parcela)
    if len(Mensal2) > 0:
        
        parcelas = ( calcular_parcelas(Mensal2,ValorMensais2,  "MENSAL 2", lista_vcto_mensal2))
        for parcela in parcelas:
            condicoes.append(parcela)
    if len(Sinal) > 0:
        
        parcelas = ( calcular_parcelas(Sinal,ValorSinal, "SINAL", lista_vcto_sinal))
        for parcela in parcelas:
            condicoes.append(parcela)
    if len(Parc_inter) > 0:
        
        parcelas = ( calcular_parcelas(Parc_inter,ValorIntermediaria, "INTERMEDIÁRIA", lista_vcto_intermediaria))
        for parcela in parcelas:
            condicoes.append(parcela)
    if len(Parc_interm2) > 0:
        
        parcelas = ( calcular_parcelas(Parc_interm2,ValorIntermediaria2, "INTERMEDIÁRIA 2", lista_vcto_intermediaria2 ))
        for parcela in parcelas:
            condicoes.append(parcela)
    if len(Sinal_cart) > 0:
        
        parcelas = ( calcular_parcelas(Sinal_cart,ValorSinalCartao,  "SINAL CARTÃO", lista_vcto_sincart))
        for parcela in parcelas:
            condicoes.append(parcela)
    if len(Parcela_cart) > 0:
        
        parcelas = ( calcular_parcelas(Parcela_cart,ValorParcelaCartao,  "PARCELA CARTÃO", lista_vcto_parcart))
        for parcela in parcelas:
            condicoes.append(parcela)
    if len(cartao_cred) > 0:
        
        parcelas = ( calcular_parcelas(cartao_cred,ValorCartaoCredito, "CARTÃO DE CREDITO", lista_vcto_cartaocred ))
        for parcela in parcelas:
            condicoes.append(parcela)
    if len(trans_cred) > 0:
        
        parcelas = ( calcular_parcelas(trans_cred,ValorTransferenciaCredito, "TRANSFERENCIA DE CREDITO", lista_vcto_transcred))
        for parcela in parcelas:
            condicoes.append(parcela)
    if len(FinAss) > 0:
        
        parcelas = ( calcular_parcelas(FinAss,ValorFinanciamentoAss, "FINANCIAMENTO ASSOCIATIVO", lista_vcto_finass ))
        for parcela in parcelas:
            condicoes.append(parcela)
    if len(Anual) > 0:
        
        parcelas = ( calcular_parcelas(Anual,ValorAnual, "ANUAL", lista_vcto_anual))
        for parcela in parcelas:
            condicoes.append(parcela)
    if len(Fgts) > 0:
        
        parcelas = ( calcular_parcelas(Fgts,ValorFgts, "FGTS", lista_vcto_fgts) )
        for parcela in parcelas:
            condicoes.append(parcela)
    if len(Financiamento) > 0:   
        parcelas = ( calcular_parcelas(Financiamento,ValorFinanciamento, "FINANCIAMENTO", lista_vcto_financiamento))
        for parcela in parcelas:
            condicoes.append(parcela)
    if len(debitos) > 0:
        debito = round(sum(debitos), 2)
        condicoes.append(f"TOTAL DÉBITOS: {formatar_real(debito)} ({numero_por_extenso.monetario(debito)})")
    
    for condicao in condicoes:
        lista_comercial_condicoes.append(ClientesComercial(nome=cliente, tituloID = titulo_cliente, condicoes = condicao ))

    DadosComercial.objects.bulk_create(lista_comercial) 
    ClientesComercial.objects.bulk_create(lista_comercial_condicoes)    

#Renderiza a página de resultados de Comercial
def comercial(request):
    first = DadosComercial.objects.first()
    Soma_Par_Men2 = DadosComercial.objects.filter(tipo_condicao="Parcela Mensais 2").exclude(valor_devido=0).aggregate(Sum('valor_devido'))['valor_devido__sum']
    Soma_Ato = DadosComercial.objects.filter(tipo_condicao="Ato").exclude(valor_devido=0).aggregate(Sum('valor_devido'))['valor_devido__sum']
    Soma_Par_Mensais = DadosComercial.objects.filter(tipo_condicao="Parcelas Mensais").exclude(valor_devido=0).aggregate(Sum('valor_devido'))['valor_devido__sum']
    Soma_Par_Semestrais = DadosComercial.objects.filter(tipo_condicao="Parcelas Semestrais").exclude(valor_devido=0).aggregate(Sum('valor_devido'))['valor_devido__sum']
    Soma_Par_Bimestrais = DadosComercial.objects.filter(tipo_condicao="Parcelas Bimestrais").exclude(valor_devido=0).aggregate(Sum('valor_devido'))['valor_devido__sum']
    Soma_Ent_chaves = DadosComercial.objects.filter(tipo_condicao="Entrega das chaves").exclude(valor_devido=0).aggregate(Sum('valor_devido'))['valor_devido__sum']
    Soma_Resíduo = DadosComercial.objects.filter(tipo_condicao="Resíduo").exclude(valor_devido=0).aggregate(Sum('valor_devido'))['valor_devido__sum']
    Soma_Sinal = DadosComercial.objects.filter(tipo_condicao="Sinal").exclude(valor_devido=0).aggregate(Sum('valor_devido'))['valor_devido__sum']
    Soma_Par_Inter = DadosComercial.objects.filter(tipo_condicao="Parcelas Intermediária").exclude(valor_devido=0).aggregate(Sum('valor_devido'))['valor_devido__sum']
    Soma_Par_Inter_2 = DadosComercial.objects.filter(tipo_condicao="Parcelas Intermediária 2").exclude(valor_devido=0).aggregate(Sum('valor_devido'))['valor_devido__sum']
    Soma_Sin_Cartão = DadosComercial.objects.filter(tipo_condicao="Sinal Cartão").exclude(valor_devido=0).aggregate(Sum('valor_devido'))['valor_devido__sum']
    Soma_Par_Cartão = DadosComercial.objects.filter(tipo_condicao="Parcela Cartão").exclude(valor_devido=0).aggregate(Sum('valor_devido'))['valor_devido__sum']
    Soma_Car_Crédito = DadosComercial.objects.filter(tipo_condicao="Carta de Crédito").exclude(valor_devido=0).aggregate(Sum('valor_devido'))['valor_devido__sum']
    Soma_Transf_Crédito = DadosComercial.objects.filter(tipo_condicao="Transferencia Crédito").exclude(valor_devido=0).aggregate(Sum('valor_devido'))['valor_devido__sum']
    Soma_Fin_Associativo = DadosComercial.objects.filter(tipo_condicao="Financiamento Associativo").exclude(valor_devido=0).aggregate(Sum('valor_devido'))['valor_devido__sum']
    Soma_Anual = DadosComercial.objects.filter(tipo_condicao="Anual").exclude(valor_devido=0).aggregate(Sum('valor_devido'))['valor_devido__sum']
    Soma_FGTS = DadosComercial.objects.filter(tipo_condicao="FGTS").exclude(valor_devido=0).aggregate(Sum('valor_devido'))['valor_devido__sum']
    Soma_Financiamento = DadosComercial.objects.filter(tipo_condicao="Financiamento").exclude(valor_devido=0).aggregate(Sum('valor_devido'))['valor_devido__sum']
    teste = DadosComercial.objects.exclude(total_lanc=None)
    total_lanc = (teste[0].total_lanc)
    try:
        Soma_Financiamento_pago = round(DadosComercial.objects.filter(tipo_condicao="Financiamento").exclude(valor_pago=0).aggregate(Sum('valor_pago'))['valor_pago__sum'], 2)
    except TypeError:
        Soma_Financiamento_pago = None


    return render(request, 'comercial.html', {'dados': DadosComercial.objects.all(), 'first': first, 'total_lanc': formatar_real(total_lanc), 
                                              'condicoes': ClientesComercial.objects.all(),'Total_Par_Men2': formatar_real(Soma_Par_Men2 ),'Total_Ato': formatar_real(Soma_Ato ),
                                              'Total_Par_Mensais': formatar_real(Soma_Par_Mensais ),'Total_Par_Semestrais': formatar_real(Soma_Par_Semestrais ),
                                              'Total_Par_Bimestrais': formatar_real(Soma_Par_Bimestrais ),'Total_Ent_chave': formatar_real(Soma_Ent_chaves),
                                              'Total_Sinal': formatar_real(Soma_Sinal ),'Total_Par_Inter': formatar_real(Soma_Par_Inter ),'Total_Par_Inter_2': formatar_real(Soma_Par_Inter_2 ),
                                              'Total_Sin_Cartão': formatar_real(Soma_Sin_Cartão ),'Total_Par_Cartão': formatar_real(Soma_Par_Cartão ),'Total_Car_Credit': formatar_real(Soma_Car_Crédito),
                                              'Total_Transf_Credito': formatar_real(Soma_Transf_Crédito ),'Total_Fin_Associativo': formatar_real(Soma_Fin_Associativo ),'Total_Anual': formatar_real(Soma_Anual),
                                              'Total_FGTS': formatar_real(Soma_FGTS ),'Total_Financiamento': formatar_real(Soma_Financiamento), 'total_residuo': formatar_real(Soma_Resíduo), 
                                              'finan_pago': Soma_Financiamento_pago, })
#Upload dos arquivos de Comercial
def upload_comercial(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            arquivo = request.FILES['arquivo']
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                for chunk in arquivo.chunks():
                    tmp.write(chunk)
            dados_xls = pd.read_excel(tmp.name)
            os.unlink(tmp.name)
            dados_comercial(dados_xls, request)
            return(redirect('comercial'))
        else:
            return(redirect('upload-page-comercial'))
    else:
        return(redirect('upload-page-comercial'))
    
