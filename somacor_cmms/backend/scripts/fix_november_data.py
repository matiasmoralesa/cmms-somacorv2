"""
Script para corregir el exceso de datos en noviembre
Redistribuye las órdenes de trabajo uniformemente en todo 2024
"""

import os
import sys
import django
from datetime import datetime, timedelta
from random import randint, choice
from django.utils import timezone

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from cmms_api.models import OrdenesTrabajo

# Colores
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.YELLOW}ℹ️  {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def analizar_distribucion_actual():
    """Analizar la distribución actual de órdenes por mes"""
    print(f"\n{Colors.BOLD}📊 DISTRIBUCIÓN ACTUAL DE ÓRDENES{Colors.END}\n")
    
    ordenes = OrdenesTrabajo.objects.all()
    total = ordenes.count()
    
    print(f"Total de órdenes: {total}\n")
    
    # Analizar por año y mes
    años_meses = {}
    for orden in ordenes:
        if orden.fechacreacionot:
            año = orden.fechacreacionot.year
            mes = orden.fechacreacionot.month
            key = f"{año}-{mes:02d}"
            años_meses[key] = años_meses.get(key, 0) + 1
    
    # Mostrar distribución por año
    años = sorted(set(int(k.split('-')[0]) for k in años_meses.keys()))
    
    for año in años:
        print(f"\n{Colors.BOLD}Año {año}:{Colors.END}")
        distribucion = {}
        for mes in range(1, 13):
            key = f"{año}-{mes:02d}"
            count = años_meses.get(key, 0)
            distribucion[mes] = count
            
            meses_nombres = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
            
            barra = '█' * (count // 10) if count > 0 else ''
            if count > 0:
                print(f"{meses_nombres[mes]:12} {mes:02d}/{año}: {count:4d} {barra}")
    
    # Retornar distribución del último año con datos
    if años:
        ultimo_año = max(años)
        distribucion_ultimo = {}
        for mes in range(1, 13):
            key = f"{ultimo_año}-{mes:02d}"
            distribucion_ultimo[mes] = años_meses.get(key, 0)
        return distribucion_ultimo, ultimo_año
    
    return {}, None


def redistribuir_ordenes():
    """Redistribuir órdenes uniformemente en 2024"""
    print(f"\n{Colors.BOLD}🔄 REDISTRIBUYENDO ÓRDENES EN 2024{Colors.END}\n")
    
    ordenes = list(OrdenesTrabajo.objects.all())
    total = len(ordenes)
    
    if total == 0:
        print_info("No hay órdenes para redistribuir")
        return
    
    # Calcular órdenes por mes (distribución uniforme)
    ordenes_por_mes = total // 12
    ordenes_extra = total % 12
    
    print_info(f"Total órdenes: {total}")
    print_info(f"Órdenes por mes: {ordenes_por_mes}")
    print_info(f"Órdenes extra: {ordenes_extra}\n")
    
    # Redistribuir
    indice = 0
    actualizadas = 0
    
    for mes in range(1, 13):
        # Calcular cuántas órdenes para este mes
        ordenes_este_mes = ordenes_por_mes
        if mes <= ordenes_extra:
            ordenes_este_mes += 1
        
        print_info(f"Procesando mes {mes:02d}/2024: {ordenes_este_mes} órdenes...")
        
        for _ in range(ordenes_este_mes):
            if indice >= len(ordenes):
                break
            
            orden = ordenes[indice]
            
            # Generar fecha aleatoria en el mes
            if mes == 2:
                dia_max = 29  # 2024 es bisiesto
            elif mes in [4, 6, 9, 11]:
                dia_max = 30
            else:
                dia_max = 31
            
            dia = randint(1, dia_max)
            hora = randint(7, 18)
            minuto = randint(0, 59)
            
            nueva_fecha = datetime(2024, mes, dia, hora, minuto, tzinfo=timezone.get_current_timezone())
            
            # Actualizar fecha de creación
            orden.fechacreacionot = nueva_fecha
            
            # Si está completada, ajustar fecha de completado
            if orden.fechacompletado:
                dias_duracion = randint(1, 15)
                orden.fechacompletado = nueva_fecha + timedelta(days=dias_duracion)
            
            orden.save()
            actualizadas += 1
            indice += 1
    
    print_success(f"\nÓrdenes actualizadas: {actualizadas}")


def verificar_distribucion():
    """Verificar la nueva distribución"""
    print(f"\n{Colors.BOLD}✅ DISTRIBUCIÓN CORREGIDA{Colors.END}\n")
    
    ordenes = OrdenesTrabajo.objects.all()
    total = ordenes.count()
    
    print(f"Total de órdenes: {total}\n")
    
    for mes in range(1, 13):
        count = ordenes.filter(
            fechacreacionot__year=2024,
            fechacreacionot__month=mes
        ).count()
        
        meses_nombres = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        
        porcentaje = (count / total * 100) if total > 0 else 0
        barra = '█' * (count // 10) if count > 0 else ''
        print(f"{meses_nombres[mes]:12} {mes:02d}/2024: {count:4d} ({porcentaje:5.1f}%) {barra}")


def main():
    """Función principal"""
    print(f"\n{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{'CORRECCIÓN DE DISTRIBUCIÓN DE DATOS':^80}{Colors.END}")
    print(f"{Colors.BOLD}{'='*80}{Colors.END}")
    
    try:
        # 1. Analizar distribución actual
        distribucion_actual, año_actual = analizar_distribucion_actual()
        
        if not año_actual:
            print_info("\nNo hay órdenes con fechas válidas")
            return
        
        # Verificar si hay problema en noviembre
        noviembre_count = distribucion_actual.get(11, 0)
        total_ordenes = sum(distribucion_actual.values())
        promedio = total_ordenes / 12 if total_ordenes > 0 else 0
        
        print(f"\n{Colors.BOLD}Análisis:{Colors.END}")
        print(f"  • Total órdenes en {año_actual}: {total_ordenes}")
        print(f"  • Promedio por mes: {promedio:.0f}")
        print(f"  • Noviembre {año_actual}: {noviembre_count}")
        
        # Siempre ofrecer redistribuir a 2024
        print_info(f"\nSe redistribuirán TODAS las órdenes uniformemente en 2024")
        
        # Pedir confirmación
        respuesta = input(f"\n{Colors.BOLD}¿Deseas redistribuir las órdenes a 2024? (si/no): {Colors.END}").lower()
        
        if respuesta in ['si', 's', 'yes', 'y']:
            # 2. Redistribuir
            redistribuir_ordenes()
            
            # 3. Verificar
            verificar_distribucion()
            
            print(f"\n{Colors.GREEN}{Colors.BOLD}✅ CORRECCIÓN COMPLETADA{Colors.END}\n")
        else:
            print_info("Operación cancelada")
        
    except Exception as e:
        print_error(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
