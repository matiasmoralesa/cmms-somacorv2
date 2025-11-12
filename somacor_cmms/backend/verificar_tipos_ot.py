import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from cmms_api.models import OrdenesTrabajo

print("Verificando tipos de mantenimiento en OT...")
print("=" * 60)

# Obtener una muestra de órdenes
ordenes = OrdenesTrabajo.objects.all()[:5]

for ot in ordenes:
    print(f"\nOT: {ot.numeroot}")
    print(f"  Tipo ID: {ot.idtipomantenimientoot_id}")
    if ot.idtipomantenimientoot:
        print(f"  Tipo Nombre: {ot.idtipomantenimientoot.nombretipomantenimientoot}")
    else:
        print(f"  Tipo Nombre: None")
    print(f"  Equipo: {ot.idequipo.nombreequipo if ot.idequipo else 'None'}")
    print(f"  Estado: {ot.idestadoot.nombreestadoot if ot.idestadoot else 'None'}")
