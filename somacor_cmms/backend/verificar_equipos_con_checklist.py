import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from cmms_api.models import Equipos, ChecklistTemplate, TiposEquipo

print("=" * 60)
print("TEMPLATES DE CHECKLIST DISPONIBLES")
print("=" * 60)

templates = ChecklistTemplate.objects.all()
for template in templates:
    print(f"\n📋 {template.nombre}")
    print(f"   Tipo de equipo: {template.tipo_equipo.nombretipo}")
    equipos_count = Equipos.objects.filter(idtipoequipo=template.tipo_equipo, activo=True).count()
    print(f"   Equipos con este tipo: {equipos_count}")
    
    if equipos_count > 0:
        print(f"   Ejemplos:")
        equipos = Equipos.objects.filter(idtipoequipo=template.tipo_equipo, activo=True)[:3]
        for equipo in equipos:
            print(f"      - {equipo.nombreequipo} (ID: {equipo.idequipo})")

print("\n" + "=" * 60)
print("TIPOS DE EQUIPO SIN TEMPLATE")
print("=" * 60)

tipos_con_template = ChecklistTemplate.objects.values_list('tipo_equipo_id', flat=True)
tipos_sin_template = TiposEquipo.objects.exclude(idtipoequipo__in=tipos_con_template)

for tipo in tipos_sin_template:
    equipos_count = Equipos.objects.filter(idtipoequipo=tipo, activo=True).count()
    if equipos_count > 0:
        print(f"\n⚠️  {tipo.nombretipo}")
        print(f"   Equipos activos: {equipos_count}")
