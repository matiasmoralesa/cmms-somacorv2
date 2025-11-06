# cmms_api/management/commands/crear_plantillas_checklist.py

from django.core.management.base import BaseCommand
from cmms_api.models import (
    TiposEquipo, ChecklistTemplate, ChecklistCategory, ChecklistItem
)

class Command(BaseCommand):
    help = 'Crea plantillas de checklist basadas en los PDFs analizados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tipo-equipo',
            type=str,
            help='Crear plantilla solo para un tipo de equipo específico'
        )

    def handle(self, *args, **options):
        tipo_equipo_filtro = options['tipo_equipo']
        
        self.stdout.write('Creando plantillas de checklist...')
        
        # Definir todas las plantillas
        plantillas = {
            'Minicargador': self._get_plantilla_minicargador(),
            'Cargador Frontal': self._get_plantilla_cargador_frontal(),
            'Retroexcavadora': self._get_plantilla_retroexcavadora(),
            'Camioneta': self._get_plantilla_camioneta(),
            'Camión Supersucker': self._get_plantilla_camion_supersucker()
        }
        
        for tipo_nombre, plantilla_data in plantillas.items():
            if tipo_equipo_filtro and tipo_equipo_filtro != tipo_nombre:
                continue
                
            try:
                tipo_equipo = TiposEquipo.objects.get(nombretipo=tipo_nombre)
                self._crear_plantilla(tipo_equipo, plantilla_data)
                self.stdout.write(f'Plantilla creada para: {tipo_nombre}')
            except TiposEquipo.DoesNotExist:
                self.stdout.write(f'Tipo de equipo no encontrado: {tipo_nombre}')

        self.stdout.write(
            self.style.SUCCESS('Plantillas de checklist creadas exitosamente')
        )

    def _crear_plantilla(self, tipo_equipo, plantilla_data):
        """
        Crea una plantilla de checklist con sus categorías e ítems
        """
        template, created = ChecklistTemplate.objects.get_or_create(
            nombre=plantilla_data['nombre'],
            defaults={'tipo_equipo': tipo_equipo}
        )
        
        if not created:
            # Si ya existe, limpiar categorías existentes
            template.categories.all().delete()
        
        for orden_cat, (nombre_categoria, items) in enumerate(plantilla_data['categorias'], 1):
            categoria = ChecklistCategory.objects.create(
                template=template,
                nombre=nombre_categoria,
                orden=orden_cat
            )
            
            for orden_item, (texto_item, es_critico) in enumerate(items, 1):
                ChecklistItem.objects.create(
                    category=categoria,
                    texto=texto_item,
                    es_critico=es_critico,
                    orden=orden_item
                )

    def _get_plantilla_minicargador(self):
        return {
            'nombre': 'Check List Minicargador (Diario)',
            'categorias': [
                ('MOTOR', [
                    ('Nivel de Agua', True),
                    ('Nivel de Aceite', True),
                    ('Nivel de Líquido de Freno', True),
                    ('Combustible', False),
                    ('Batería', False),
                    ('Correas', False),
                    ('Filtraciones', False),
                    ('Alternador', False),
                    ('Partida en Frío', False),
                    ('Radiador / Anticongelante', False),
                    ('Motor Arranque', False)
                ]),
                ('LUCES', [
                    ('Luces Altas', True),
                    ('Luces Bajas', True),
                    ('Luces Intermitentes', False),
                    ('Luz Marcha Atrás', False),
                    ('Focos Faeneros', False),
                    ('Luz Patente', False),
                    ('Luz Tablero', False),
                    ('Luz Baliza', False),
                    ('Luz Pértiga', False),
                    ('Luces de Freno', False),
                    ('Estado de Micas', False)
                ]),
                ('DOCUMENTOS', [
                    ('Permiso de Circulación', False),
                    ('Revisión Técnica', False),
                    ('Seguro Obligatorio', False)
                ]),
                ('ACCESORIOS', [
                    ('Botiquín', False),
                    ('Extintor (8-10 kilos) (A-B-C) /Sistema AFEX', False),
                    ('Llave de Rueda', False),
                    ('Triángulos / Conos', False),
                    ('Cinturón de Seguridad', True),
                    ('Marcadores', True),
                    ('Señaléticas en Español', False),
                    ('Manual de operación en Español', False),
                    ('Instrumentos en buen estado', False),
                    ('Sistema Corta corriente', True),
                    ('Revisión de tres puntos de apoyo', False),
                    ('Puerta en buen estado', False),
                    ('Chapas de Puertas', False),
                    ('Manillas de Puertas', False),
                    ('Limpia parabrisas', False),
                    ('Cinta reflectante', False),
                    ('Vidrios', False),
                    ('Protección contra volcamiento', False),
                    ('Asiento con regulador y certificado', True),
                    ('Espejo Retrovisor', False),
                    ('Espejos Laterales', False),
                    ('Estado de Carrocería en General', False),
                    ('Bocina / Alarma de Retroceso', False),
                    ('Aire Acondicionado', False),
                    ('Cuñas', False),
                    ('Estado de neumáticos', True),
                    ('Seguros en tuercas', False),
                    ('Dirección (Mecánica o Hidráulica)', True),
                    ('Tubo de Escape', False),
                    ('Parada de Emergencia Exterior Equipo', False),
                    ('Se ha sobrecargado el sistema eléctrico original del equipo?', True)
                ]),
                ('ESTADO MECÁNICO', [
                    ('Avanzar', True),
                    ('Retroceder', True)
                ]),
                ('FRENOS', [
                    ('Freno de Servicio', True),
                    ('Freno de Parqueo', True)
                ]),
                ('CARGADOR', [
                    ('Balde', False),
                    ('Cuchillo de balde', False),
                    ('Porte cuchilla balde', False),
                    ('Seguros manuales de balde', False),
                    ('Conexión inferior', False),
                    ('Sistema hidráulico', False),
                    ('Mangueras hidráulicas', False),
                    ('Conexiones hidráulicas', False),
                    ('Sistema Corta Corriente', True),
                    ('Desgaste dientes', False),
                    ('Estado de los mandos del balde', True)
                ])
            ]
        }

    def _get_plantilla_cargador_frontal(self):
        return {
            'nombre': 'Check List Cargador Frontal (Diario)',
            'categorias': [
                ('MOTOR', [
                    ('Nivel de Agua', False),
                    ('Nivel de Aceite', False),
                    ('Nivel de Líquido de Freno', False),
                    ('Batería', False),
                    ('Correas', False),
                    ('Filtraciones', False),
                    ('Alternador', False),
                    ('Partida en Frío', False),
                    ('Radiador / Anticongelante', False),
                    ('Motor Arranque', False)
                ]),
                ('LUCES', [
                    ('Luces Altas', True),
                    ('Luces Bajas', True),
                    ('Luces Intermitentes', False),
                    ('Luz Marcha Atrás', False),
                    ('Luz Interior', False),
                    ('Luz Patente', False),
                    ('Luz Tablero', False),
                    ('Luz Baliza', False),
                    ('Luz Pértiga', False),
                    ('Luces de Freno', False),
                    ('Estado de Micas', False)
                ]),
                ('DOCUMENTOS', [
                    ('Permiso de Circulación', False),
                    ('Revisión Técnica', False),
                    ('Seguro Obligatorio', False)
                ]),
                ('ACCESORIOS', [
                    ('Cinturón de Seguridad', True),
                    ('Extintor (8-10 kilos) (A-B-C)/ Sistema AFEX', False),
                    ('Marcadores', False),
                    ('Triángulos / Conos', False),
                    ('Chapas de Puertas', False),
                    ('Calefacción', False),
                    ('Limpia parabrisas', False),
                    ('Vidrios', False),
                    ('Manillas de Puertas', False),
                    ('Asiento', False),
                    ('Espejo Retrovisor', False),
                    ('Espejos Laterales', False),
                    ('Estado de Carrocería en General', True),
                    ('Bocina / Alarma de Retroceso', False),
                    ('Aire Acondicionado', False),
                    ('Cuñas', False),
                    ('Estado de neumáticos', False),
                    ('Seguros en tuercas', False),
                    ('Dirección (Mecánica o Hidráulica)', True),
                    ('Tubo de Escape', False),
                    ('Estado pasamanos', False),
                    ('Escaleras de acceso', False),
                    ('Se ha sobrecargado el sistema eléctrico original del equipo?', False)
                ]),
                ('FRENOS', [
                    ('Freno de Servicio', True),
                    ('Freno de Parqueo', True)
                ]),
                ('CARGADOR FRONTAL', [
                    ('Grietas', False),
                    ('Indicador de Angulo', False),
                    ('Calzas', False),
                    ('Seguros', False),
                    ('Balde', False),
                    ('Sistema hidráulico', False),
                    ('Mangueras hidráulicas', False),
                    ('Conexiones hidráulicas', False),
                    ('Sistema Corta Corriente', True),
                    ('Desgaste dientes', False),
                    ('Mandos Operacional', True),
                    ('Sistema de Levante', False),
                    ('Sistema Engrase', False)
                ])
            ]
        }

    def _get_plantilla_retroexcavadora(self):
        return {
            'nombre': 'Inspección Retroexcavadora (Diario)',
            'categorias': [
                ('MOTOR', [
                    ('Nivel de Agua', False),
                    ('Nivel de Aceite', False),
                    ('Nivel de Hidraulico', False),
                    ('Batería', False),
                    ('Correas', False),
                    ('Filtraciones (Aceite / Combustible)', True),
                    ('Alternador', False),
                    ('Partida en Frío', False),
                    ('Radiador / Anticongelante', False),
                    ('Motor Arranque', False)
                ]),
                ('LUCES', [
                    ('Focos faeneros', True),
                    ('Luces Bajas', False),
                    ('Luces Intermitentes', False),
                    ('Luz Marcha Atrás', False),
                    ('Luz Interior', False),
                    ('Luz Patente', False),
                    ('Luz Tablero', False),
                    ('Luz Baliza', False),
                    ('Luz Pértiga', False),
                    ('Luces de Freno', False),
                    ('Estado de Micas', False)
                ]),
                ('DOCUMENTOS VIGENTES', [
                    ('Permiso de Circulación ( si aplicase)', False),
                    ('Revisión Técnica ( si aplicase)', False),
                    ('Seguro Obligatorio ( si aplicase)', False)
                ]),
                ('ACCESORIOS', [
                    ('Extintor (8-10 kilos) (A-B-C)/Sistema AFEX', False),
                    ('Llave de Rueda', False),
                    ('Conos', False),
                    ('Cinturón de Seguridad', False),
                    ('Otros', False),
                    ('Chapas de Puertas', False),
                    ('Calefacción', False),
                    ('Limpia parabrisas', False),
                    ('Vidrios', False),
                    ('Manillas de Puertas', False),
                    ('Asiento', False),
                    ('Espejo Retrovisor', False),
                    ('Espejos Laterales', False),
                    ('Estado de Carrocería en General', False),
                    ('Bocina / Alarma de Retroceso', False),
                    ('Aire Acondicionado', False),
                    ('Cuñas', False),
                    ('Estado de neumáticos', True),
                    ('Seguros en tuercas', False),
                    ('Dirección (Mecánica o Hidráulica)', True),
                    ('Tubo de Escape', False)
                ]),
                ('FRENOS', [
                    ('Freno de Servicio', True),
                    ('Freno Parqueo', True)
                ]),
                ('ELEMENTOS RETROEXCAVADORA', [
                    ('Juego Pasador Balde', False),
                    ('Juego Bujes', False),
                    ('Desgaste Cuchillos', False),
                    ('Desgaste Dientes', False),
                    ('Degaste Cadena', False),
                    ('Sistema Hidráulico', False),
                    ('Mangueras Hidráulicas', False),
                    ('Conexiones Hidráulicas', False),
                    ('Sistema corta corriente', True),
                    ('Estado de Aguilón', False),
                    ('Martillo Hidráulico', False),
                    ('Mandos Operacionales', False),
                    ('Otros', False)
                ])
            ]
        }

    def _get_plantilla_camioneta(self):
        return {
            'nombre': 'Check List Camionetas (Diario)',
            'categorias': [
                ('AUTO EVALUACION DEL OPERADOR', [
                    ('Cumplo con descanso suficiente y condiciones para manejo seguro', False),
                    ('Cumplo con condiciones físicas adecuadas y no tengo dolencias o enfermedades que me impidan conducir', False),
                    ('Estoy conciente de mi responsabilidad al conducir, sin poner en riesgo mi integridad ni la de mis compañeros o de patrimonio de la empresa', False)
                ]),
                ('DOCUMENTACION DEL OPERADOR', [
                    ('Licencia Municipal', False),
                    ('Licencia interna de Faena', False)
                ]),
                ('REQUISITOS', [
                    ('Aire acondicionado/ calefacción', False),
                    ('Baliza y pertiga (funcionando y en condiciones)', False),
                    ('Bocina en buen estado', False),
                    ('Cinturones de Seguridad en buen estado', False),
                    ('Cuñas de seguridad disponibles (2)', False),
                    ('Espejos interior y exterior en condiciones y limpios', False),
                    ('Frenos (incluye freno de mano) en condiciones operativas', False),
                    ('Neumáticos en buen estado (incluye dos repuestos)', False),
                    ('Luces (Altas, Bajas, Frenos, intermitentes, retroceso)', False),
                    ('Sello caja de operación invierno en buenas condiciones', False)
                ]),
                ('CONDICIONES PARA REQUISITOS COMPLEMENTARIOS', [
                    ('Orden y Aseo (interior vehículo y pick up)', False),
                    ('Estado de carroceria, parachoques, portalón', False),
                    ('Gata y llave de rueda disponible', False),
                    ('Vidrios y parabrisas limpios', False),
                    ('Limpiaparabrisas funciona correctamente', False),
                    ('Radio Base funciona en todos los canales', False)
                ]),
                ('DOCUMENTACION', [
                    ('Permiso de Circulación', False),
                    ('Revisión Técnica', False),
                    ('Seguro Obligatorio', False)
                ])
            ]
        }

    def _get_plantilla_camion_supersucker(self):
        return {
            'nombre': 'Check-List Camión Supersucker',
            'categorias': [
                ('LUCES', [
                    ('Luz baja', False),
                    ('Luz Alta', False),
                    ('Luz Marcha Atrás', False),
                    ('Luz Interior', False),
                    ('Luz de Freno', False),
                    ('Tercera Luz de Freno', False),
                    ('Intermitentes', False),
                    ('Luz Patente', False),
                    ('Baliza y conexión eléctrica', False),
                    ('Pértiga y conexión eléctrica', False)
                ]),
                ('ACCESORIOS', [
                    ('Barra interna /certificado', False),
                    ('Extintor, Botiquín, Triángulos', False),
                    ('Cinturón de Seguridad', False),
                    ('Chapas de Puertas', False),
                    ('Bocina', False),
                    ('Parabrisas', False),
                    ('Vidrios laterales', False),
                    ('Bolso Herramientas', False),
                    ('Manillas Alza vidrios', False),
                    ('Batería', False),
                    ('Nivel de Agua', False),
                    ('Nivel de Aceite', False),
                    ('Espejos Retrovisores', False),
                    ('Logotipo', False),
                    ('Cuñas', False),
                    ('Gata. y manivela', False),
                    ('Llave rueda', False),
                    ('Plumillas Limpia Vidrios', False),
                    ('Correas de accesorios', False),
                    ('Estrobos remolque', False),
                    ('Verificar gases de escape', False),
                    ('Linterna', False),
                    ('Frazadas', False)
                ]),
                ('NEUMÁTICOS', [
                    ('Delanteros', False),
                    ('Traseros', False),
                    ('Repuestos', False),
                    ('revisión de Tuercas', False)
                ]),
                ('DOCUMENTOS', [
                    ('Permiso de Circulación', False),
                    ('Revisión Técnica', False),
                    ('Tarjeta de mantención', False),
                    ('Seguro Obligatorio', False),
                    ('Tarjeta o llave combustible', False),
                    ('G.P.S.', False)
                ]),
                ('ASPIRADO', [
                    ('Bomba aspiradora', False),
                    ('Inspección ducto de succión', False),
                    ('Inspección mangueras de succión', False),
                    ('Sistema control descarga hidráulico', False)
                ]),
                ('ALTA MONTAÑA', [
                    ('Saco', False),
                    ('Cadenas para nieve', False),
                    ('Tensores de cadenas', False),
                    ('Pala', False)
                ])
            ]
        }

