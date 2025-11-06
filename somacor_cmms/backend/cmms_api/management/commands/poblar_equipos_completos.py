from django.core.management.base import BaseCommand
from django.db import transaction
from cmms_api.models import (
    TiposEquipo, EstadosEquipo, Equipos, Faenas,
    ChecklistTemplate, ChecklistCategory, ChecklistItem
)

class Command(BaseCommand):
    help = 'Poblar la base de datos con equipos y checklists completos según los tipos analizados'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando población de equipos y checklists...'))
        
        with transaction.atomic():
            # 1. Crear tipos de equipo si no existen
            self.crear_tipos_equipo()
            
            # 2. Crear estados de equipo si no existen
            self.crear_estados_equipo()
            
            # 3. Crear faenas si no existen
            self.crear_faenas()
            
            # 4. Crear equipos de ejemplo
            self.crear_equipos()
            
            # 5. Crear templates de checklist
            self.crear_checklist_templates()
            
            # 6. Crear categorías y items para cada template
            self.crear_checklist_minicargador()
            self.crear_checklist_cargador_frontal()
            self.crear_checklist_retroexcavadora()
            self.crear_checklist_camionetas()
        
        self.stdout.write(self.style.SUCCESS('¡Población completada exitosamente!'))

    def crear_tipos_equipo(self):
        """Crear tipos de equipo según los checklists analizados"""
        tipos = [
            {'nombre': 'Minicargador', 'descripcion': 'Minicargador para trabajos de construcción'},
            {'nombre': 'Cargador Frontal', 'descripcion': 'Cargador frontal para movimiento de tierra'},
            {'nombre': 'Retroexcavadora', 'descripcion': 'Retroexcavadora para excavación y movimiento de tierra'},
            {'nombre': 'Camioneta', 'descripcion': 'Vehículo liviano para transporte de personal'},
            {'nombre': 'Camión', 'descripcion': 'Vehículo pesado para transporte de materiales'},
        ]
        
        for tipo_data in tipos:
            tipo, created = TiposEquipo.objects.get_or_create(
                nombretipo=tipo_data['nombre'],
                defaults={}
            )
            if created:
                self.stdout.write(f'Creado tipo de equipo: {tipo.nombretipo}')

    def crear_estados_equipo(self):
        """Crear estados de equipo básicos"""
        estados = [
            {'nombre': 'Operativo', 'descripcion': 'Equipo en condiciones de operar'},
            {'nombre': 'En Mantenimiento', 'descripcion': 'Equipo en proceso de mantenimiento'},
            {'nombre': 'Fuera de Servicio', 'descripcion': 'Equipo no disponible para operación'},
            {'nombre': 'En Reparación', 'descripcion': 'Equipo en proceso de reparación'},
        ]
        
        for estado_data in estados:
            estado, created = EstadosEquipo.objects.get_or_create(
                nombreestado=estado_data['nombre'],
                defaults={}
            )
            if created:
                self.stdout.write(f'Creado estado de equipo: {estado.nombreestado}')

    def crear_faenas(self):
        """Crear faenas de ejemplo"""
        faenas = [
            {'nombre': 'Faena Central', 'ubicacion': 'Santiago, Chile'},
            {'nombre': 'Faena Norte', 'ubicacion': 'Antofagasta, Chile'},
            {'nombre': 'Faena Sur', 'ubicacion': 'Concepción, Chile'},
        ]
        
        for faena_data in faenas:
            faena, created = Faenas.objects.get_or_create(
                nombrefaena=faena_data['nombre'],
                defaults={'ubicacion': faena_data['ubicacion']}
            )
            if created:
                self.stdout.write(f'Creada faena: {faena.nombrefaena}')

    def crear_equipos(self):
        """Crear equipos de ejemplo para cada tipo"""
        # Obtener referencias necesarias
        estado_operativo = EstadosEquipo.objects.get(nombreestado='Operativo')
        faena_central = Faenas.objects.get(nombrefaena='Faena Central')
        
        equipos_data = [
            # Minicargadores
            {
                'nombre': 'Minicargador CAT 236D',
                'tipo': 'Minicargador',
                'marca': 'Caterpillar',
                'modelo': '236D',
                'anio': 2020,
                'patente': 'CAT-001',
                'codigo': 'MC-001'
            },
            {
                'nombre': 'Minicargador CAT 242D',
                'tipo': 'Minicargador',
                'marca': 'Caterpillar',
                'modelo': '242D',
                'anio': 2021,
                'patente': 'CAT-002',
                'codigo': 'MC-002'
            },
            {
                'nombre': 'Minicargador Bobcat S650',
                'tipo': 'Minicargador',
                'marca': 'Bobcat',
                'modelo': 'S650',
                'anio': 2019,
                'patente': 'BOB-001',
                'codigo': 'MC-003'
            },
            
            # Cargadores Frontales
            {
                'nombre': 'Cargador Frontal CAT 950M',
                'tipo': 'Cargador Frontal',
                'marca': 'Caterpillar',
                'modelo': '950M',
                'anio': 2020,
                'patente': 'CF-001',
                'codigo': 'CF-001'
            },
            {
                'nombre': 'Cargador Frontal Komatsu WA380',
                'tipo': 'Cargador Frontal',
                'marca': 'Komatsu',
                'modelo': 'WA380',
                'anio': 2019,
                'patente': 'CF-002',
                'codigo': 'CF-002'
            },
            
            # Retroexcavadoras
            {
                'nombre': 'Retroexcavadora CAT 320D',
                'tipo': 'Retroexcavadora',
                'marca': 'Caterpillar',
                'modelo': '320D',
                'anio': 2020,
                'patente': 'RE-001',
                'codigo': 'RE-001'
            },
            {
                'nombre': 'Retroexcavadora Komatsu PC200',
                'tipo': 'Retroexcavadora',
                'marca': 'Komatsu',
                'modelo': 'PC200',
                'anio': 2021,
                'patente': 'RE-002',
                'codigo': 'RE-002'
            },
            
            # Camionetas
            {
                'nombre': 'Camioneta Toyota Hilux',
                'tipo': 'Camioneta',
                'marca': 'Toyota',
                'modelo': 'Hilux',
                'anio': 2022,
                'patente': 'HJKL-12',
                'codigo': 'CM-001'
            },
            {
                'nombre': 'Camioneta Ford Ranger',
                'tipo': 'Camioneta',
                'marca': 'Ford',
                'modelo': 'Ranger',
                'anio': 2021,
                'patente': 'MNOP-34',
                'codigo': 'CM-002'
            },
            {
                'nombre': 'Camioneta Chevrolet D-Max',
                'tipo': 'Camioneta',
                'marca': 'Chevrolet',
                'modelo': 'D-Max',
                'anio': 2020,
                'patente': 'QRST-56',
                'codigo': 'CM-003'
            },
        ]
        
        for equipo_data in equipos_data:
            tipo_equipo = TiposEquipo.objects.get(nombretipo=equipo_data['tipo'])
            
            equipo, created = Equipos.objects.get_or_create(
                codigointerno=equipo_data['codigo'],
                defaults={
                    'nombreequipo': equipo_data['nombre'],
                    'marca': equipo_data['marca'],
                    'modelo': equipo_data['modelo'],
                    'anio': equipo_data['anio'],
                    'patente': equipo_data['patente'],
                    'idtipoequipo': tipo_equipo,
                    'idfaenaactual': faena_central,
                    'idestadoactual': estado_operativo,
                    'activo': True
                }
            )
            if created:
                self.stdout.write(f'Creado equipo: {equipo.nombreequipo}')

    def crear_checklist_templates(self):
        """Crear templates de checklist para cada tipo de equipo"""
        templates_data = [
            {'nombre': 'Check List Minicargador (Diario)', 'tipo': 'Minicargador'},
            {'nombre': 'Check List Cargador Frontal (Diario)', 'tipo': 'Cargador Frontal'},
            {'nombre': 'Check List Retroexcavadora (Diario)', 'tipo': 'Retroexcavadora'},
            {'nombre': 'Check List Camionetas (Diario)', 'tipo': 'Camioneta'},
        ]
        
        for template_data in templates_data:
            tipo_equipo = TiposEquipo.objects.get(nombretipo=template_data['tipo'])
            
            template, created = ChecklistTemplate.objects.get_or_create(
                nombre=template_data['nombre'],
                defaults={
                    'tipo_equipo': tipo_equipo,
                    'activo': True
                }
            )
            if created:
                self.stdout.write(f'Creado template: {template.nombre}')

    def crear_checklist_minicargador(self):
        """Crear checklist completo para minicargador"""
        template = ChecklistTemplate.objects.get(nombre='Check List Minicargador (Diario)')
        
        # No eliminar categorías existentes, usar get_or_create
        
        categorias_items = [
            {
                'nombre': 'MOTOR',
                'orden': 1,
                'items': [
                    {'texto': '1.1 Nivel de Agua', 'critico': False, 'orden': 1},
                    {'texto': '1.2 Nivel de Aceite', 'critico': True, 'orden': 2},
                    {'texto': '1.3 Nivel de Líquido de Freno', 'critico': True, 'orden': 3},
                    {'texto': '1.4 Combustible', 'critico': False, 'orden': 4},
                    {'texto': '1.5 Batería', 'critico': False, 'orden': 5},
                    {'texto': '1.6 Correas', 'critico': False, 'orden': 6},
                    {'texto': '1.7 Filtraciones', 'critico': False, 'orden': 7},
                    {'texto': '1.8 Alternador', 'critico': False, 'orden': 8},
                    {'texto': '1.9 Partida en Frío', 'critico': False, 'orden': 9},
                    {'texto': '1.10 Radiador / Anticongelante', 'critico': False, 'orden': 10},
                    {'texto': '1.11 Motor Arranque', 'critico': False, 'orden': 11},
                ]
            },
            {
                'nombre': 'LUCES',
                'orden': 2,
                'items': [
                    {'texto': '2.1 Luces Altas', 'critico': True, 'orden': 1},
                    {'texto': '2.2 Luces Bajas', 'critico': True, 'orden': 2},
                    {'texto': '2.3 Luces Intermitentes', 'critico': False, 'orden': 3},
                    {'texto': '2.4 Luz Marcha Atrás', 'critico': False, 'orden': 4},
                    {'texto': '2.5 Luz Tablero', 'critico': False, 'orden': 5},
                    {'texto': '2.6 Luz Baliza', 'critico': False, 'orden': 6},
                    {'texto': '2.7 Luz Pértiga', 'critico': False, 'orden': 7},
                    {'texto': '2.8 Luces de Freno', 'critico': False, 'orden': 8},
                    {'texto': '2.9 Estado de Micas', 'critico': False, 'orden': 9},
                    {'texto': '2.10 Focos Faeneros', 'critico': False, 'orden': 10},
                    {'texto': '2.11 Luz Patente', 'critico': False, 'orden': 11},
                ]
            },
            {
                'nombre': 'DOCUMENTOS',
                'orden': 3,
                'items': [
                    {'texto': '3.1 Permiso de Circulación', 'critico': False, 'orden': 1},
                    {'texto': '3.2 Revisión Técnica', 'critico': False, 'orden': 2},
                    {'texto': '3.3 Seguro Obligatorio', 'critico': False, 'orden': 3},
                ]
            },
            {
                'nombre': 'ACCESORIOS',
                'orden': 4,
                'items': [
                    {'texto': '4.1 Botiquín', 'critico': False, 'orden': 1},
                    {'texto': '4.2 Extintor', 'critico': False, 'orden': 2},
                    {'texto': '4.3 Llave de Rueda', 'critico': False, 'orden': 3},
                    {'texto': '4.4 Triángulos / Conos', 'critico': False, 'orden': 4},
                    {'texto': '4.5 Cinturón de Seguridad', 'critico': True, 'orden': 5},
                    {'texto': '4.6 Marcadores', 'critico': True, 'orden': 6},
                    {'texto': '4.7 Señaléticas en Español', 'critico': False, 'orden': 7},
                    {'texto': '4.8 Manual de Operación', 'critico': False, 'orden': 8},
                    {'texto': '4.9 Sistema Corta Corriente', 'critico': False, 'orden': 9},
                    {'texto': '4.10 Revisión Tres Puntos de Apoyo', 'critico': True, 'orden': 10},
                    {'texto': '4.11 Protección Contra Volcamiento', 'critico': False, 'orden': 11},
                    {'texto': '4.12 Asiento Certificado', 'critico': False, 'orden': 12},
                    {'texto': '4.13 Estado de Neumáticos', 'critico': False, 'orden': 13},
                    {'texto': '4.14 Seguros en Tuercas', 'critico': False, 'orden': 14},
                    {'texto': '4.15 Dirección', 'critico': False, 'orden': 15},
                    {'texto': '4.16 Tubo de Escape', 'critico': False, 'orden': 16},
                    {'texto': '4.17 Parada de Emergencia', 'critico': False, 'orden': 17},
                    {'texto': '4.18 Escaleras de Acceso', 'critico': False, 'orden': 18},
                    {'texto': '4.19 Pasamanos', 'critico': True, 'orden': 19},
                    {'texto': '4.20 Bocina', 'critico': False, 'orden': 20},
                    {'texto': '4.21 Espejo Retrovisor', 'critico': False, 'orden': 21},
                    {'texto': '4.22 Limpiaparabrisas', 'critico': False, 'orden': 22},
                    {'texto': '4.23 Vidrios', 'critico': False, 'orden': 23},
                    {'texto': '4.24 Puertas', 'critico': False, 'orden': 24},
                    {'texto': '4.25 Cabina', 'critico': False, 'orden': 25},
                    {'texto': '4.26 Instrumentos', 'critico': True, 'orden': 26},
                    {'texto': '4.27 Mandos', 'critico': False, 'orden': 27},
                    {'texto': '4.28 Alarma de Retroceso', 'critico': True, 'orden': 28},
                    {'texto': '4.29 Estructura', 'critico': False, 'orden': 29},
                    {'texto': '4.30 Chasis', 'critico': False, 'orden': 30},
                    {'texto': '4.31 Tren de Rodaje', 'critico': True, 'orden': 31},
                ]
            },
            {
                'nombre': 'FRENOS',
                'orden': 5,
                'items': [
                    {'texto': '5.1 Freno de Servicio', 'critico': True, 'orden': 1},
                    {'texto': '5.2 Freno de Parqueo', 'critico': True, 'orden': 2},
                ]
            },
            {
                'nombre': 'CARGADOR',
                'orden': 6,
                'items': [
                    {'texto': '6.1 Balde', 'critico': True, 'orden': 1},
                    {'texto': '6.2 Cuchillo de Balde', 'critico': True, 'orden': 2},
                    {'texto': '6.3 Porte Cuchilla', 'critico': False, 'orden': 3},
                    {'texto': '6.4 Seguros Manuales', 'critico': False, 'orden': 4},
                    {'texto': '6.5 Conexión Inferior', 'critico': False, 'orden': 5},
                    {'texto': '6.6 Sistema Hidráulico', 'critico': False, 'orden': 6},
                    {'texto': '6.7 Mangueras', 'critico': False, 'orden': 7},
                    {'texto': '6.8 Conexiones', 'critico': False, 'orden': 8},
                    {'texto': '6.9 Sistema Corta Corriente', 'critico': False, 'orden': 9},
                    {'texto': '6.10 Desgaste Dientes', 'critico': False, 'orden': 10},
                    {'texto': '6.11 Estado de Mandos del Balde', 'critico': True, 'orden': 11},
                ]
            },
        ]
        
        self.crear_categorias_items(template, categorias_items)
        self.stdout.write(f'Creado checklist completo para Minicargador')

    def crear_checklist_cargador_frontal(self):
        """Crear checklist completo para cargador frontal"""
        template = ChecklistTemplate.objects.get(nombre='Check List Cargador Frontal (Diario)')
        
        # No eliminar categorías existentes, usar get_or_create
        
        categorias_items = [
            {
                'nombre': 'MOTOR',
                'orden': 1,
                'items': [
                    {'texto': '1.1 Nivel de Agua', 'critico': False, 'orden': 1},
                    {'texto': '1.2 Nivel de Aceite', 'critico': False, 'orden': 2},
                    {'texto': '1.3 Batería', 'critico': False, 'orden': 3},
                    {'texto': '1.4 Correas', 'critico': False, 'orden': 4},
                    {'texto': '1.5 Filtraciones', 'critico': False, 'orden': 5},
                    {'texto': '1.6 Alternador', 'critico': False, 'orden': 6},
                    {'texto': '1.7 Partida en Frío', 'critico': False, 'orden': 7},
                    {'texto': '1.8 Radiador / Anticongelante', 'critico': False, 'orden': 8},
                    {'texto': '1.9 Motor Arranque', 'critico': False, 'orden': 9},
                ]
            },
            {
                'nombre': 'LUCES',
                'orden': 2,
                'items': [
                    {'texto': '2.1 Luces Altas', 'critico': True, 'orden': 1},
                    {'texto': '2.2 Luces Bajas', 'critico': True, 'orden': 2},
                    {'texto': '2.3 Luces Intermitentes', 'critico': False, 'orden': 3},
                    {'texto': '2.4 Luz Marcha Atrás', 'critico': False, 'orden': 4},
                    {'texto': '2.5 Luz Tablero', 'critico': False, 'orden': 5},
                    {'texto': '2.6 Luz Baliza', 'critico': False, 'orden': 6},
                    {'texto': '2.7 Luz Pértiga', 'critico': False, 'orden': 7},
                    {'texto': '2.8 Luces de Freno', 'critico': False, 'orden': 8},
                    {'texto': '2.9 Estado de Micas', 'critico': False, 'orden': 9},
                    {'texto': '2.10 Luz Interior', 'critico': False, 'orden': 10},
                    {'texto': '2.11 Luz Patente', 'critico': False, 'orden': 11},
                ]
            },
            {
                'nombre': 'DOCUMENTOS',
                'orden': 3,
                'items': [
                    {'texto': '3.1 Permiso de Circulación', 'critico': False, 'orden': 1},
                    {'texto': '3.2 Revisión Técnica', 'critico': False, 'orden': 2},
                    {'texto': '3.3 Seguro Obligatorio', 'critico': False, 'orden': 3},
                ]
            },
            {
                'nombre': 'ACCESORIOS',
                'orden': 4,
                'items': [
                    {'texto': '4.1 Extintor', 'critico': True, 'orden': 1},
                    {'texto': '4.2 Triángulos / Conos', 'critico': False, 'orden': 2},
                    {'texto': '4.3 Cinturón de Seguridad', 'critico': False, 'orden': 3},
                    {'texto': '4.4 Marcadores', 'critico': False, 'orden': 4},
                    {'texto': '4.5 Señaléticas en Español', 'critico': False, 'orden': 5},
                    {'texto': '4.6 Manual de Operación', 'critico': False, 'orden': 6},
                    {'texto': '4.7 Sistema Corta Corriente', 'critico': False, 'orden': 7},
                    {'texto': '4.8 Revisión Tres Puntos de Apoyo', 'critico': False, 'orden': 8},
                    {'texto': '4.9 Protección Contra Volcamiento', 'critico': False, 'orden': 9},
                    {'texto': '4.10 Asiento Certificado', 'critico': False, 'orden': 10},
                    {'texto': '4.11 Estado de Neumáticos', 'critico': False, 'orden': 11},
                    {'texto': '4.12 Seguros en Tuercas', 'critico': False, 'orden': 12},
                    {'texto': '4.13 Dirección', 'critico': True, 'orden': 13},
                    {'texto': '4.14 Tubo de Escape', 'critico': False, 'orden': 14},
                    {'texto': '4.15 Parada de Emergencia', 'critico': False, 'orden': 15},
                    {'texto': '4.16 Escaleras de Acceso', 'critico': False, 'orden': 16},
                    {'texto': '4.17 Pasamanos', 'critico': False, 'orden': 17},
                    {'texto': '4.18 Bocina', 'critico': False, 'orden': 18},
                    {'texto': '4.19 Espejo Retrovisor', 'critico': True, 'orden': 19},
                ]
            },
            {
                'nombre': 'FRENOS',
                'orden': 5,
                'items': [
                    {'texto': '5.1 Freno de Servicio', 'critico': True, 'orden': 1},
                    {'texto': '5.2 Freno de Parqueo', 'critico': True, 'orden': 2},
                ]
            },
            {
                'nombre': 'CARGADOR FRONTAL',
                'orden': 6,
                'items': [
                    {'texto': '6.1 Grietas', 'critico': False, 'orden': 1},
                    {'texto': '6.2 Indicador de Ángulo', 'critico': False, 'orden': 2},
                    {'texto': '6.3 Calzas', 'critico': False, 'orden': 3},
                    {'texto': '6.4 Seguros', 'critico': False, 'orden': 4},
                    {'texto': '6.5 Balde', 'critico': False, 'orden': 5},
                    {'texto': '6.6 Sistema Hidráulico', 'critico': False, 'orden': 6},
                    {'texto': '6.7 Mangueras', 'critico': False, 'orden': 7},
                    {'texto': '6.8 Conexiones', 'critico': False, 'orden': 8},
                    {'texto': '6.9 Sistema Corta Corriente', 'critico': True, 'orden': 9},
                    {'texto': '6.10 Desgaste Dientes', 'critico': False, 'orden': 10},
                    {'texto': '6.11 Mandos Operacionales', 'critico': True, 'orden': 11},
                    {'texto': '6.12 Sistema de Levante', 'critico': False, 'orden': 12},
                    {'texto': '6.13 Sistema Engrase', 'critico': False, 'orden': 13},
                ]
            },
        ]
        
        self.crear_categorias_items(template, categorias_items)
        self.stdout.write(f'Creado checklist completo para Cargador Frontal')

    def crear_checklist_retroexcavadora(self):
        """Crear checklist completo para retroexcavadora"""
        template = ChecklistTemplate.objects.get(nombre='Check List Retroexcavadora (Diario)')
        
        # No eliminar categorías existentes, usar get_or_create
        
        categorias_items = [
            {
                'nombre': 'MOTOR',
                'orden': 1,
                'items': [
                    {'texto': '1.1 Nivel de Agua', 'critico': False, 'orden': 1},
                    {'texto': '1.2 Nivel de Aceite', 'critico': False, 'orden': 2},
                    {'texto': '1.3 Batería', 'critico': False, 'orden': 3},
                    {'texto': '1.4 Correas', 'critico': False, 'orden': 4},
                    {'texto': '1.5 Filtraciones', 'critico': False, 'orden': 5},
                    {'texto': '1.6 Nivel Hidráulico', 'critico': True, 'orden': 6},
                    {'texto': '1.7 Alternador', 'critico': False, 'orden': 7},
                    {'texto': '1.8 Partida en Frío', 'critico': False, 'orden': 8},
                    {'texto': '1.9 Radiador / Anticongelante', 'critico': False, 'orden': 9},
                    {'texto': '1.10 Motor Arranque', 'critico': False, 'orden': 10},
                ]
            },
            {
                'nombre': 'LUCES',
                'orden': 2,
                'items': [
                    {'texto': '2.1 Luces Altas', 'critico': True, 'orden': 1},
                    {'texto': '2.2 Luces Bajas', 'critico': False, 'orden': 2},
                    {'texto': '2.3 Luces Intermitentes', 'critico': False, 'orden': 3},
                    {'texto': '2.4 Luz Marcha Atrás', 'critico': False, 'orden': 4},
                    {'texto': '2.5 Luz Tablero', 'critico': False, 'orden': 5},
                    {'texto': '2.6 Luz Baliza', 'critico': False, 'orden': 6},
                    {'texto': '2.7 Luz Pértiga', 'critico': False, 'orden': 7},
                    {'texto': '2.8 Luces de Freno', 'critico': False, 'orden': 8},
                    {'texto': '2.9 Estado de Micas', 'critico': False, 'orden': 9},
                    {'texto': '2.10 Focos Faeneros', 'critico': False, 'orden': 10},
                    {'texto': '2.11 Luz Interior', 'critico': False, 'orden': 11},
                    {'texto': '2.12 Luz Patente', 'critico': False, 'orden': 12},
                ]
            },
            {
                'nombre': 'DOCUMENTOS',
                'orden': 3,
                'items': [
                    {'texto': '3.1 Permiso de Circulación (si aplicase)', 'critico': False, 'orden': 1},
                    {'texto': '3.2 Revisión Técnica (si aplicase)', 'critico': False, 'orden': 2},
                    {'texto': '3.3 Seguro Obligatorio (si aplicase)', 'critico': False, 'orden': 3},
                ]
            },
            {
                'nombre': 'ACCESORIOS',
                'orden': 4,
                'items': [
                    {'texto': '4.1 Extintor', 'critico': False, 'orden': 1},
                    {'texto': '4.2 Llave de Rueda', 'critico': False, 'orden': 2},
                    {'texto': '4.3 Conos', 'critico': False, 'orden': 3},
                    {'texto': '4.4 Cinturón de Seguridad', 'critico': False, 'orden': 4},
                    {'texto': '4.5 Marcadores', 'critico': False, 'orden': 5},
                    {'texto': '4.6 Señaléticas en Español', 'critico': False, 'orden': 6},
                    {'texto': '4.7 Manual de Operación', 'critico': False, 'orden': 7},
                    {'texto': '4.8 Sistema Corta Corriente', 'critico': False, 'orden': 8},
                    {'texto': '4.9 Revisión Tres Puntos de Apoyo', 'critico': False, 'orden': 9},
                    {'texto': '4.10 Protección Contra Volcamiento', 'critico': False, 'orden': 10},
                    {'texto': '4.11 Asiento Certificado', 'critico': False, 'orden': 11},
                    {'texto': '4.12 Estado de Neumáticos', 'critico': False, 'orden': 12},
                    {'texto': '4.13 Seguros en Tuercas', 'critico': False, 'orden': 13},
                    {'texto': '4.14 Dirección', 'critico': False, 'orden': 14},
                    {'texto': '4.15 Tubo de Escape', 'critico': False, 'orden': 15},
                    {'texto': '4.16 Parada de Emergencia', 'critico': False, 'orden': 16},
                    {'texto': '4.17 Escaleras de Acceso', 'critico': False, 'orden': 17},
                    {'texto': '4.18 Pasamanos', 'critico': False, 'orden': 18},
                    {'texto': '4.19 Bocina', 'critico': True, 'orden': 19},
                    {'texto': '4.20 Espejo Retrovisor', 'critico': False, 'orden': 20},
                    {'texto': '4.21 Limpiaparabrisas', 'critico': True, 'orden': 21},
                    {'texto': '4.22 Otros', 'critico': False, 'orden': 22},
                ]
            },
            {
                'nombre': 'FRENOS',
                'orden': 5,
                'items': [
                    {'texto': '5.1 Freno de Servicio', 'critico': True, 'orden': 1},
                    {'texto': '5.2 Freno de Parqueo', 'critico': True, 'orden': 2},
                ]
            },
            {
                'nombre': 'ELEMENTOS RETROEXCAVADORA',
                'orden': 6,
                'items': [
                    {'texto': '6.1 Juego Pasador Balde', 'critico': False, 'orden': 1},
                    {'texto': '6.2 Juego Bujes', 'critico': False, 'orden': 2},
                    {'texto': '6.3 Desgaste Cuchillos', 'critico': False, 'orden': 3},
                    {'texto': '6.4 Desgaste Dientes', 'critico': False, 'orden': 4},
                    {'texto': '6.5 Desgaste Cadena', 'critico': False, 'orden': 5},
                    {'texto': '6.6 Sistema Hidráulico', 'critico': False, 'orden': 6},
                    {'texto': '6.7 Mangueras', 'critico': False, 'orden': 7},
                    {'texto': '6.8 Conexiones', 'critico': False, 'orden': 8},
                    {'texto': '6.9 Sistema Corta Corriente', 'critico': True, 'orden': 9},
                    {'texto': '6.10 Estado de Aguilón', 'critico': False, 'orden': 10},
                    {'texto': '6.11 Martillo Hidráulico', 'critico': False, 'orden': 11},
                    {'texto': '6.12 Mandos Operacionales', 'critico': False, 'orden': 12},
                ]
            },
        ]
        
        self.crear_categorias_items(template, categorias_items)
        self.stdout.write(f'Creado checklist completo para Retroexcavadora')

    def crear_checklist_camionetas(self):
        """Crear checklist completo para camionetas"""
        template = ChecklistTemplate.objects.get(nombre='Check List Camionetas (Diario)')
        
        # No eliminar categorías existentes, usar get_or_create
        
        categorias_items = [
            {
                'nombre': 'INFORMACIÓN GENERAL',
                'orden': 1,
                'items': [
                    {'texto': '1.1 Licencia de Conducir Vigente', 'critico': False, 'orden': 1},
                    {'texto': '1.2 Conocimiento del Vehículo', 'critico': False, 'orden': 2},
                    {'texto': '1.3 Condiciones Físicas Aptas', 'critico': False, 'orden': 3},
                    {'texto': '1.4 Uso de EPP', 'critico': False, 'orden': 4},
                ]
            },
            {
                'nombre': 'DOCUMENTOS',
                'orden': 2,
                'items': [
                    {'texto': '2.1 Permiso de Circulación', 'critico': False, 'orden': 1},
                    {'texto': '2.2 Revisión Técnica', 'critico': False, 'orden': 2},
                    {'texto': '2.3 Seguro Obligatorio', 'critico': False, 'orden': 3},
                ]
            },
            {
                'nombre': 'REQUISITOS BÁSICOS',
                'orden': 3,
                'items': [
                    {'texto': '3.1 Cinturón de Seguridad', 'critico': False, 'orden': 1},
                    {'texto': '3.2 Frenos', 'critico': False, 'orden': 2},
                    {'texto': '3.3 Neumáticos', 'critico': False, 'orden': 3},
                    {'texto': '3.4 Luces', 'critico': False, 'orden': 4},
                    {'texto': '3.5 Dirección', 'critico': False, 'orden': 5},
                    {'texto': '3.6 Bocina', 'critico': False, 'orden': 6},
                    {'texto': '3.7 Espejos', 'critico': False, 'orden': 7},
                    {'texto': '3.8 Limpiaparabrisas', 'critico': False, 'orden': 8},
                    {'texto': '3.9 Parabrisas', 'critico': False, 'orden': 9},
                    {'texto': '3.10 Puertas', 'critico': False, 'orden': 10},
                ]
            },
            {
                'nombre': 'REQUISITOS COMPLEMENTARIOS',
                'orden': 4,
                'items': [
                    {'texto': '4.1 Extintor', 'critico': False, 'orden': 1},
                    {'texto': '4.2 Botiquín', 'critico': False, 'orden': 2},
                    {'texto': '4.3 Herramientas Básicas', 'critico': False, 'orden': 3},
                    {'texto': '4.4 Rueda de Repuesto', 'critico': False, 'orden': 4},
                    {'texto': '4.5 Gata', 'critico': False, 'orden': 5},
                    {'texto': '4.6 Llave de Rueda', 'critico': False, 'orden': 6},
                    {'texto': '4.7 Triángulos de Seguridad', 'critico': False, 'orden': 7},
                    {'texto': '4.8 Chaleco Reflectante', 'critico': False, 'orden': 8},
                ]
            },
            {
                'nombre': 'MOTOR Y FLUIDOS',
                'orden': 5,
                'items': [
                    {'texto': '5.1 Nivel de Aceite', 'critico': False, 'orden': 1},
                    {'texto': '5.2 Nivel de Agua/Refrigerante', 'critico': False, 'orden': 2},
                    {'texto': '5.3 Nivel de Combustible', 'critico': False, 'orden': 3},
                    {'texto': '5.4 Nivel de Líquido de Frenos', 'critico': False, 'orden': 4},
                    {'texto': '5.5 Batería', 'critico': False, 'orden': 5},
                    {'texto': '5.6 Correas', 'critico': False, 'orden': 6},
                    {'texto': '5.7 Filtraciones', 'critico': False, 'orden': 7},
                ]
            },
        ]
        
        self.crear_categorias_items(template, categorias_items)
        self.stdout.write(f'Creado checklist completo para Camionetas')

    def crear_categorias_items(self, template, categorias_items):
        """Método auxiliar para crear categorías e items"""
        for categoria_data in categorias_items:
            categoria, created = ChecklistCategory.objects.get_or_create(
                template=template,
                nombre=categoria_data['nombre'],
                defaults={'orden': categoria_data['orden']}
            )
            if created:
                self.stdout.write(f'Creada categoría: {categoria.nombre}')
            
            for item_data in categoria_data['items']:
                item, created = ChecklistItem.objects.get_or_create(
                    category=categoria,
                    texto=item_data['texto'],
                    defaults={
                        'es_critico': item_data['critico'],
                        'orden': item_data['orden']
                    }
                )
                if created:
                    self.stdout.write(f'  Creado item: {item.texto}')

