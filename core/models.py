from django.db import models

class Dados(models.Model):
    id = models.IntegerField(primary_key=True)
    nome_obra = models.CharField(max_length=100, null=True, blank=True)
    item = models.IntegerField(null=True, blank=True)
    cod_sol_compra = models.IntegerField(null=True, blank=True)
    cod_obra = models.IntegerField(null=True, blank=True)
    cod_insumo = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=50, null=True)
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
    titles = models.CharField(max_length=100, null=True, blank=True)
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
    nome_obra = models.CharField(max_length=100, null=True)

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

