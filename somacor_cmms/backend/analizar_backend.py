"""
Script para analizar carencias en serializers y views del backend
"""
import os
import re
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from cmms_api import models
from cmms_api import serializers_v2
from cmms_api import views_v2
import inspect

def analizar_modelos():
    """Analizar todos los modelos definidos"""
    print("=" * 80)
    print("MODELOS DEFINIDOS EN EL SISTEMA")
    print("=" * 80)
    
    modelos = []
    for name, obj in inspect.getmembers(models):
        if inspect.isclass(obj) and hasattr(obj, '_meta') and hasattr(obj._meta, 'db_table'):
            modelos.append({
                'nombre': name,
                'tabla': obj._meta.db_table,
                'campos': [f.name for f in obj._meta.fields]
            })
    
    for modelo in sorted(modelos, key=lambda x: x['nombre']):
        print(f"\n{modelo['nombre']}")
        print(f"  Tabla: {modelo['tabla']}")
        print(f"  Campos: {len(modelo['campos'])}")
    
    return modelos

def analizar_serializers():
    """Analizar todos los serializers definidos"""
    print("\n" + "=" * 80)
    print("SERIALIZERS DEFINIDOS")
    print("=" * 80)
    
    serializers_list = []
    for name, obj in inspect.getmembers(serializers_v2):
        if inspect.isclass(obj) and name.endswith('Serializer'):
            serializers_list.append(name)
    
    for serializer in sorted(serializers_list):
        print(f"  - {serializer}")
    
    return serializers_list

def analizar_viewsets():
    """Analizar todos los viewsets definidos"""
    print("\n" + "=" * 80)
    print("VIEWSETS DEFINIDOS")
    print("=" * 80)
    
    viewsets_list = []
    for name, obj in inspect.getmembers(views_v2):
        if inspect.isclass(obj) and name.endswith('ViewSet'):
            viewsets_list.append(name)
    
    for viewset in sorted(viewsets_list):
        print(f"  - {viewset}")
    
    return viewsets_list

def identificar_carencias(modelos, serializers_list, viewsets_list):
    """Identificar modelos sin serializers o viewsets"""
    print("\n" + "=" * 80)
    print("ANÁLISIS DE CARENCIAS")
    print("=" * 80)
    
    print("\n1. MODELOS SIN SERIALIZER:")
    print("-" * 80)
    modelos_sin_serializer = []
    for modelo in modelos:
        nombre_modelo = modelo['nombre']
        # Buscar serializer correspondiente
        serializer_esperado = f"{nombre_modelo}Serializer"
        serializer_plural = f"{nombre_modelo}sSerializer"
        
        if serializer_esperado not in serializers_list and serializer_plural not in serializers_list:
            modelos_sin_serializer.append(nombre_modelo)
            print(f"  ❌ {nombre_modelo} (tabla: {modelo['tabla']})")
    
    if not modelos_sin_serializer:
        print("  ✅ Todos los modelos tienen serializer")
    
    print("\n2. MODELOS SIN VIEWSET:")
    print("-" * 80)
    modelos_sin_viewset = []
    for modelo in modelos:
        nombre_modelo = modelo['nombre']
        # Buscar viewset correspondiente
        viewset_esperado = f"{nombre_modelo}ViewSet"
        viewset_plural = f"{nombre_modelo}sViewSet"
        
        if viewset_esperado not in viewsets_list and viewset_plural not in viewsets_list:
            modelos_sin_viewset.append(nombre_modelo)
            print(f"  ❌ {nombre_modelo} (tabla: {modelo['tabla']})")
    
    if not modelos_sin_viewset:
        print("  ✅ Todos los modelos tienen viewset")
    
    print("\n3. SERIALIZERS SIN VIEWSET:")
    print("-" * 80)
    serializers_sin_viewset = []
    for serializer in serializers_list:
        # Extraer nombre base del serializer
        nombre_base = serializer.replace('Serializer', '')
        viewset_esperado = f"{nombre_base}ViewSet"
        
        if viewset_esperado not in viewsets_list:
            serializers_sin_viewset.append(serializer)
            print(f"  ⚠️  {serializer} → falta {viewset_esperado}")
    
    if not serializers_sin_viewset:
        print("  ✅ Todos los serializers tienen viewset")
    
    return {
        'modelos_sin_serializer': modelos_sin_serializer,
        'modelos_sin_viewset': modelos_sin_viewset,
        'serializers_sin_viewset': serializers_sin_viewset
    }

def analizar_campos_faltantes():
    """Analizar campos importantes que podrían faltar"""
    print("\n" + "=" * 80)
    print("ANÁLISIS DE CAMPOS IMPORTANTES")
    print("=" * 80)
    
    # Verificar campos comunes que deberían existir
    campos_importantes = {
        'OrdenesTrabajo': ['idordentrabajo', 'numeroot', 'idequipo', 'idtecnicoasignado', 'idestadoot'],
        'Equipos': ['idequipo', 'nombreequipo', 'idtipoequipo', 'idestadoactual'],
        'Tecnicos': ['idtecnico', 'usuario', 'especialidades', 'estado'],
        'Usuarios': ['user', 'idrol'],
    }
    
    for modelo_nombre, campos_esperados in campos_importantes.items():
        try:
            modelo = getattr(models, modelo_nombre)
            campos_modelo = [f.name for f in modelo._meta.fields]
            campos_faltantes = [c for c in campos_esperados if c not in campos_modelo]
            
            if campos_faltantes:
                print(f"\n❌ {modelo_nombre} - Campos faltantes:")
                for campo in campos_faltantes:
                    print(f"     - {campo}")
            else:
                print(f"\n✅ {modelo_nombre} - Todos los campos importantes presentes")
        except AttributeError:
            print(f"\n⚠️  {modelo_nombre} - Modelo no encontrado")

def main():
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "ANÁLISIS DEL BACKEND CMMS" + " " * 34 + "║")
    print("╚" + "=" * 78 + "╝")
    
    modelos = analizar_modelos()
    serializers_list = analizar_serializers()
    viewsets_list = analizar_viewsets()
    
    carencias = identificar_carencias(modelos, serializers_list, viewsets_list)
    
    analizar_campos_faltantes()
    
    # Resumen final
    print("\n" + "=" * 80)
    print("RESUMEN DE CARENCIAS")
    print("=" * 80)
    print(f"Total modelos: {len(modelos)}")
    print(f"Total serializers: {len(serializers_list)}")
    print(f"Total viewsets: {len(viewsets_list)}")
    print(f"\nModelos sin serializer: {len(carencias['modelos_sin_serializer'])}")
    print(f"Modelos sin viewset: {len(carencias['modelos_sin_viewset'])}")
    print(f"Serializers sin viewset: {len(carencias['serializers_sin_viewset'])}")
    
    if (carencias['modelos_sin_serializer'] or 
        carencias['modelos_sin_viewset'] or 
        carencias['serializers_sin_viewset']):
        print("\n⚠️  SE ENCONTRARON CARENCIAS QUE REQUIEREN ATENCIÓN")
    else:
        print("\n✅ NO SE ENCONTRARON CARENCIAS CRÍTICAS")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    main()
