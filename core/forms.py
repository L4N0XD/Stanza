from django import forms

class FiltroForm(forms.Form):
    data_inicial = forms.DateField(label='', required=True)
    data_final = forms.DateField(label='', required=True)
    filtro = forms.CharField(widget=forms.HiddenInput(), required=True)


class UploadForm(forms.Form):
    arquivo = forms.FileField(required=True)

class UploadRH(forms.Form):
    arquivo1 = forms.FileField(required=True)
    arquivo2 = forms.FileField(required=True)

class AddInsumoForm(forms.Form):
    codigo_insumo = forms.IntegerField(label='', required=True)
    nome_do_insumo = forms.CharField(label='')
    qtd_dias = forms.IntegerField(label='')