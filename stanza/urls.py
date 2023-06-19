"""
URL configuration for stanza project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.views.generic import RedirectView
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('logar/', views.logar, name='logar'),
    path('index/', views.index, name='index'),
    path('', RedirectView.as_view(url='/index/', permanent=True)),
    path('entrar/', views.entrar, name='entrar'),
    path('sair/', views.sair, name='sair'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('solicitacao/', views.solicitar_acesso, name='solicitacao'),
    path('upload-page-obras/', views.upload_page_obras, name='upload-page-obras'),
    path('upload-import-vt/', views.upload_import_vt, name='upload-import-vt'),
    path('import-vt/', views.import_vt, name='import-vt'),
    path('upload-page-comercial/', views.upload_page_comercial),
    path('comercial/', views.comercial, name='comercial'),
    path('upload-page-rh/', views.upload_page_rh, name='upload-page-rh'),
    path('results-rh/', views.results_rh, name='results-rh'),
    path('results-obras/', views.results_obras, name='results-obras'),
    path('ajax-comercial/', views.dados_do_modelo_comercial),
    path('filtrar/', views.filtrar, name='filtrar'),
    path('upload/', views.upload, name='upload'),
    path('upload-rh/', views.upload_rh, name='upload-rh'),
    path('upload-comercial/', views.upload_comercial, name='upload-comercial'),
    path('upload-vt/', views.upload_vt, name='upload-vt'),
    path('insumos/', views.cadastrar_insumo, name='insumos'),
    path('download_table/<str:nome_obra>/', views.download_table, name='download_table'),
    path('save_data/', views.save_data, name='save_data'),
    path('download_txt_analise/<str:nome_obra>/', views.download_txt_analise, name='download_txt_analise'),
    path('download_txt_desconto/<str:nome_obra>/', views.download_txt_desconto, name='download_txt_desconto'),
    path('download_txt_vt/', views.download_txt_vt, name='download_txt_vt'),
    path('insumo/editar/<int:codigo_insumo>/', views.editar_insumo, name='editar_insumo'),
    path('insumo/excluir/<int:codigo_insumo>/', views.excluir_insumo, name='excluir_insumo'),
    path('filtrar-obras/', views.filtrar_obras, name='filtrar-obras'),
    path('conteudo-prazo/<str:nome_obra>/', views.conteudo_prazo, name='conteudo-prazo'),
    path('conteudo-atraso/<str:nome_obra>/', views.conteudo_atraso, name='conteudo-atraso'),
    path('conteudo-indeterminados/<str:nome_obra>/', views.conteudo_indeterminados, name='conteudo-indeterminados'),
    path('erro/<str:msg>/', views.erro, name='erro'),
    path('selecionar-minutas/', views.selecionar_minutas, name='selecionar-minutas'),
    path('upload-minutas/', views.upload_minutas, name='upload-minutas'),
    path('minuta-selecionada/', views.minuta_selecionada, name='minuta-selecionada'),

]
