"""
Script para verificar que los datos estén en 2024
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from cmms_api.models import OrdenesTrabajo
from datetime import datetime

# Colores
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{text:^80}{Colors.END}")
    print(f"{Colors.BOLD}{'='*80}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def main():
    print_header("VERIFICACIÓN DE DATOS 2024")
    
    # Verificar órdenes de trabajo
    ordenes_2024 = OrdenesTrabajo.objects.filter(fechacreacionot__year=2024)
    total_ordenes = OrdenesTrabajo.objects.count()
    
    print_info(f"Total de órdenes: {total_ordenes}")
    print_info(f"Órdenes en 2024: {ordenes_2024.count()}")
    
    if ordenes_2024.count() == 0:
        print_warning("No hay órdenes en 2024!")
        print_info("Ejecuta: python fix_november_data.py")
        return
    
    # Mostrar distribución por mes
    print(f"\n{Colors.BOLD}Distribución por mes en 2024:{Colors.END}\n")
    
    meses_nombres = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    
    for mes in range(1, 13):
        count = ordenes_2024.filter(fechacreacionot__month=mes).count()
        barra = '█' * (count // 10) if count > 0 else ''
        print(f"{meses_nombres[mes]:12} {mes:02d}/2024: {count:4d} {barra}")
    
    # Verificar rango de fechas
    primera_orden = ordenes_2024.order_by('fechacreacionot').first()
    ultima_orden = ordenes_2024.order_by('-fechacreacionot').first()
    
    if primera_orden and ultima_orden:
        print(f"\n{Colors.BOLD}Rango de fechas:{Colors.END}")
        print(f"  Primera orden: {primera_orden.fechacreacionot.strftime('%d/%m/%Y')}")
        print(f"  Última orden: {ultima_orden.fechacreacionot.strftime('%d/%m/%Y')}")
    
    print_success("\n✅ Datos verificados correctamente")
    print_info("\nSi el dashboard no muestra datos, verifica:")
    print_info("  1. Que el backend esté corriendo")
    print_info("  2. Que el frontend esté conectado al backend correcto")
    print_info("  3. Refresca el navegador (Ctrl+F5)")


if __name__ == '__main__':
    main()
