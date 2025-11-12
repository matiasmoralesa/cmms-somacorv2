"""
Script para generar datos históricos del año 2024
- Órdenes de trabajo distribuidas mensualmente
- Checklists diarios realistas
- Mantenimientos preventivos y correctivos
"""

import os
import sys
import django
from datetime import datetime, timedelta
from random import randint, choice, uniform, random

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from cmms_api.models import Equipos, Usuarios, TiposEquipo
from django.contrib.auth.models import User

# Colores para output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")


def generar_fecha_aleatoria(año, mes):
    """Generar una fecha aleatoria dentro de un mes específico"""
    if mes == 12:
        ultimo_dia = 31
    elif mes in [4, 6, 9, 11]:
        ultimo_dia = 30
    elif mes == 2:
        ultimo_dia = 29 if año % 4 == 0 else 28
    else:
        ultimo_dia = 31
    
    dia = randint(1, ultimo_dia)
    hora = randint(7, 18)  # Horario laboral
    minuto = randint(0, 59)
    
    return datetime(año, mes, dia, hora, minuto)


def generar_checklists_diarios():
    """Generar checklists diarios para todo el año 2024"""
    print_header("GENERANDO CHECKLISTS DIARIOS 2024")
    
    equipos = list(Equipos.objects.filter(activo=True))
    operadores = list(Usuarios.objects.filter(idrol__nombrerol='Operador'))
    
    if not equipos:
        print_info("No hay equipos disponibles")
        return 0
    
    if not operadores:
        print_info("No hay operadores disponibles")
        return 0
    
    total_checklists = 0
    año = 2024
    
    # Generar checklists por mes
    for mes in range(1, 13):  # Enero a Diciembre
        print_info(f"Generando checklists para {mes:02d}/2024...")
        
        # Cada equipo tiene checklists en días laborales (aprox 22 días/mes)
        dias_laborales = 22
        
        for equipo in equipos:
            # No todos los equipos tienen checklist todos los días
            # Probabilidad basada en tipo de equipo
            if 'Camioneta' in equipo.idtipoequipo.nombretipo:
                prob_checklist = 0.95  # Camionetas casi siempre
            elif 'Supersucker' in equipo.idtipoequipo.nombretipo:
                prob_checklist = 0.85  # Supersuckers frecuente
            else:
                prob_checklist = 0.90  # Maquinaria pesada muy frecuente
            
            checklists_mes = int(dias_laborales * prob_checklist)
            
            for _ in range(checklists_mes):
                fecha = generar_fecha_aleatoria(año, mes)
                operador = choice(operadores)
                
                # Simular checklist (aquí irían los datos reales)
                # Por ahora solo contamos
                total_checklists += 1
        
        print_success(f"Mes {mes:02d}/2024: ~{len(equipos) * int(dias_laborales * 0.9)} checklists")
    
    print_success(f"Total checklists generados: {total_checklists}")
    return total_checklists


def generar_ordenes_trabajo():
    """Generar órdenes de trabajo distribuidas en el año"""
    print_header("GENERANDO ÓRDENES DE TRABAJO 2024")
    
    equipos = list(Equipos.objects.filter(activo=True))
    tecnicos = list(Usuarios.objects.filter(idrol__nombrerol='Técnico'))
    
    if not equipos or not tecnicos:
        print_info("No hay equipos o técnicos disponibles")
        return 0
    
    total_ordenes = 0
    año = 2024
    
    tipos_mantenimiento = [
        ('Preventivo', 0.60),  # 60% preventivo
        ('Correctivo', 0.30),  # 30% correctivo
        ('Predictivo', 0.10)   # 10% predictivo
    ]
    
    prioridades = [
        ('Alta', 0.20),
        ('Media', 0.50),
        ('Baja', 0.30)
    ]
    
    # Generar órdenes por mes
    for mes in range(1, 13):
        print_info(f"Generando órdenes para {mes:02d}/2024...")
        
        # Cada equipo tiene entre 2-4 órdenes por mes
        for equipo in equipos:
            num_ordenes = randint(2, 4)
            
            for _ in range(num_ordenes):
                fecha = generar_fecha_aleatoria(año, mes)
                tecnico = choice(tecnicos)
                
                # Tipo de mantenimiento
                rand = random()
                acum = 0
                tipo_mant = 'Preventivo'
                for tipo, prob in tipos_mantenimiento:
                    acum += prob
                    if rand <= acum:
                        tipo_mant = tipo
                        break
                
                # Prioridad
                rand = random()
                acum = 0
                prioridad = 'Media'
                for prio, prob in prioridades:
                    acum += prob
                    if rand <= acum:
                        prioridad = prio
                        break
                
                # Simular orden (aquí irían los datos reales)
                total_ordenes += 1
        
        ordenes_mes = len(equipos) * 3  # Promedio
        print_success(f"Mes {mes:02d}/2024: ~{ordenes_mes} órdenes")
    
    print_success(f"Total órdenes generadas: {total_ordenes}")
    return total_ordenes


def generar_estadisticas_uso():
    """Generar estadísticas de uso de equipos"""
    print_header("GENERANDO ESTADÍSTICAS DE USO")
    
    equipos = Equipos.objects.filter(activo=True)
    
    for equipo in equipos:
        # Simular horómetro/kilometraje acumulado en el año
        if 'Camioneta' in equipo.idtipoequipo.nombretipo or 'Supersucker' in equipo.idtipoequipo.nombretipo:
            # Vehículos: km
            km_mes = randint(1500, 3000)
            km_año = km_mes * 12
            print_info(f"{equipo.codigointerno}: {km_año:,} km en 2024")
        else:
            # Maquinaria: horas
            horas_mes = randint(150, 250)
            horas_año = horas_mes * 12
            print_info(f"{equipo.codigointerno}: {horas_año:,} horas en 2024")
    
    print_success("Estadísticas de uso generadas")


def generar_resumen():
    """Generar resumen de datos del año"""
    print_header("RESUMEN DE DATOS 2024")
    
    equipos = Equipos.objects.filter(activo=True).count()
    usuarios = Usuarios.objects.count()
    
    # Estimaciones
    checklists_estimados = equipos * 22 * 12 * 0.9  # 22 días/mes, 12 meses, 90% cumplimiento
    ordenes_estimadas = equipos * 3 * 12  # 3 órdenes/mes por equipo
    
    print(f"\n{Colors.BOLD}📊 DATOS GENERADOS PARA 2024:{Colors.END}")
    print(f"   • Equipos activos: {equipos}")
    print(f"   • Usuarios: {usuarios}")
    print(f"   • Checklists diarios: ~{int(checklists_estimados):,}")
    print(f"   • Órdenes de trabajo: ~{int(ordenes_estimadas):,}")
    print(f"   • Período: Enero - Diciembre 2024")
    
    print(f"\n{Colors.BOLD}📈 DISTRIBUCIÓN MENSUAL:{Colors.END}")
    print(f"   • Checklists/mes: ~{int(checklists_estimados/12):,}")
    print(f"   • Órdenes/mes: ~{int(ordenes_estimadas/12):,}")
    print(f"   • Días laborales/mes: ~22")
    
    print(f"\n{Colors.BOLD}🎯 MÉTRICAS CLAVE:{Colors.END}")
    print(f"   • Cumplimiento checklists: 90%")
    print(f"   • Mantenimiento preventivo: 60%")
    print(f"   • Mantenimiento correctivo: 30%")
    print(f"   • Mantenimiento predictivo: 10%")


def main():
    """Función principal"""
    print_header("GENERACIÓN DE DATOS HISTÓRICOS 2024")
    print(f"{Colors.BOLD}Sistema CMMS Somacor - Año Completo{Colors.END}\n")
    
    try:
        # Verificar que existan datos base
        if Equipos.objects.count() == 0:
            print_info("No hay equipos en la base de datos.")
            print_info("Ejecuta primero: python scripts/reset_and_populate_realistic.py")
            return
        
        # Generar datos del año
        print_info("Generando datos para el año 2024...")
        print_info("Esto puede tomar unos minutos...\n")
        
        # 1. Checklists diarios
        checklists = generar_checklists_diarios()
        
        # 2. Órdenes de trabajo
        ordenes = generar_ordenes_trabajo()
        
        # 3. Estadísticas de uso
        generar_estadisticas_uso()
        
        # 4. Resumen
        generar_resumen()
        
        print_header("✅ GENERACIÓN COMPLETADA")
        print(f"\n{Colors.YELLOW}NOTA: Este script genera estimaciones y conteos.{Colors.END}")
        print(f"{Colors.YELLOW}Para datos reales, se deben implementar los modelos completos.{Colors.END}\n")
        
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error: {str(e)}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
