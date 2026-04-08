from django.contrib import admin
from django.urls import path, include
from inicio import views 

urlpatterns = [
    # --- ADMINISTRACIÓN Y AUTH ---
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('registro/', views.registro, name='registro'),
    
    # --- RUTAS DE GASTOS (DASHBOARD PRINCIPAL) ---
    path('', views.home, name='home'),
    path('eliminar/<int:id>/', views.eliminar_registro, name='eliminar'),
    path('editar/<int:id>/', views.editar_registro, name='editar'),
    
    # --- RUTAS DE RESIDENTES ---
    path('residentes/', views.lista_residentes, name='residentes'),
    path('residentes/editar/<int:id>/', views.editar_residente, name='editar_residente'),
    path('residentes/eliminar/<int:id>/', views.eliminar_residente, name='eliminar_residente'),
    
    # --- RUTAS DE PAGOS ---
    # Ver historial del residente
    path('residente/<int:residente_id>/historial/', views.historial_pagos, name='historial_pagos'),
    
    # Procesar el nuevo pago
    path('residente/<int:residente_id>/registrar-pago/', views.registrar_pago, name='registrar_pago'),

    # --- NUEVA RUTA: GENERACIÓN DE PDF ---
    # Esta ruta conecta con la función exportar_historial_pdf que agregamos en views.py
    path('residente/<int:residente_id>/pdf/', views.exportar_historial_pdf, name='descargar_pdf'),
]