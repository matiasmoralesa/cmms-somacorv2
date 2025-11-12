"""
Script para limpiar todos los datos de la base de datos excepto usuarios
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from cmms_api.models import (
    # Modelos a limpiar
    ChecklistAnswer, ChecklistInstance, ChecklistItem, ChecklistCategory, ChecklistTemplate,
    ActividadesOrdenTrabajo, OrdenesTrabajo, Agendas,
    DetallesPlanMantenimiento, PlanesMantenimiento,
    Equipos, EstadosEquipo, TiposEquipo, Faenas,
    EstadosOrdenTrabajo, TiposMantenimientoOT, TiposTarea, TareasEstandar,
    EvidenciaOT, ChecklistImage
)
from django.contrib.auth.models import User

def limpiar_base_datos():
    """
    Elimina todos los datos excepto usuarios
    """
    print("=" * 80)
    print("LIMPIEZA DE BASE DE DATOS")
    print("=" * 80)
    print("\n⚠️  ADVERTENCIA: Esta operación eliminará todos los datos excepto usuarios")
    print("=" * 80)
    
    confirmacion = input("\n¿Estás seguro de que deseas continuar? (escribe 'SI' para confirmar): ")
    
    if confirmacion != 'SI':
        print("\n❌ Operación cancelada")
        return
    
    print("\n🗑️  Iniciando limpieza de datos...\n")
    
    try:
        # Orden de eliminación (de dependientes a independientes)
        modelos_a_limpiar = [
            # Evidencias y respuestas de checklist
            ('ChecklistAnswer', ChecklistAnswer),
            ('ChecklistImage', ChecklistImage),
            ('ChecklistInstance', ChecklistInstance),
            ('ChecklistItem', ChecklistItem),
            ('ChecklistCategory', ChecklistCategory),
            ('ChecklistTemplate', ChecklistTemplate),
            
            # Evidencias de OT
            ('EvidenciaOT', EvidenciaOT),
            
            # Actividades y órdenes de trabajo
            ('ActividadesOrdenTrabajo', ActividadesOrdenTrabajo),
            ('OrdenesTrabajo', OrdenesTrabajo),
            
            # Agendas
            ('Agendas', Agendas),
            
            # Planes de mantenimiento
            ('DetallesPlanMantenimiento', DetallesPlanMantenimiento),
            ('PlanesMantenimiento', PlanesMantenimiento),
            
            # Equipos
            ('Equipos', Equipos),
            
            # Catálogos (opcional - descomenta si quieres limpiarlos también)
            # ('EstadosEquipo', EstadosEquipo),
            # ('TiposEquipo', TiposEquipo),
            # ('Faenas', Faenas),
            # ('EstadosOrdenTrabajo', EstadosOrdenTrabajo),
            # ('TiposMantenimientoOT', TiposMantenimientoOT),
            # ('TiposTarea', TiposTarea),
            # ('TareasEstandar', TareasEstandar),
        ]
        
        total_eliminados = 0
        
        for nombre_modelo, modelo in modelos_a_limpiar:
            try:
                count = modelo.objects.count()
                if count > 0:
                    modelo.objects.all().delete()
                    print(f"✅ {nombre_modelo}: {count} registros eliminados")
                    total_eliminados += count
                else:
                    print(f"⚪ {nombre_modelo}: Sin registros")
            except Exception as e:
                print(f"❌ Error eliminando {nombre_modelo}: {e}")
        
        print("\n" + "=" * 80)
        print(f"✅ LIMPIEZA COMPLETADA")
        print(f"📊 Total de registros eliminados: {total_eliminados}")
        print("=" * 80)
        
        # Mostrar usuarios que se mantuvieron
        usuarios_count = User.objects.count()
        print(f"\n👥 Usuarios mantenidos: {usuarios_count}")
        
        usuarios = User.objects.all()
        print("\nLista de usuarios:")
        for usuario in usuarios:
            print(f"  - {usuario.username} ({usuario.email})")
        
        print("\n✅ Base de datos limpiada exitosamente")
        print("💡 Los usuarios y sus credenciales se mantuvieron intactos")
        
    except Exception as e:
        print(f"\n❌ Error durante la limpieza: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    limpiar_base_datos()
