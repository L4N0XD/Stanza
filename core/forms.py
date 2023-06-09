from django import forms

class FiltroForm(forms.Form):
    data_inicial = forms.DateField(label='', required=True)
    data_final = forms.DateField(label='', required=True)
    filtro = forms.CharField(widget=forms.HiddenInput(), required=True)
    filtrar_nome_da_obra = forms.CharField(widget=forms.HiddenInput(), required=True)

class FiltrarObras(forms.Form):
    nome_da_obra = forms.CharField(widget=forms.HiddenInput(), required=True)

class MinutaSelecionada(forms.Form):
    nome_minuta = forms.CharField(widget=forms.HiddenInput(), required=True)


class UploadForm(forms.Form):
    arquivo = forms.FileField(required=True)

class UploadRH(forms.Form):
    arquivo0 = forms.FileField(required=True)
    arquivo1 = forms.FileField(required=True)
    arquivo2 = forms.FileField(required=True)
    diasUteis = forms.IntegerField(label='')

class AddInsumoForm(forms.Form):
    codigo_insumo = forms.IntegerField(label='', required=True)
    nome_do_insumo = forms.CharField(label='')
    qtd_dias = forms.IntegerField(label='')