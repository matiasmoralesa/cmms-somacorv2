"""
Script para poblar datos de inventario de prueba
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from cmms_api.models import CategoriasInventario, Proveedores, Inventario
from django.contrib.auth.models import User

def populate_inventario():
    print("🔧 Poblando datos de inventario...")
    
    # Obtener el primer usuario para asignar como creador
    usuario = User.objects.first()
    if not usuario:
        print("❌ No hay usuarios en el sistema. Crea un usuario primero.")
        return
    
    # Crear categorías
    categorias_data = [
        {'nombrecategoria': 'Filtros', 'descripcion': 'Filtros de aire, aceite y combustible'},
        {'nombrecategoria': 'Rodamientos', 'descripcion': 'Rodamientos y cojinetes'},
        {'nombrecategoria': 'Lubricantes', 'descripcion': 'Aceites y grasas lubricantes'},
        {'nombrecategoria': 'Herramientas', 'descripcion': 'Herramientas manuales y eléctricas'},
        {'nombrecategoria': 'Neumáticos', 'descripcion': 'Neumáticos y cámaras'},
        {'nombrecategoria': 'Eléctricos', 'descripcion': 'Componentes eléctricos y electrónicos'},
        {'nombrecategoria': 'Hidráulicos', 'descripcion': 'Componentes hidráulicos'},
    ]
    
    categorias = {}
    for cat_data in categorias_data:
        cat, created = CategoriasInventario.objects.get_or_create(
            nombrecategoria=cat_data['nombrecategoria'],
            defaults={'descripcion': cat_data['descripcion']}
        )
        categorias[cat_data['nombrecategoria']] = cat
        if created:
            print(f"✅ Categoría creada: {cat.nombrecategoria}")
    
    # Crear proveedores
    proveedores_data = [
        {
            'nombreproveedor': 'Repuestos Industriales S.A.',
            'rut': '76123456-7',
            'contacto': 'Juan Pérez',
            'telefono': '+56912345678',
            'email': 'ventas@repuestosindustriales.cl'
        },
        {
            'nombreproveedor': 'Lubricantes del Sur',
            'rut': '76234567-8',
            'contacto': 'María González',
            'telefono': '+56923456789',
            'email': 'contacto@lubricantesdelsur.cl'
        },
        {
            'nombreproveedor': 'Neumáticos Chile',
            'rut': '76345678-9',
            'contacto': 'Pedro Ramírez',
            'telefono': '+56934567890',
            'email': 'ventas@neumaticos.cl'
        },
    ]
    
    proveedores = {}
    for prov_data in proveedores_data:
        prov, created = Proveedores.objects.get_or_create(
            rut=prov_data['rut'],
            defaults=prov_data
        )
        proveedores[prov_data['nombreproveedor']] = prov
        if created:
            print(f"✅ Proveedor creado: {prov.nombreproveedor}")
    
    # Crear items de inventario
    items_data = [
        {
            'codigointerno': 'FLT-001',
            'nombreitem': 'Filtro de Aire HD',
            'descripcion': 'Filtro de aire para equipos pesados',
            'categoria': 'Filtros',
            'proveedor': 'Repuestos Industriales S.A.',
            'cantidad': 15,
            'stockminimo': 10,
            'stockmaximo': 50,
            'unidadmedida': 'unidad',
            'ubicacion': 'Bodega A - Estante 1',
            'costounitario': 25000,
        },
        {
            'codigointerno': 'FLT-002',
            'nombreitem': 'Filtro de Aceite',
            'descripcion': 'Filtro de aceite motor',
            'categoria': 'Filtros',
            'proveedor': 'Repuestos Industriales S.A.',
            'cantidad': 8,
            'stockminimo': 15,
            'stockmaximo': 60,
            'unidadmedida': 'unidad',
            'ubicacion': 'Bodega A - Estante 1',
            'costounitario': 18000,
        },
        {
            'codigointerno': 'ROD-001',
            'nombreitem': 'Rodamiento 6308',
            'descripcion': 'Rodamiento rígido de bolas 6308',
            'categoria': 'Rodamientos',
            'proveedor': 'Repuestos Industriales S.A.',
            'cantidad': 25,
            'stockminimo': 20,
            'stockmaximo': 100,
            'unidadmedida': 'unidad',
            'ubicacion': 'Bodega A - Estante 2',
            'costounitario': 35000,
        },
        {
            'codigointerno': 'LUB-001',
            'nombreitem': 'Aceite Motor 15W-40',
            'descripcion': 'Aceite mineral para motores diesel',
            'categoria': 'Lubricantes',
            'proveedor': 'Lubricantes del Sur',
            'cantidad': 120,
            'stockminimo': 50,
            'stockmaximo': 200,
            'unidadmedida': 'litro',
            'ubicacion': 'Bodega B - Zona Líquidos',
            'costounitario': 8500,
        },
        {
            'codigointerno': 'LUB-002',
            'nombreitem': 'Grasa Multiuso',
            'descripcion': 'Grasa de litio multiuso',
            'categoria': 'Lubricantes',
            'proveedor': 'Lubricantes del Sur',
            'cantidad': 0,
            'stockminimo': 30,
            'stockmaximo': 100,
            'unidadmedida': 'kilogramo',
            'ubicacion': 'Bodega B - Zona Líquidos',
            'costounitario': 12000,
        },
        {
            'codigointerno': 'NEU-001',
            'nombreitem': 'Neumático 12.00R20',
            'descripcion': 'Neumático para camión minero',
            'categoria': 'Neumáticos',
            'proveedor': 'Neumáticos Chile',
            'cantidad': 4,
            'stockminimo': 8,
            'stockmaximo': 20,
            'unidadmedida': 'unidad',
            'ubicacion': 'Patio Exterior',
            'costounitario': 850000,
        },
        {
            'codigointerno': 'HER-001',
            'nombreitem': 'Llave de Impacto 1/2"',
            'descripcion': 'Llave de impacto neumática',
            'categoria': 'Herramientas',
            'proveedor': 'Repuestos Industriales S.A.',
            'cantidad': 3,
            'stockminimo': 2,
            'stockmaximo': 5,
            'unidadmedida': 'unidad',
            'ubicacion': 'Taller - Caja Herramientas',
            'costounitario': 180000,
        },
    ]
    
    for item_data in items_data:
        categoria = categorias.get(item_data.pop('categoria'))
        proveedor = proveedores.get(item_data.pop('proveedor'))
        
        item, created = Inventario.objects.get_or_create(
            codigointerno=item_data['codigointerno'],
            defaults={
                **item_data,
                'idcategoria': categoria,
                'idproveedor': proveedor,
                'usuariocreacion': usuario
            }
        )
        if created:
            print(f"✅ Item creado: {item.codigointerno} - {item.nombreitem}")
    
    print("\n✅ Datos de inventario poblados exitosamente!")
    print(f"📦 Total categorías: {CategoriasInventario.objects.count()}")
    print(f"🏢 Total proveedores: {Proveedores.objects.count()}")
    print(f"📋 Total items: {Inventario.objects.count()}")
    
    # Mostrar estadísticas
    items_stock_bajo = Inventario.objects.extra(where=["cantidad <= stockminimo AND cantidad > 0"]).count()
    items_sin_stock = Inventario.objects.filter(cantidad=0).count()
    print(f"⚠️  Items con stock bajo: {items_stock_bajo}")
    print(f"❌ Items sin stock: {items_sin_stock}")

if __name__ == '__main__':
    populate_inventario()
