from django.core.management.base import BaseCommand
from cmms_api.models import (
    TiposEquipo, ChecklistTemplate, ChecklistCategory, ChecklistItem
)

class Command(BaseCommand):
    help = 'Poblar templates de checklist para todos los tipos de equipos'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando población de templates de checklist...')
        
        # Crear templates para cada tipo de equipo
        self.crear_template_minicargador()
        self.crear_template_cargador_frontal()
        self.crear_template_retroexcavadora()
        self.crear_template_camionetas()
        
        self.stdout.write(
            self.style.SUCCESS('Templates de checklist creados exitosamente!')
        )

    def crear_template_minicargador(self):
        """Crear template para minicargador"""
        try:
            tipo_equipo = TiposEquipo.objects.get(nombretipo__icontains='minicargador')
        except TiposEquipo.DoesNotExist:
            self.stdout.write(
                self.style.WARNING('Tipo de equipo "minicargador" no encontrado. Creándolo...')
            )
            tipo_equipo = TiposEquipo.objects.create(nombretipo='Minicargador')

        template, created = ChecklistTemplate.objects.get_or_create(
            nombre='Check List Minicargador (Diario)',
            tipo_equipo=tipo_equipo,
            defaults={'activo': True}
        )
        
        if not created:
            self.stdout.write('Template de minicargador ya existe, actualizando...')
            # Limpiar categorías existentes
            template.categories.all().delete()

        # 1. MOTOR
        cat_motor = ChecklistCategory.objects.create(
            template=template, nombre='MOTOR', orden=1
        )
        items_motor = [
            ('Nivel de Agua', False, 1),
            ('Nivel de Aceite', True, 2),
            ('Nivel de Líquido de Freno', True, 3),
            ('Combustible', False, 4),
            ('Batería', False, 5),
            ('Correas', False, 6),
            ('Filtraciones', False, 7),
            ('Alternador', False, 8),
            ('Partida en Frío', False, 9),
            ('Radiador / Anticongelante', False, 10),
            ('Motor Arranque', False, 11),
        ]
        for texto, critico, orden in items_motor:
            ChecklistItem.objects.create(
                category=cat_motor, texto=texto, es_critico=critico, orden=orden
            )

        # 2. LUCES
        cat_luces = ChecklistCategory.objects.create(
            template=template, nombre='LUCES', orden=2
        )
        items_luces = [
            ('Luces Altas', True, 1),
            ('Luces Bajas', True, 2),
            ('Luces Intermitentes', False, 3),
            ('Luz Marcha Atrás', False, 4),
            ('Focos Faeneros', False, 5),
            ('Luz Patente', False, 6),
            ('Luz Tablero', False, 7),
            ('Luz Baliza', False, 8),
            ('Luz Pértiga', False, 9),
            ('Luces de Freno', False, 10),
            ('Estado de Micas', False, 11),
        ]
        for texto, critico, orden in items_luces:
            ChecklistItem.objects.create(
                category=cat_luces, texto=texto, es_critico=critico, orden=orden
            )

        # 3. DOCUMENTOS
        cat_docs = ChecklistCategory.objects.create(
            template=template, nombre='DOCUMENTOS', orden=3
        )
        items_docs = [
            ('Permiso de Circulación', False, 1),
            ('Revisión Técnica', False, 2),
            ('Seguro Obligatorio', False, 3),
        ]
        for texto, critico, orden in items_docs:
            ChecklistItem.objects.create(
                category=cat_docs, texto=texto, es_critico=critico, orden=orden
            )

        # 4. ACCESORIOS
        cat_acc = ChecklistCategory.objects.create(
            template=template, nombre='ACCESORIOS', orden=4
        )
        items_acc = [
            ('Botiquín', False, 1),
            ('Extintor (8-10 kilos) (A-B-C) /Sistema AFEX', False, 2),
            ('Llave de Rueda', False, 3),
            ('Triángulos / Conos', False, 4),
            ('Cinturón de Seguridad', True, 5),
            ('Marcadores', True, 6),
            ('Señaléticas en Español', False, 7),
            ('Manual de operación en Español', False, 8),
            ('Instrumentos en buen estado', False, 9),
            ('Sistema Corta corriente', True, 10),
            ('Revisión de tres puntos de apoyo', False, 11),
            ('Puerta en buen estado', False, 12),
            ('Chapas de Puertas', False, 13),
            ('Manillas de Puertas', False, 14),
            ('Limpia parabrisas', False, 15),
            ('Cinta reflectante', False, 16),
            ('Vidrios', False, 17),
            ('Protección contra volcamiento', False, 18),
            ('Asiento con regulador y certificado', True, 19),
            ('Espejo Retrovisor', False, 20),
            ('Espejos Laterales', False, 21),
            ('Estado de Carrocería en General', False, 22),
            ('Bocina / Alarma de Retroceso', False, 23),
            ('Aire Acondicionado', False, 24),
            ('Cuñas', False, 25),
            ('Estado de neumáticos', True, 26),
            ('Seguros en tuercas', False, 27),
            ('Dirección (Mecánica o Hidráulica)', True, 28),
            ('Tubo de Escape', False, 29),
            ('Parada de Emergencia Exterior Equipo', False, 30),
            ('Se ha sobrecargado el sistema eléctrico original del equipo?', True, 31),
        ]
        for texto, critico, orden in items_acc:
            ChecklistItem.objects.create(
                category=cat_acc, texto=texto, es_critico=critico, orden=orden
            )

        # 5. ESTADO MECÁNICO
        cat_mec = ChecklistCategory.objects.create(
            template=template, nombre='ESTADO MECÁNICO', orden=5
        )
        items_mec = [
            ('Avanzar', True, 1),
            ('Retroceder', True, 2),
        ]
        for texto, critico, orden in items_mec:
            ChecklistItem.objects.create(
                category=cat_mec, texto=texto, es_critico=critico, orden=orden
            )

        # 6. FRENOS
        cat_frenos = ChecklistCategory.objects.create(
            template=template, nombre='FRENOS', orden=6
        )
        items_frenos = [
            ('Freno de Servicio', True, 1),
            ('Freno de Parqueo', True, 2),
        ]
        for texto, critico, orden in items_frenos:
            ChecklistItem.objects.create(
                category=cat_frenos, texto=texto, es_critico=critico, orden=orden
            )

        # 7. CARGADOR
        cat_cargador = ChecklistCategory.objects.create(
            template=template, nombre='CARGADOR', orden=7
        )
        items_cargador = [
            ('Balde', False, 1),
            ('Cuchillo de balde', False, 2),
            ('Porte cuchilla balde', False, 3),
            ('Seguros manuales de balde', False, 4),
            ('Conexión inferior', False, 5),
            ('Sistema hidráulico', False, 6),
            ('Mangueras hidráulicas', False, 7),
            ('Conexiones hidráulicas', False, 8),
            ('Sistema Corta Corriente', False, 9),
            ('Desgaste dientes', False, 10),
            ('Estado de los mandos del balde', True, 11),
        ]
        for texto, critico, orden in items_cargador:
            ChecklistItem.objects.create(
                category=cat_cargador, texto=texto, es_critico=critico, orden=orden
            )

        self.stdout.write('✓ Template de Minicargador creado')

    def crear_template_cargador_frontal(self):
        """Crear template para cargador frontal"""
        try:
            tipo_equipo = TiposEquipo.objects.get(nombretipo__icontains='cargador frontal')
        except TiposEquipo.DoesNotExist:
            self.stdout.write(
                self.style.WARNING('Tipo de equipo "cargador frontal" no encontrado. Creándolo...')
            )
            tipo_equipo = TiposEquipo.objects.create(nombretipo='Cargador Frontal')

        template, created = ChecklistTemplate.objects.get_or_create(
            nombre='Check List Cargador Frontal (Diario)',
            tipo_equipo=tipo_equipo,
            defaults={'activo': True}
        )
        
        if not created:
            template.categories.all().delete()

        # 1. MOTOR
        cat_motor = ChecklistCategory.objects.create(
            template=template, nombre='MOTOR', orden=1
        )
        items_motor = [
            ('Nivel de Agua', False, 1),
            ('Nivel de Aceite', False, 2),
            ('Nivel de Líquido de Freno', False, 3),
            ('Batería', False, 4),
            ('Correas', False, 5),
            ('Filtraciones', False, 6),
            ('Alternador', False, 7),
            ('Partida en Frío', False, 8),
            ('Radiador / Anticongelante', False, 9),
            ('Motor Arranque', False, 10),
        ]
        for texto, critico, orden in items_motor:
            ChecklistItem.objects.create(
                category=cat_motor, texto=texto, es_critico=critico, orden=orden
            )

        # 2. LUCES
        cat_luces = ChecklistCategory.objects.create(
            template=template, nombre='LUCES', orden=2
        )
        items_luces = [
            ('Luces Altas', True, 1),
            ('Luces Bajas', True, 2),
            ('Luces Intermitentes', False, 3),
            ('Luz Marcha Atrás', False, 4),
            ('Luz Interior', False, 5),
            ('Luz Patente', False, 6),
            ('Luz Tablero', False, 7),
            ('Luz Baliza', False, 8),
            ('Luz Pértiga', False, 9),
            ('Luces de Freno', False, 10),
            ('Estado de Micas', False, 11),
        ]
        for texto, critico, orden in items_luces:
            ChecklistItem.objects.create(
                category=cat_luces, texto=texto, es_critico=critico, orden=orden
            )

        # 3. DOCUMENTOS
        cat_docs = ChecklistCategory.objects.create(
            template=template, nombre='DOCUMENTOS', orden=3
        )
        items_docs = [
            ('Permiso de Circulación', False, 1),
            ('Revisión Técnica', False, 2),
            ('Seguro Obligatorio', False, 3),
        ]
        for texto, critico, orden in items_docs:
            ChecklistItem.objects.create(
                category=cat_docs, texto=texto, es_critico=critico, orden=orden
            )

        # 4. ACCESORIOS
        cat_acc = ChecklistCategory.objects.create(
            template=template, nombre='ACCESORIOS', orden=4
        )
        items_acc = [
            ('Cinturón de Seguridad', True, 1),
            ('Extintor (8-10 kilos) (A-B-C)/ Sistema AFEX', False, 2),
            ('Marcadores', False, 3),
            ('Triángulos / Conos', False, 4),
            ('Chapas de Puertas', False, 5),
            ('Calefacción', False, 6),
            ('Limpia parabrisas', False, 7),
            ('Vidrios', False, 8),
            ('Manillas de Puertas', False, 9),
            ('Asiento', False, 10),
            ('Espejo Retrovisor', False, 11),
            ('Espejos Laterales', False, 12),
            ('Estado de Carrocería en General', True, 13),
            ('Bocina / Alarma de Retroceso', False, 14),
            ('Aire Acondicionado', False, 15),
            ('Cuñas', False, 16),
            ('Estado de neumáticos', False, 17),
            ('Seguros en tuercas', False, 18),
            ('Dirección (Mecánica o Hidráulica)', True, 19),
            ('Tubo de Escape', False, 20),
            ('Estado pasamanos', False, 21),
            ('Escaleras de acceso', False, 22),
            ('Se ha sobrecargado el sistema eléctrico original del equipo?', False, 23),
        ]
        for texto, critico, orden in items_acc:
            ChecklistItem.objects.create(
                category=cat_acc, texto=texto, es_critico=critico, orden=orden
            )

        # 5. FRENOS
        cat_frenos = ChecklistCategory.objects.create(
            template=template, nombre='FRENOS', orden=5
        )
        items_frenos = [
            ('Freno de Servicio', True, 1),
            ('Freno de Parqueo', True, 2),
        ]
        for texto, critico, orden in items_frenos:
            ChecklistItem.objects.create(
                category=cat_frenos, texto=texto, es_critico=critico, orden=orden
            )

        # 6. CARGADOR FRONTAL
        cat_cargador = ChecklistCategory.objects.create(
            template=template, nombre='CARGADOR FRONTAL', orden=6
        )
        items_cargador = [
            ('Grietas', False, 1),
            ('Indicador de Angulo', False, 2),
            ('Calzas', False, 3),
            ('Seguros', False, 4),
            ('Balde', False, 5),
            ('Sistema hidráulico', False, 6),
            ('Mangueras hidráulicas', False, 7),
            ('Conexiones hidráulicas', False, 8),
            ('Sistema Corta Corriente', True, 9),
            ('Desgaste dientes', False, 10),
            ('Mandos Operacional', True, 11),
            ('Sistema de Levante', False, 12),
            ('Sistema Engrase', False, 13),
        ]
        for texto, critico, orden in items_cargador:
            ChecklistItem.objects.create(
                category=cat_cargador, texto=texto, es_critico=critico, orden=orden
            )

        self.stdout.write('✓ Template de Cargador Frontal creado')

    def crear_template_retroexcavadora(self):
        """Crear template para retroexcavadora"""
        try:
            tipo_equipo = TiposEquipo.objects.get(nombretipo__icontains='retroexcavadora')
        except TiposEquipo.DoesNotExist:
            self.stdout.write(
                self.style.WARNING('Tipo de equipo "retroexcavadora" no encontrado. Creándolo...')
            )
            tipo_equipo = TiposEquipo.objects.create(nombretipo='Retroexcavadora')

        template, created = ChecklistTemplate.objects.get_or_create(
            nombre='Inspección Retroexcavadora (Diario)',
            tipo_equipo=tipo_equipo,
            defaults={'activo': True}
        )
        
        if not created:
            template.categories.all().delete()

        # 1. MOTOR
        cat_motor = ChecklistCategory.objects.create(
            template=template, nombre='MOTOR', orden=1
        )
        items_motor = [
            ('Nivel de Agua', False, 1),
            ('Nivel de Aceite', False, 2),
            ('Nivel de Hidraulico', False, 3),
            ('Batería', False, 4),
            ('Correas', False, 5),
            ('Filtraciones (Aceite / Combustible)', True, 6),
            ('Alternador', False, 7),
            ('Partida en Frío', False, 8),
            ('Radiador / Anticongelante', False, 9),
            ('Motor Arranque', False, 10),
        ]
        for texto, critico, orden in items_motor:
            ChecklistItem.objects.create(
                category=cat_motor, texto=texto, es_critico=critico, orden=orden
            )

        # 2. LUCES
        cat_luces = ChecklistCategory.objects.create(
            template=template, nombre='LUCES', orden=2
        )
        items_luces = [
            ('Focos faeneros', True, 1),
            ('Luces Bajas', False, 2),
            ('Luces Intermitentes', False, 3),
            ('Luz Marcha Atrás', False, 4),
            ('Luz Interior', False, 5),
            ('Luz Patente', False, 6),
            ('Luz Tablero', False, 7),
            ('Luz Baliza', False, 8),
            ('Luz Pértiga', False, 9),
            ('Luces de Freno', False, 10),
            ('Estado de Micas', False, 11),
        ]
        for texto, critico, orden in items_luces:
            ChecklistItem.objects.create(
                category=cat_luces, texto=texto, es_critico=critico, orden=orden
            )

        # 3. DOCUMENTOS VIGENTES
        cat_docs = ChecklistCategory.objects.create(
            template=template, nombre='DOCUMENTOS VIGENTES', orden=3
        )
        items_docs = [
            ('Permiso de Circulación (si aplicase)', False, 1),
            ('Revisión Técnica (si aplicase)', False, 2),
            ('Seguro Obligatorio (si aplicase)', False, 3),
        ]
        for texto, critico, orden in items_docs:
            ChecklistItem.objects.create(
                category=cat_docs, texto=texto, es_critico=critico, orden=orden
            )

        # 4. ACCESORIOS
        cat_acc = ChecklistCategory.objects.create(
            template=template, nombre='ACCESORIOS', orden=4
        )
        items_acc = [
            ('Extintor (8-10 kilos) (A-B-C)/Sistema AFEX', False, 1),
            ('Llave de Rueda', False, 2),
            ('Conos', False, 3),
            ('Cinturón de Seguridad', False, 4),
            ('Otros', False, 5),
            ('Chapas de Puertas', False, 7),
            ('Calefacción', False, 8),
            ('Limpia parabrisas', False, 9),
            ('Vidrios', False, 10),
            ('Manillas de Puertas', False, 11),
            ('Asiento', False, 12),
            ('Espejo Retrovisor', False, 13),
            ('Espejos Laterales', False, 14),
            ('Estado de Carrocería en General', False, 15),
            ('Bocina / Alarma de Retroceso', False, 16),
            ('Aire Acondicionado', False, 17),
            ('Cuñas', False, 18),
            ('Estado de neumáticos', True, 19),
            ('Seguros en tuercas', False, 20),
            ('Dirección (Mecánica o Hidráulica)', True, 21),
            ('Tubo de Escape', False, 22),
        ]
        for texto, critico, orden in items_acc:
            ChecklistItem.objects.create(
                category=cat_acc, texto=texto, es_critico=critico, orden=orden
            )

        # 5. FRENOS
        cat_frenos = ChecklistCategory.objects.create(
            template=template, nombre='FRENOS', orden=5
        )
        items_frenos = [
            ('Freno de Servicio', True, 1),
            ('Freno Parqueo', True, 2),
        ]
        for texto, critico, orden in items_frenos:
            ChecklistItem.objects.create(
                category=cat_frenos, texto=texto, es_critico=critico, orden=orden
            )

        # 6. ELEMENTOS RETROEXCAVADORA
        cat_retro = ChecklistCategory.objects.create(
            template=template, nombre='ELEMENTOS RETROEXCAVADORA', orden=6
        )
        items_retro = [
            ('Juego Pasador Balde', False, 1),
            ('Juego Bujes', False, 2),
            ('Desgaste Cuchillos', False, 3),
            ('Desgaste Dientes', False, 4),
            ('Degaste Cadena', False, 5),
            ('Sistema Hidráulico', False, 6),
            ('Mangueras Hidráulicas', False, 7),
            ('Conexiones Hidráulicas', False, 8),
            ('Sistema corta corriente', True, 9),
            ('Estado de Aguilón', False, 10),
            ('Martillo Hidráulico', False, 11),
            ('Mandos Operacionales', False, 12),
            ('Otros', False, 13),
        ]
        for texto, critico, orden in items_retro:
            ChecklistItem.objects.create(
                category=cat_retro, texto=texto, es_critico=critico, orden=orden
            )

        self.stdout.write('✓ Template de Retroexcavadora creado')

    def crear_template_camionetas(self):
        """Crear template para camionetas"""
        try:
            tipo_equipo = TiposEquipo.objects.get(nombretipo__icontains='camioneta')
        except TiposEquipo.DoesNotExist:
            self.stdout.write(
                self.style.WARNING('Tipo de equipo "camioneta" no encontrado. Creándolo...')
            )
            tipo_equipo = TiposEquipo.objects.create(nombretipo='Camioneta')

        template, created = ChecklistTemplate.objects.get_or_create(
            nombre='Check List Camionetas (Diario)',
            tipo_equipo=tipo_equipo,
            defaults={'activo': True}
        )
        
        if not created:
            template.categories.all().delete()

        # 1. AUTO EVALUACION DEL OPERADOR
        cat_auto = ChecklistCategory.objects.create(
            template=template, nombre='AUTO EVALUACION DEL OPERADOR', orden=1
        )
        items_auto = [
            ('Cumplo con descanso suficiente y condiciones para manejo seguro', False, 1),
            ('Cumplo con condiciones físicas adecuadas y no tengo dolencias o enfermedades que me impidan conducir', False, 2),
            ('Estoy conciente de mi responsabilidad al conducir, sin poner en riesgo mi integridad ni la de mis compañeros o de patrimonio de la empresa', False, 3),
        ]
        for texto, critico, orden in items_auto:
            ChecklistItem.objects.create(
                category=cat_auto, texto=texto, es_critico=critico, orden=orden
            )

        # 2. DOCUMENTACION DEL OPERADOR
        cat_doc_op = ChecklistCategory.objects.create(
            template=template, nombre='DOCUMENTACION DEL OPERADOR', orden=2
        )
        items_doc_op = [
            ('Licencia Municipal', False, 1),
            ('Licencia interna de Faena', False, 2),
        ]
        for texto, critico, orden in items_doc_op:
            ChecklistItem.objects.create(
                category=cat_doc_op, texto=texto, es_critico=critico, orden=orden
            )

        # 3. REQUISITOS
        cat_req = ChecklistCategory.objects.create(
            template=template, nombre='REQUISITOS', orden=3
        )
        items_req = [
            ('Aire acondicionado/ calefacción', False, 1),
            ('Baliza y pertiga (funcionando y en condiciones)', False, 2),
            ('Bocina en buen estado', False, 3),
            ('Cinturones de Seguridad en buen estado', False, 4),
            ('Cuñas de seguridad disponibles (2)', False, 5),
            ('Espejos interior y exterior en condiciones y limpios', False, 6),
            ('Frenos (incluye freno de mano) en condiciones operativas', False, 7),
            ('Neumáticos en buen estado (incluye dos repuestos)', False, 8),
            ('Luces (Altas, Bajas, Frenos, intermitentes, retroceso)', False, 9),
            ('Sello caja de operación invierno en buenas condiciones', False, 10),
        ]
        for texto, critico, orden in items_req:
            ChecklistItem.objects.create(
                category=cat_req, texto=texto, es_critico=critico, orden=orden
            )

        # 4. CONDICIONES PARA REQUISITOS COMPLEMENTARIOS
        cat_comp = ChecklistCategory.objects.create(
            template=template, nombre='CONDICIONES PARA REQUISITOS COMPLEMENTARIOS', orden=4
        )
        items_comp = [
            ('Orden y Aseo (interior vehículo y pick up)', False, 1),
            ('Estado de carroceria, parachoques, portalón', False, 2),
            ('Gata y llave de rueda disponible', False, 3),
            ('Vidrios y parabrisas limpios', False, 4),
            ('Limpiaparabrisas funciona correctamente', False, 5),
            ('Radio Base funciona en todos los canales', False, 6),
        ]
        for texto, critico, orden in items_comp:
            ChecklistItem.objects.create(
                category=cat_comp, texto=texto, es_critico=critico, orden=orden
            )

        # 5. DOCUMENTACION
        cat_docs = ChecklistCategory.objects.create(
            template=template, nombre='DOCUMENTACION', orden=5
        )
        items_docs = [
            ('Permiso de Circulación', False, 1),
            ('Revisión Técnica', False, 2),
            ('Seguro Obligatorio', False, 3),
        ]
        for texto, critico, orden in items_docs:
            ChecklistItem.objects.create(
                category=cat_docs, texto=texto, es_critico=critico, orden=orden
            )

        self.stdout.write('✓ Template de Camionetas creado')

