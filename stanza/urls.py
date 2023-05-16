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
    path('index/', views.index, name='index'),
    path('logar/', views.logar, name='logar'),
    path('entrar/', views.entrar, name='entrar'),
    path('sair/', views.sair, name='sair'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('graphic/', views.graphic, name='graphic'),
    path('upload-page-obras/', views.upload_page_obras, name='upload-page-obras'),
    path('upload-import-vt/', views.upload_import_vt, name='upload-import-vt'),
    path('import-vt/', views.import_vt, name='import-vt'),
    path('upload-page-comercial/', views.upload_page_comercial),
    path('comercial/', views.comercial, name='comercial'),
    path('upload-page-rh/', views.upload_page_rh, name='upload-page-rh'),
    path('results-rh/', views.results_rh, name='results-rh'),
    path('ajax/', views.dados_do_modelo),
    path('ajax-comercial/', views.dados_do_modelo_comercial),
    path('filtrar/', views.filtrar, name='filtrar'),
    path('upload/', views.upload, name='upload'),
    path('upload-rh/', views.upload_rh, name='upload-rh'),
    path('upload-comercial/', views.upload_comercial, name='upload-comercial'),
    path('upload-vt/', views.upload_vt, name='upload-vt'),
    path('insumos/', views.cadastrar_insumo, name='insumos'),
    path('', RedirectView.as_view(url='/logar/', permanent=True)),
    path('download_table/<str:nome_obra>/', views.download_table, name='download_table'),
    path('save_data/', views.save_data, name='save_data'),
    path('download_txt/<str:nome_obra>/', views.download_txt, name='download_txt'),
    path('download_txt_vt/', views.download_txt_vt, name='download_txt_vt'),
]
