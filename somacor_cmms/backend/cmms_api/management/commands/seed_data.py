# cmms_api/management/commands/seed_data.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from cmms_api.models import (
    Roles, Usuarios, TiposEquipo, Faenas, EstadosEquipo, Equipos,
    TiposTarea, TareasEstandar, PlanesMantenimiento, DetallesPlanMantenimiento,
    TiposMantenimientoOT, EstadosOrdenTrabajo, ChecklistTemplate,
    ChecklistCategory, ChecklistItem
)

class Command(BaseCommand):
    help = 'Carga datos iniciales para el sistema CMMS'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando carga de datos iniciales...')

        # Crear roles
        self._crear_roles()
        
        # Crear tipos de equipo
        self._crear_tipos_equipo()
        
        # Crear faenas
        self._crear_faenas()
        
        # Crear estados de equipo
        self._crear_estados_equipo()
        
        # Crear tipos de tarea
        self._crear_tipos_tarea()
        
        # Crear tareas estándar
        self._crear_tareas_estandar()
        
        # Crear tipos de mantenimiento OT
        self._crear_tipos_mantenimiento_ot()
        
        # Crear estados de orden de trabajo
        self._crear_estados_orden_trabajo()
        
        # Crear equipos de ejemplo
        self._crear_equipos_ejemplo()
        
        # Crear planes de mantenimiento
        self._crear_planes_mantenimiento()
        
        # Crear plantillas de checklist
        self._crear_plantillas_checklist()

        self.stdout.write(
            self.style.SUCCESS('Datos iniciales cargados exitosamente.')
        )

    def _crear_roles(self):
        roles = [
            'Administrador',
            'Supervisor',
            'Técnico',
            'Operador',
            'Solicitante'
        ]
        
        for rol_nombre in roles:
            rol, created = Roles.objects.get_or_create(nombrerol=rol_nombre)
            if created:
                self.stdout.write(f'Rol creado: {rol_nombre}')

    def _crear_tipos_equipo(self):
        tipos = [
            'Minicargador',
            'Cargador Frontal',
            'Retroexcavadora',
            'Camioneta',
            'Camión Supersucker'
        ]
        
        for tipo_nombre in tipos:
            tipo, created = TiposEquipo.objects.get_or_create(nombretipo=tipo_nombre)
            if created:
                self.stdout.write(f'Tipo de equipo creado: {tipo_nombre}')

    def _crear_faenas(self):
        faenas = [
            ('Faena Norte', 'Sector Norte de la mina'),
            ('Faena Sur', 'Sector Sur de la mina'),
            ('Faena Central', 'Sector Central de la mina'),
            ('Taller Principal', 'Taller de mantenimiento principal')
        ]
        
        for nombre, ubicacion in faenas:
            faena, created = Faenas.objects.get_or_create(
                nombrefaena=nombre,
                defaults={'ubicacion': ubicacion}
            )
            if created:
                self.stdout.write(f'Faena creada: {nombre}')

    def _crear_estados_equipo(self):
        estados = [
            'Operativo',
            'En Mantenimiento',
            'Fuera de Servicio',
            'En Reparación',
            'Disponible'
        ]
        
        for estado_nombre in estados:
            estado, created = EstadosEquipo.objects.get_or_create(nombreestado=estado_nombre)
            if created:
                self.stdout.write(f'Estado de equipo creado: {estado_nombre}')

    def _crear_tipos_tarea(self):
        tipos = [
            ('Inspección', 'Tareas de inspección visual y técnica'),
            ('Lubricación', 'Tareas de lubricación y engrase'),
            ('Reemplazo', 'Reemplazo de componentes y partes'),
            ('Limpieza', 'Tareas de limpieza y aseo'),
            ('Calibración', 'Calibración de instrumentos y sistemas'),
            ('Reparación', 'Reparación de fallas y averías')
        ]
        
        for nombre, descripcion in tipos:
            tipo, created = TiposTarea.objects.get_or_create(
                nombretipotarea=nombre,
                defaults={'descripcion': descripcion}
            )
            if created:
                self.stdout.write(f'Tipo de tarea creado: {nombre}')

    def _crear_tareas_estandar(self):
        # Obtener tipos de tarea
        inspeccion = TiposTarea.objects.get(nombretipotarea='Inspección')
        lubricacion = TiposTarea.objects.get(nombretipotarea='Lubricación')
        reemplazo = TiposTarea.objects.get(nombretipotarea='Reemplazo')
        
        tareas = [
            ('Inspección nivel de aceite motor', 'Verificar nivel y estado del aceite del motor', inspeccion, 15),
            ('Inspección nivel de agua radiador', 'Verificar nivel de agua en el radiador', inspeccion, 10),
            ('Lubricación puntos de engrase', 'Aplicar grasa en puntos de lubricación', lubricacion, 30),
            ('Inspección sistema de frenos', 'Verificar funcionamiento del sistema de frenos', inspeccion, 20),
            ('Cambio de filtro de aceite', 'Reemplazar filtro de aceite del motor', reemplazo, 45),
            ('Cambio de aceite motor', 'Cambio completo de aceite del motor', reemplazo, 60),
            ('Inspección neumáticos', 'Verificar estado y presión de neumáticos', inspeccion, 15),
            ('Inspección sistema hidráulico', 'Verificar nivel y estado del fluido hidráulico', inspeccion, 20)
        ]
        
        for nombre, descripcion, tipo_tarea, tiempo in tareas:
            tarea, created = TareasEstandar.objects.get_or_create(
                nombretarea=nombre,
                defaults={
                    'descripciontarea': descripcion,
                    'idtipotarea': tipo_tarea,
                    'tiempoestimadominutos': tiempo
                }
            )
            if created:
                self.stdout.write(f'Tarea estándar creada: {nombre}')

    def _crear_tipos_mantenimiento_ot(self):
        tipos = [
            ('Preventivo', 'Mantenimiento planificado y programado'),
            ('Correctivo', 'Mantenimiento por falla o avería'),
            ('Predictivo', 'Mantenimiento basado en condición'),
            ('Mejorativo', 'Mantenimiento para mejora de equipos')
        ]
        
        for nombre, descripcion in tipos:
            tipo, created = TiposMantenimientoOT.objects.get_or_create(
                nombretipomantenimientoot=nombre,
                defaults={'descripcion': descripcion}
            )
            if created:
                self.stdout.write(f'Tipo de mantenimiento OT creado: {nombre}')

    def _crear_estados_orden_trabajo(self):
        estados = [
            ('Abierta', 'Orden de trabajo recién creada'),
            ('Asignada', 'Orden de trabajo asignada a técnico'),
            ('En Progreso', 'Orden de trabajo en ejecución'),
            ('Completada', 'Orden de trabajo finalizada'),
            ('Cancelada', 'Orden de trabajo cancelada'),
            ('Pendiente Aprobación', 'Orden de trabajo pendiente de aprobación')
        ]
        
        for nombre, descripcion in estados:
            estado, created = EstadosOrdenTrabajo.objects.get_or_create(
                nombreestadoot=nombre,
                defaults={'descripcion': descripcion}
            )
            if created:
                self.stdout.write(f'Estado de orden de trabajo creado: {nombre}')

    def _crear_equipos_ejemplo(self):
        # Obtener referencias necesarias
        tipo_minicargador = TiposEquipo.objects.get(nombretipo='Minicargador')
        tipo_camioneta = TiposEquipo.objects.get(nombretipo='Camioneta')
        faena_norte = Faenas.objects.get(nombrefaena='Faena Norte')
        estado_operativo = EstadosEquipo.objects.get(nombreestado='Operativo')
        
        equipos = [
            ('Minicargador CAT 236D', 'CAT-001', 'Caterpillar', '236D', 2020, 'MC-001', tipo_minicargador, 1250),
            ('Minicargador CAT 242D', 'CAT-002', 'Caterpillar', '242D', 2021, 'MC-002', tipo_minicargador, 890),
            ('Camioneta Toyota Hilux', 'TOY-001', 'Toyota', 'Hilux', 2019, 'BBXX-12', tipo_camioneta, 45000),
            ('Camioneta Ford Ranger', 'FOR-001', 'Ford', 'Ranger', 2020, 'CCYY-34', tipo_camioneta, 38000)
        ]
        
        for nombre, codigo, marca, modelo, anio, patente, tipo_equipo, horometro in equipos:
            equipo, created = Equipos.objects.get_or_create(
                codigointerno=codigo,
                defaults={
                    'nombreequipo': nombre,
                    'marca': marca,
                    'modelo': modelo,
                    'anio': anio,
                    'patente': patente,
                    'idtipoequipo': tipo_equipo,
                    'idfaenaactual': faena_norte,
                    'idestadoactual': estado_operativo,
                    'horometroactual': horometro
                }
            )
            if created:
                self.stdout.write(f'Equipo creado: {nombre}')

    def _crear_planes_mantenimiento(self):
        # Crear planes para minicargadores
        tipo_minicargador = TiposEquipo.objects.get(nombretipo='Minicargador')
        
        plan, created = PlanesMantenimiento.objects.get_or_create(
            nombreplan='Plan Mantenimiento Minicargador',
            defaults={
                'descripcionplan': 'Plan de mantenimiento preventivo para minicargadores',
                'idtipoequipo': tipo_minicargador
            }
        )
        
        if created:
            self.stdout.write('Plan de mantenimiento para minicargador creado')
            
            # Crear detalles del plan
            tareas_intervalos = [
                ('Inspección nivel de aceite motor', 250),
                ('Inspección nivel de agua radiador', 250),
                ('Lubricación puntos de engrase', 250),
                ('Inspección sistema de frenos', 500),
                ('Cambio de filtro de aceite', 500),
                ('Cambio de aceite motor', 1000),
                ('Inspección neumáticos', 250),
                ('Inspección sistema hidráulico', 500)
            ]
            
            for nombre_tarea, intervalo in tareas_intervalos:
                try:
                    tarea = TareasEstandar.objects.get(nombretarea=nombre_tarea)
                    detalle, created = DetallesPlanMantenimiento.objects.get_or_create(
                        idplanmantenimiento=plan,
                        idtareaestandar=tarea,
                        defaults={
                            'intervalohorasoperacion': intervalo,
                            'escritic': intervalo <= 250  # Tareas de 250h o menos son críticas
                        }
                    )
                    if created:
                        self.stdout.write(f'Detalle de plan creado: {nombre_tarea} cada {intervalo}h')
                except TareasEstandar.DoesNotExist:
                    self.stdout.write(f'Tarea no encontrada: {nombre_tarea}')

    def _crear_plantillas_checklist(self):
        # Crear plantilla para minicargador
        tipo_minicargador = TiposEquipo.objects.get(nombretipo='Minicargador')
        
        template, created = ChecklistTemplate.objects.get_or_create(
            nombre='Check List Minicargador (Diario)',
            defaults={'tipo_equipo': tipo_minicargador}
        )
        
        if created:
            self.stdout.write('Plantilla de checklist para minicargador creada')
            
            # Crear categorías y elementos basados en el PDF analizado
            categorias_items = [
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
                    ('Revisión de tres puntos de apoyo', False)
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
            
            for orden, (nombre_categoria, items) in enumerate(categorias_items, 1):
                categoria, created = ChecklistCategory.objects.get_or_create(
                    template=template,
                    nombre=nombre_categoria,
                    defaults={'orden': orden}
                )
                
                if created:
                    self.stdout.write(f'Categoría creada: {nombre_categoria}')
                
                for item_orden, (texto_item, es_critico) in enumerate(items, 1):
                    item, created = ChecklistItem.objects.get_or_create(
                        category=categoria,
                        texto=texto_item,
                        defaults={
                            'es_critico': es_critico,
                            'orden': item_orden
                        }
                    )
                    if created:
                        self.stdout.write(f'  Item creado: {texto_item} (Crítico: {es_critico})')

