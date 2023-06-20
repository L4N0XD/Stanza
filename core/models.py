from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
import os



class Minutas(models.Model):
    nome = models.CharField(max_length=100, primary_key=True)
    arquivo = models.FileField(null=True, default=None)




class Dados(models.Model):
    id = models.IntegerField(primary_key=True)
    nome_obra = models.CharField(max_length=100, null=True, blank=True)
    item = models.IntegerField(null=True, blank=True)
    cod_sol_compra = models.IntegerField(null=True, blank=True)
    cod_obra = models.IntegerField(null=True, blank=True)
    cod_insumo = models.IntegerField(null=True, blank=True)
    status_entregue = models.CharField(max_length=50, null=True)
    status_compra = models.CharField(max_length=50, null=True)
    desc_insumo = models.CharField(max_length=100, null=True,blank=True)
    quant_sol = models.CharField(max_length=50, null=True, blank=True)
    data_sol = models.DateField(null=True, blank=True)
    data_sol_cheg_obra = models.DateField(null=True, blank=True)
    num_ped_compra = models.IntegerField(null=True, blank=True)
    data_emissao_pc = models.DateField(null=True, blank=True)
    prev_entrega = models.DateField(null=True, blank=True)
    quant_entregue = models.CharField(max_length=50, null=True, blank=True)
    saldo = models.CharField(max_length=50, null=True, blank=True)
    data_NF = models.DateField(null=True, blank=True)
    cod_NF = models.CharField(max_length=50, null=True, blank=True)
    data_entrada_obra = models.DateField(null=True, blank=True)
    data_vencimento = models.DateField(null=True, blank=True)
    total_sols_compra = models.IntegerField(null=True, blank=True)
    data_prev_final = models.DateField(null=True, blank=True)

class Operations(models.Model):
    id = models.AutoField(primary_key=True)
    atrasados = models.IntegerField(null=True, blank=True)
    prazo = models.IntegerField(null=True, blank=True)
    total_atendido = models.IntegerField(null=True, blank=True)
    indeterminados = models.IntegerField(null=True, blank=True)

class Insumos(models.Model):
    codigo_insumo = models.IntegerField(primary_key=True)
    nome_do_insumo = models.CharField(max_length=150)
    qtd_dias = models.IntegerField(null=True, blank=True)

class DadosRH(models.Model):
    cpf = models.CharField(primary_key=True, max_length=100)
    nome = models.CharField(max_length=100)
    dias_trabalhados = models.IntegerField()
    dias_contabilizados = models.IntegerField(null=True,)
    valor = models.IntegerField()
    pagar = models.DecimalField(null=True,max_digits=10, decimal_places=2)
    total = models.DecimalField(null=True,max_digits=10, decimal_places=2)
    total_atualizado = models.DecimalField(null=True,max_digits=10, decimal_places=2)
    valor_desconto_colaborador = models.DecimalField(null=True, max_digits=10, decimal_places=2)
    salario = models.DecimalField(null=True, max_digits=10, decimal_places=2)
    matricula = models.CharField(max_length=30, null=True)
    nome_obra = models.CharField(max_length=100, null=True)
    codigo_desconto_vt = models.CharField(max_length=100, null=True)

class Totais(models.Model):
    nome_obra = models.CharField(primary_key=True, max_length=100)
    total = models.CharField(max_length=100)
    total_pagar = models.CharField(max_length=100)
    total_descontos = models.CharField(max_length=100)
    
class DadosAjuCard(models.Model):
    cpf = models.CharField(primary_key=True, max_length=100)
    nome = models.CharField(max_length=100, null=False)
    cartao = models.CharField(max_length=100, null=False)
    saldoA = models.DecimalField(null=True,max_digits=10, decimal_places=2)
    saldo = models.DecimalField(null=True,max_digits=10, decimal_places=2)
    total_saldo = models.DecimalField(null=True,max_digits=10, decimal_places=2)
    recarga = models.DecimalField(null=True,max_digits=10, decimal_places=2)
    total = models.DecimalField(null=True,max_digits=10, decimal_places=2)
    total_atualizado = models.DecimalField(null=True,max_digits=10, decimal_places=2)
    data_planilha = models.DateField(null=True, blank=True)
    nome_obra = models.CharField(max_length=100, null=True)

class DadosVT(models.Model):
        empresa = models.IntegerField(null=True, blank=True)
        admissao =models.DateField(null=True, blank=True)
        nome = models.CharField(max_length=150, null=True, blank=True)
        cpf = models.CharField(max_length=50, primary_key=True)
        id = models.CharField(max_length=150, null=True, blank=True)
        mae =models.CharField(max_length=150, null=True, blank=True)
        nasc = models.DateField(null=True, blank=True)
        cep = models.CharField(max_length=150, null=True, blank=True)
        endereco = models.CharField(max_length=150, null=True, blank=True)
        numero_endereco = models.IntegerField(null=True, blank=True)
        cidade =models.CharField(max_length=150, null=True, blank=True)
        bairro = models.CharField(max_length=150, null=True, blank=True)

class DadosComercial(models.Model):
    id_value = models.AutoField(primary_key=True)
    par = models.CharField(max_length=10, null=True, blank=True)
    data_vcto = models.DateField(null=True, blank=True)
    tipo_condicao = models.CharField(max_length=50, null=True, blank=True)
    id = models.IntegerField(null=True, blank=True)
    vl_original = models.DecimalField(null=True,blank=True, max_digits=10, decimal_places=2)
    ind_dt_base = models.DecimalField(null=True,blank=True, max_digits=10, decimal_places=2)
    ind_dt_calc = models.DecimalField(null=True,blank=True, max_digits=10, decimal_places=2)
    correcao = models.DecimalField(null=True,blank=True, max_digits=10, decimal_places=2)
    porc_juro_contr = models.DecimalField(null=True,blank=True, max_digits=10, decimal_places=2)
    dt_base_juro = models.DecimalField(null=True,blank=True, max_digits=10, decimal_places=2)
    dt_calc_juro = models.DecimalField(null=True,blank=True, max_digits=10, decimal_places=2)
    juro_contr = models.DecimalField(null=True,blank=True, max_digits=10, decimal_places=2)
    porc_multa = models.DecimalField(null=True,blank=True, max_digits=10, decimal_places=2)
    porc_juros = models.DecimalField(null=True,blank=True, max_digits=10, decimal_places=2)
    porc_pro_rata = models.DecimalField(null=True,blank=True, max_digits=10, decimal_places=2)
    multa = models.DecimalField(null=True,blank=True, max_digits=10, decimal_places=2)
    juros = models.DecimalField(null=True,blank=True, max_digits=10, decimal_places=2)
    pro_rata = models.DecimalField(null=True,blank=True, max_digits=10, decimal_places=2)
    total = models.DecimalField(null=True,blank=True, max_digits=10, decimal_places=2)
    valor_devido = models.DecimalField(null=True,blank=True, max_digits=10, decimal_places=2)
    dias = models.IntegerField(null=True,blank=True)
    dt_recto = models.DateField(null=True, blank=True)
    valor_pago = models.DecimalField(null=True,blank=True, max_digits=10, decimal_places=2)
    empresa = models.CharField(max_length=100, null=True, blank=True, )
    centro_custo = models.CharField(max_length=100, null=True, blank=True)
    titulo_cliente = models.IntegerField(null=True, blank=True)
    cliente = models.CharField(max_length=100, null=True, blank=True)
    data_emissao = models.DateField(null=True, blank=True)
    limite_correcao = models.DateField(null=True, blank=True)
    ultimo_reajuste = models.DateField(null=True, blank=True)
    documento = models.CharField(max_length=100, null=True, blank=True)
    unidades = models.CharField(max_length=100, null=True, blank=True)
    total_lanc = models.DecimalField(null=True,blank=True, max_digits=10, decimal_places=2)
    reparcelamento = models.BooleanField(default=False)
    status = models.CharField(max_length=100, null=True, default=None)

class ClientesComercial(models.Model):
    nome = models.CharField(max_length=50, null=True, blank=True)
    tituloID = models.IntegerField(null=True, blank=True)
    id = models.AutoField(primary_key=True)
    condicoes = models.CharField(max_length=150)

class ExtendedUser(User):
    aprovado = models.BooleanField(default=False)
    grupo_rh = models.BooleanField(default=False)
    grupo_suprimentos = models.BooleanField(default=False)
    grupo_comercial = models.BooleanField(default=False)
