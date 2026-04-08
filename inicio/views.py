from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.db.models import Sum
from django.contrib import messages
from django.http import HttpResponse
from .models import Gasto, Residente, Pago

# Para el PDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

# --- MOTOR DE FLUJO DE CAJA ---
def obtener_balance_total(usuario):
    total_recaudado = Pago.objects.filter(pagado=True).aggregate(Sum('monto'))['monto__sum'] or 0
    total_gastado = Gasto.objects.filter(usuario=usuario).aggregate(Sum('monto'))['monto__sum'] or 0
    return {
        'total_recaudado': total_recaudado,
        'total_gastado': total_gastado,
        'saldo_disponible': total_recaudado - total_gastado
    }

# --- VISTAS DE GASTOS ---
@login_required
def home(request):
    if request.method == 'POST':
        try:
            monto_raw = request.POST.get('monto', '0').replace('.', '').replace(',', '')
            with transaction.atomic():
                Gasto.objects.create(
                    usuario=request.user, 
                    titulo=request.POST.get('titulo'), 
                    monto=int(monto_raw),
                    categoria=request.POST.get('categoria'),
                    descripcion=request.POST.get('descripcion'),
                    fecha_gasto=request.POST.get('fecha') or None
                )
            messages.success(request, "Gasto registrado.")
        except ValueError:
            messages.error(request, "Monto inválido.")
        return redirect('home')

    balance = obtener_balance_total(request.user)
    registros = Gasto.objects.filter(usuario=request.user).order_by('-fecha_gasto')
    return render(request, 'inicio/dashboard.html', {'registros': registros, **balance})

@login_required
def editar_registro(request, id):
    gasto = get_object_or_404(Gasto, id=id, usuario=request.user)
    if request.method == 'POST':
        monto_raw = request.POST.get('monto', '0').replace('.', '').replace(',', '')
        gasto.titulo = request.POST.get('titulo')
        gasto.monto = int(monto_raw)
        gasto.categoria = request.POST.get('categoria')
        gasto.fecha_gasto = request.POST.get('fecha') or None
        gasto.descripcion = request.POST.get('descripcion')
        gasto.save()
        return redirect('home')
    
    # Aseguramos enviar saldo_disponible para el JavaScript del HTML
    contexto = {'registro': gasto}
    contexto.update(obtener_balance_total(request.user))
    return render(request, 'inicio/editar.html', contexto)

@login_required
def eliminar_registro(request, id):
    """SOLUCIÓN AL AttributeError: eliminar_registro"""
    gasto = get_object_or_404(Gasto, id=id, usuario=request.user)
    gasto.delete()
    return redirect('home')

# --- GESTIÓN DE RESIDENTES ---
@login_required
def lista_residentes(request):
    """SOLUCIÓN AL AttributeError: residentes (lista)"""
    if request.method == 'POST':
        Residente.objects.create(
            nombre=request.POST.get('nombre'),
            apellido=request.POST.get('apellido'),
            rut=request.POST.get('rut'),
            departamento=request.POST.get('departamento'),
            torre=request.POST.get('torre')
        )
        return redirect('residentes')
    return render(request, 'inicio/residentes.html', {'residentes': Residente.objects.all()})

@login_required
def editar_residente(request, id):
    residente = get_object_or_404(Residente, id=id)
    if request.method == 'POST':
        residente.nombre = request.POST.get('nombre')
        residente.apellido = request.POST.get('apellido')
        residente.save()
        return redirect('residentes')
    return render(request, 'inicio/editar_residente.html', {'residente': residente})

@login_required
def eliminar_residente(request, id):
    get_object_or_404(Residente, id=id).delete()
    return redirect('residentes')

# --- PAGOS Y PDF ---
@login_required
def registrar_pago(request, residente_id):
    residente = get_object_or_404(Residente, id=residente_id)
    if request.method == 'POST':
        try:
            # SOLUCIÓN AL ValueError: '10.000'
            monto_raw = request.POST.get('monto', '0').replace('.', '').replace(',', '')
            Pago.objects.create(
                residente=residente,
                monto=int(monto_raw),
                mes_correspondiente=request.POST.get('fecha'),
                pagado=True
            )
            messages.success(request, "Pago registrado.")
        except ValueError:
            messages.error(request, "Error en el monto.")
    return redirect('historial_pagos', residente_id=residente.id)

@login_required
def historial_pagos(request, residente_id):
    """SOLUCIÓN AL AttributeError: historial_pagos"""
    residente = get_object_or_404(Residente, id=residente_id)
    pagos = Pago.objects.filter(residente=residente).order_by('-mes_correspondiente')
    return render(request, 'inicio/historial.html', {'residente': residente, 'pagos': pagos})

@login_required
def exportar_historial_pdf(request, residente_id):
    residente = get_object_or_404(Residente, id=residente_id)
    pagos = Pago.objects.filter(residente=residente)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Historial_{residente.apellido}.pdf"'
    
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    
    # Cabecera
    p.setFillColor(colors.HexColor("#0D6EFD"))
    p.rect(0, height - 80, width, 80, fill=1)
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 20)
    p.drawString(40, height - 50, f"CONDO-SMART IA - REPORTE: {residente.nombre} {residente.apellido}")
    
    p.showPage()
    p.save()
    return response

# --- AUTENTICACIÓN ---
def registro(request):
    """SOLUCIÓN AL AttributeError: registro"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/registro.html', {'form': form})