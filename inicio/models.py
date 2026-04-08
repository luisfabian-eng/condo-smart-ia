from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# --- MODELO DE GASTOS COMUNES DEL CONDOMINIO ---
class Gasto(models.Model):
    CATEGORIAS = [
        ('servicios', 'Servicios Básicos'),
        ('mantenimiento', 'Mantenimiento'),
        ('sueldos', 'Sueldos'),
        ('seguridad', 'Seguridad'),
        ('otros', 'Otros'),
    ]
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    # Usamos DecimalField para dinero para evitar errores de redondeo
    monto = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='otros')
    fecha_gasto = models.DateField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titulo} - ${self.monto}"

# --- MODELO DE RESIDENTES ---
class Residente(models.Model):
    TIPOS = [
        ('propietario', 'Propietario'),
        ('arrendatario', 'Arrendatario'),
    ]
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    rut = models.CharField(max_length=12, unique=True)
    tipo = models.CharField(max_length=20, choices=TIPOS, default='propietario')
    telefono = models.CharField(max_length=15)
    departamento = models.CharField(max_length=10)
    torre = models.CharField(max_length=10, choices=[('A', 'Torre A'), ('B', 'Torre B')], default='A')
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} - Depto {self.departamento} ({self.torre})"

# --- MODELO DE PAGOS (GC, MULTAS, ETC) ---
class Pago(models.Model):
    residente = models.ForeignKey(Residente, on_delete=models.CASCADE, related_name='pagos')
    monto = models.IntegerField() # Para CLP suele ser entero, está bien.
    mes_correspondiente = models.DateField()
    fecha_pago = models.DateTimeField(auto_now_add=True)
    pagado = models.BooleanField(default=False)
    notas = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-mes_correspondiente']
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"

    def __str__(self):
        estado_txt = "PAGADO" if self.pagado else "PENDIENTE"
        # Usamos try/except por si mes_correspondiente llega a estar vacío en algún test
        try:
            fecha_str = self.mes_correspondiente.strftime('%B %Y')
        except:
            fecha_str = "Fecha no definida"
        return f"{self.residente.apellido} - {fecha_str} ({estado_txt})"

    @property
    def esta_atrasado(self):
        """Retorna True si no está pagado y ya pasó el primer día del mes actual"""
        if not self.pagado:
            hoy = timezone.now().date()
            # Creamos una fecha del primer día del mes actual para comparar
            inicio_mes_actual = hoy.replace(day=1)
            if self.mes_correspondiente < inicio_mes_actual:
                return True
        return False