import os
from django.core.wsgi import get_wsgi_application

# Reemplaza 'mi_web' con el nombre real de tu carpeta de configuración si es distinto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mi_web.settings')

application = get_wsgi_application()