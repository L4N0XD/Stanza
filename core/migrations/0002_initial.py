# Generated by Django 4.2 on 2023-06-15 20:08

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClientesComercial',
            fields=[
                ('nome', models.CharField(blank=True, max_length=50, null=True)),
                ('tituloID', models.IntegerField(blank=True, null=True)),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('condicoes', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='Dados',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('nome_obra', models.CharField(blank=True, max_length=100, null=True)),
                ('item', models.IntegerField(blank=True, null=True)),
                ('cod_sol_compra', models.IntegerField(blank=True, null=True)),
                ('cod_obra', models.IntegerField(blank=True, null=True)),
                ('cod_insumo', models.IntegerField(blank=True, null=True)),
                ('status_entregue', models.CharField(max_length=50, null=True)),
                ('status_compra', models.CharField(max_length=50, null=True)),
                ('desc_insumo', models.CharField(blank=True, max_length=100, null=True)),
                ('quant_sol', models.CharField(blank=True, max_length=50, null=True)),
                ('data_sol', models.DateField(blank=True, null=True)),
                ('data_sol_cheg_obra', models.DateField(blank=True, null=True)),
                ('num_ped_compra', models.IntegerField(blank=True, null=True)),
                ('data_emissao_pc', models.DateField(blank=True, null=True)),
                ('prev_entrega', models.DateField(blank=True, null=True)),
                ('quant_entregue', models.CharField(blank=True, max_length=50, null=True)),
                ('saldo', models.CharField(blank=True, max_length=50, null=True)),
                ('data_NF', models.DateField(blank=True, null=True)),
                ('cod_NF', models.CharField(blank=True, max_length=50, null=True)),
                ('data_entrada_obra', models.DateField(blank=True, null=True)),
                ('data_vencimento', models.DateField(blank=True, null=True)),
                ('total_sols_compra', models.IntegerField(blank=True, null=True)),
                ('data_prev_final', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DadosAjuCard',
            fields=[
                ('cpf', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('nome', models.CharField(max_length=100)),
                ('cartao', models.CharField(max_length=100)),
                ('saldoA', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('saldo', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('total_saldo', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('recarga', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('total_atualizado', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('data_planilha', models.DateField(blank=True, null=True)),
                ('nome_obra', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DadosComercial',
            fields=[
                ('id_value', models.AutoField(primary_key=True, serialize=False)),
                ('par', models.CharField(blank=True, max_length=10, null=True)),
                ('data_vcto', models.DateField(blank=True, null=True)),
                ('tipo_condicao', models.CharField(blank=True, max_length=50, null=True)),
                ('id', models.IntegerField(blank=True, null=True)),
                ('vl_original', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('ind_dt_base', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('ind_dt_calc', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('correcao', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('porc_juro_contr', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('dt_base_juro', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('dt_calc_juro', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('juro_contr', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('porc_multa', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('porc_juros', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('porc_pro_rata', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('multa', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('juros', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('pro_rata', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('total', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('valor_devido', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('dias', models.IntegerField(blank=True, null=True)),
                ('dt_recto', models.DateField(blank=True, null=True)),
                ('valor_pago', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('empresa', models.CharField(blank=True, max_length=100, null=True)),
                ('centro_custo', models.CharField(blank=True, max_length=100, null=True)),
                ('titulo_cliente', models.IntegerField(blank=True, null=True)),
                ('cliente', models.CharField(blank=True, max_length=100, null=True)),
                ('data_emissao', models.DateField(blank=True, null=True)),
                ('limite_correcao', models.DateField(blank=True, null=True)),
                ('ultimo_reajuste', models.DateField(blank=True, null=True)),
                ('documento', models.CharField(blank=True, max_length=100, null=True)),
                ('unidades', models.CharField(blank=True, max_length=100, null=True)),
                ('total_lanc', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('reparcelamento', models.BooleanField(default=False)),
                ('status', models.CharField(default=None, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DadosRH',
            fields=[
                ('cpf', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('nome', models.CharField(max_length=100)),
                ('dias_trabalhados', models.IntegerField()),
                ('dias_contabilizados', models.IntegerField(null=True)),
                ('valor', models.IntegerField()),
                ('pagar', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('total_atualizado', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('valor_desconto_colaborador', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('salario', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('matricula', models.CharField(max_length=30, null=True)),
                ('nome_obra', models.CharField(max_length=100, null=True)),
                ('codigo_desconto_vt', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DadosVT',
            fields=[
                ('empresa', models.IntegerField(blank=True, null=True)),
                ('admissao', models.DateField(blank=True, null=True)),
                ('nome', models.CharField(blank=True, max_length=150, null=True)),
                ('cpf', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('id', models.CharField(blank=True, max_length=150, null=True)),
                ('mae', models.CharField(blank=True, max_length=150, null=True)),
                ('nasc', models.DateField(blank=True, null=True)),
                ('cep', models.CharField(blank=True, max_length=150, null=True)),
                ('endereco', models.CharField(blank=True, max_length=150, null=True)),
                ('numero_endereco', models.IntegerField(blank=True, null=True)),
                ('cidade', models.CharField(blank=True, max_length=150, null=True)),
                ('bairro', models.CharField(blank=True, max_length=150, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ExtendedUser',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('aprovado', models.BooleanField(default=False)),
                ('grupo_rh', models.BooleanField(default=False)),
                ('grupo_suprimentos', models.BooleanField(default=False)),
                ('grupo_comercial', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Insumos',
            fields=[
                ('codigo_insumo', models.IntegerField(primary_key=True, serialize=False)),
                ('nome_do_insumo', models.CharField(max_length=150)),
                ('qtd_dias', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Minutas',
            fields=[
                ('nome', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('arquivo', models.FileField(default=None, null=True, upload_to='minutas/')),
            ],
        ),
        migrations.CreateModel(
            name='Operations',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('atrasados', models.IntegerField(blank=True, null=True)),
                ('prazo', models.IntegerField(blank=True, null=True)),
                ('total_atendido', models.IntegerField(blank=True, null=True)),
                ('indeterminados', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Totais',
            fields=[
                ('nome_obra', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('total', models.CharField(max_length=100)),
                ('total_pagar', models.CharField(max_length=100)),
                ('total_descontos', models.CharField(max_length=100)),
            ],
        ),
    ]