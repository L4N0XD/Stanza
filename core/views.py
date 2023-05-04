from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from core.models import Dados, Operations, Insumos, DadosAjuCard, DadosRH, Totais, DadosComercial
from .forms import FiltroForm, UploadForm, AddInsumoForm, UploadRH
from datetime import datetime, timedelta
import tempfile, os, math, time
import pandas as pd
import numpy as np



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
#Upload dos arquivos de VT
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
    formatar = '{:,.0f}'.format(value).replace(',','.')
    total = (f'R${formatar},00')
    return total
#Renderiza a página de resultados do VT
def results_rh(request):
    dados = Totais.objects.all()
    data = DadosAjuCard.objects.all().first()
    date_string = str(data.data_planilha)
    date_object = datetime.strptime(date_string, '%Y-%m-%d')
    new_date = date_object.strftime('%d-%m-%Y')
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
                                                   'data_planilha': new_date, 'nome_obra': nome_obra, 'obras': obras,})
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
#Renderiza a página de upload dos arquivos de VT
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
  
def upload_page_comercial(request):
    DadosComercial.objects.all().delete()
    print('Dados excluidos!')
    return render(request, 'upload-page-comercial.html')

def dados_comercial(dados_xls, request):
    empresa = str(dados_xls.iloc[3, 5])
    centro_custo = str(dados_xls.iloc[4, 5])
    titulo_cliente = int(dados_xls.iloc[4, 25])
    cliente = str(dados_xls.iloc[7, 5])
    data_emissão = format_date(str(dados_xls.iloc[5, 5]))
    limite_correcao = format_date(str(dados_xls.iloc[6, 5]))
    ultimo_reajuste = format_date(str(dados_xls.iloc[6, 25]))
    documento = str(dados_xls.iloc[8, 5])
    unidades = str(dados_xls.iloc[8, 25])
    total_lanc = str(dados_xls.iloc[71, 9])
    lista_comercial = []

    for index, row in dados_xls.iterrows():
        if str(row[0]) != '(C) - Parcela enviada para a cobrança escritural.':
            
            if 11 < index:
                par = str(row[0]) if isinstance(row[2], str) else None
                data_vcto = format_date(str(row[2])) if isinstance(row[2], str) else None
                tipo_condicao = str(row[4]) if isinstance(row[4], str) else None
                id = (row[7]) 
                vl_original = float(row[9]) if isinstance(row[9], (int, float)) and not np.isnan(row[9]) else None
                ind_dt_base = float(row[13]) if isinstance(row[13], (int, float)) and not np.isnan(row[13]) else None
                ind_dt_calc = float(row[15]) if isinstance(row[15], (int, float)) and not np.isnan(row[15]) else None
                correcao = float(row[17]) if isinstance(row[17], (int, float)) and not np.isnan(row[17]) else None
                porc_juro_contr = float(row[20]) if isinstance(row[20], (int, float)) and not np.isnan(row[20]) else 0
                dt_base_juro = float(row[21]) if isinstance(row[21], (int, float)) and not np.isnan(row[21]) else 0
                dt_calc_juro = float(row[23]) if isinstance(row[23], (int, float)) and not np.isnan(row[23]) else 0
                juro_contr = float(row[24]) if isinstance(row[24], (int, float)) and not np.isnan(row[24]) else None
                porc_multa = float(row[26]) if isinstance(row[26], (int, float)) and not np.isnan(row[26]) else None
                porc_juros = float(row[28]) if isinstance(row[28], (int, float)) and not np.isnan(row[28]) else None
                porc_pro_rata = float(row[30]) if isinstance(row[30], (int, float)) and not np.isnan(row[30]) else None
                multa = float(row[31]) if isinstance(row[31], (int, float)) and not np.isnan(row[31]) else None
                juros = float(row[33]) if isinstance(row[33], (int, float)) and not np.isnan(row[33]) else None
                pro_rata = float(row[34]) if isinstance(row[34], (int, float)) and not np.isnan(row[34]) else None
                total = (row[36]) if isinstance(row[36], (int, float)) and not np.isnan(row[36]) else None
                valor_devido = float(row[37]) if isinstance(row[37], (int, float)) and not np.isnan(row[37]) else None
                dias = row[40]
                dt_recto = format_date(str(row[42])) if isinstance(row[42], str) else None
                valor_pago = float(row[43]) if isinstance(row[43], (int, float)) and not np.isnan(row[43]) else None
                if par is not None:
                    lista_comercial.append(DadosComercial(par=par, data_vcto = data_vcto, tipo_condicao = tipo_condicao, 
                                                      id = id, vl_original = vl_original, ind_dt_base = ind_dt_base, 
                                                      ind_dt_calc = ind_dt_calc, correcao = correcao, 
                                                      porc_juro_contr = porc_juro_contr, dt_base_juro = dt_base_juro, 
                                                      dt_calc_juro = dt_calc_juro, juro_contr = juro_contr, porc_multa = porc_multa,
                                                       porc_juros = porc_juros, porc_pro_rata = porc_pro_rata, multa = multa, 
                                                      juros = juros, pro_rata = pro_rata, total = total, valor_devido = valor_devido, 
                                                      dias = dias, dt_recto = dt_recto, valor_pago = valor_pago, empresa = empresa, 
                                                      centro_custo = centro_custo, titulo_cliente = titulo_cliente, cliente = cliente, 
                                                      data_emissão = data_emissão, limite_correcao = limite_correcao, 
                                                      ultimo_reajuste = ultimo_reajuste, documento = documento, 
                                                      unidades = unidades, total_lanc = total_lanc))
                #elif par is None and valor_pago:
                #    lista_comercial.append(DadosComercial( dt_recto = dt_recto, valor_pago = valor_pago))

        else:
            break
    DadosComercial.objects.bulk_create(lista_comercial) 

def comercial(request):
    first = DadosComercial.objects.first()
    return render(request, 'comercial.html', {'dados': DadosComercial.objects.all(), 'first': first, 'total_lanc': formatar_real(first.total_lanc)})

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
    
