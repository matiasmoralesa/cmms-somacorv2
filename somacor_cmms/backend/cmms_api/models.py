from django.db import models
from django.contrib.auth.models import User

# --- Modelos Anteriores (revisados y mantenidos para consistencia) ---
class Roles(models.Model):
    idrol = models.AutoField(db_column='IDRol', primary_key=True)
    nombrerol = models.CharField(db_column='NombreRol', unique=True, max_length=50)
    def __str__(self): return self.nombrerol
    class Meta: 
        db_table = 'roles'
        ordering = ['nombrerol']

class Usuarios(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, db_column='IDUsuario')
    idrol = models.ForeignKey(Roles, on_delete=models.PROTECT, db_column='IDRol')
    departamento = models.CharField(db_column='Departamento', max_length=100, blank=True, null=True)
    def __str__(self): return self.user.username
    class Meta: 
        db_table = 'usuarios'
        ordering = ['user__username']

class TiposEquipo(models.Model):
    idtipoequipo = models.AutoField(db_column='IDTipoEquipo', primary_key=True)
    nombretipo = models.CharField(db_column='NombreTipo', unique=True, max_length=100)
    def __str__(self): return self.nombretipo
    class Meta: 
        db_table = 'tiposequipo'
        ordering = ['nombretipo']

class Faenas(models.Model):
    idfaena = models.AutoField(db_column='IDFaena', primary_key=True)
    nombrefaena = models.CharField(db_column='NombreFaena', unique=True, max_length=100)
    ubicacion = models.CharField(db_column='Ubicacion', max_length=255, blank=True, null=True)
    direccion = models.CharField(db_column='Direccion', max_length=255, blank=True, null=True)
    ciudad = models.CharField(db_column='Ciudad', max_length=100, blank=True, null=True)
    region = models.CharField(db_column='Region', max_length=100, blank=True, null=True)
    contacto = models.CharField(db_column='Contacto', max_length=150, blank=True, null=True)
    telefono = models.CharField(db_column='Telefono', max_length=20, blank=True, null=True)
    email = models.EmailField(db_column='Email', max_length=100, blank=True, null=True)
    descripcion = models.TextField(db_column='Descripcion', blank=True, null=True)
    activa = models.BooleanField(db_column='Activa', default=True)
    fechacreacion = models.DateTimeField(db_column='FechaCreacion', auto_now_add=True, null=True)
    def __str__(self): return self.nombrefaena
    class Meta: 
        db_table = 'faenas'
        ordering = ['nombrefaena']

class EstadosEquipo(models.Model):
    idestadoequipo = models.AutoField(db_column='IDEstadoEquipo', primary_key=True)
    nombreestado = models.CharField(db_column='NombreEstado', unique=True, max_length=50)
    def __str__(self): return self.nombreestado
    class Meta: 
        db_table = 'estadosequipo'
        ordering = ['nombreestado']
    
class Equipos(models.Model):
    idequipo = models.AutoField(db_column='IDEquipo', primary_key=True)
    codigointerno = models.CharField(db_column='CodigoInterno', unique=True, max_length=50, blank=True, null=True)
    nombreequipo = models.CharField(db_column='NombreEquipo', max_length=150)
    marca = models.CharField(db_column='Marca', max_length=100, blank=True, null=True)
    modelo = models.CharField(db_column='Modelo', max_length=100, blank=True, null=True)
    anio = models.IntegerField(db_column='Anio', blank=True, null=True)
    patente = models.CharField(db_column='Patente', max_length=20, blank=True, null=True)
    idtipoequipo = models.ForeignKey(TiposEquipo, on_delete=models.PROTECT, db_column='IDTipoEquipo')
    idfaenaactual = models.ForeignKey(Faenas, on_delete=models.SET_NULL, db_column='IDFaenaActual', blank=True, null=True)
    idestadoactual = models.ForeignKey(EstadosEquipo, on_delete=models.PROTECT, db_column='IDEstadoActual')
    activo = models.BooleanField(db_column='Activo', default=True)
    
    @property
    def ordenes_pendientes_count(self):
        """Cantidad de órdenes pendientes"""
        return self.ordenestrabajo_set.filter(
            idestadoot__nombreestadoot__in=['Abierta', 'En Progreso', 'Asignada']
        ).count()
    
    @property
    def ultimo_mantenimiento(self):
        """Fecha del último mantenimiento completado"""
        ultima_orden = self.ordenestrabajo_set.filter(
            idestadoot__nombreestadoot='Completada'
        ).order_by('-fechacompletado').first()
        return ultima_orden.fechacompletado if ultima_orden else None
    
    @property
    def dias_sin_mantenimiento(self):
        """Días desde el último mantenimiento"""
        from django.utils import timezone
        ultimo = self.ultimo_mantenimiento
        if ultimo:
            return (timezone.now() - ultimo).days
        return None
    
    @property
    def requiere_atencion(self):
        """Determina si el equipo requiere atención urgente"""
        if not self.activo:
            return False
        if self.idestadoactual and 'mantenimiento' in self.idestadoactual.nombreestado.lower():
            return True
        if self.ordenes_pendientes_count > 2:
            return True
        return False
    
    def __str__(self): 
        return f"{self.nombreequipo} ({self.patente or self.codigointerno or 'S/N'})"
    
    class Meta: 
        db_table = 'equipos'
        ordering = ['nombreequipo']
        indexes = [
            models.Index(fields=['activo'], name='idx_equipos_activo'),
            models.Index(fields=['idestadoactual'], name='idx_equipos_estado'),
        ]

# --- NUEVOS MODELOS PARA EL MÓDULO DE CHECKLISTS ---

class ChecklistTemplate(models.Model):
    """
    Representa la plantilla maestra de un checklist.
    Ej: "Check List Minicargador", "Check List Camionetas".
    """
    id_template = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200, unique=True)
    tipo_equipo = models.ForeignKey(TiposEquipo, on_delete=models.CASCADE, help_text="Tipo de equipo al que aplica este checklist.")
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
    
    class Meta:
        ordering = ['nombre']

class ChecklistCategory(models.Model):
    """
    Representa una categoría dentro de un checklist.
    Ej: "1. MOTOR", "2. LUCES", "3. DOCUMENTOS".
    """
    id_category = models.AutoField(primary_key=True)
    template = models.ForeignKey(ChecklistTemplate, on_delete=models.CASCADE, related_name='categories')
    nombre = models.CharField(max_length=100)
    orden = models.IntegerField(default=1) # Para ordenar las categorías en el formulario.

    class Meta:
        ordering = ['orden']
    def __str__(self):
        return f"{self.orden}. {self.nombre}"

class ChecklistItem(models.Model):
    """
    Representa un ítem individual a ser chequeado.
    Ej: "1.1 Nivel de Agua", "2.1 Luces Altas".
    """
    id_item = models.AutoField(primary_key=True)
    category = models.ForeignKey(ChecklistCategory, on_delete=models.CASCADE, related_name='items')
    texto = models.CharField(max_length=255)
    es_critico = models.BooleanField(default=False, help_text="Marcar si una falla en este ítem impide la operación del equipo.")
    orden = models.IntegerField(default=1)

    class Meta:
        ordering = ['orden']
    def __str__(self):
        return self.texto

class ChecklistInstance(models.Model):
    """
    Representa un checklist que ha sido completado por un operador.
    Contiene la información del encabezado del informe.
    """
    id_instance = models.AutoField(primary_key=True)
    template = models.ForeignKey(ChecklistTemplate, on_delete=models.PROTECT)
    equipo = models.ForeignKey(Equipos, on_delete=models.PROTECT)
    operador = models.ForeignKey(User, on_delete=models.PROTECT)
    fecha_inspeccion = models.DateField()
    horometro_inspeccion = models.IntegerField()
    lugar_inspeccion = models.CharField(max_length=200, blank=True, null=True)
    observaciones_generales = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    imagen_evidencia = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Checklist para {self.equipo.nombreequipo} - {self.fecha_inspeccion}"
    
    class Meta:
        ordering = ['-fecha_inspeccion']

class ChecklistAnswer(models.Model):
    """
    Almacena la respuesta (Bueno, Malo, N/A) para un ítem específico
    de un checklist completado.
    """
    ESTADO_CHOICES = [
        ('bueno', 'Bueno'),
        ('malo', 'Malo'),
        ('na', 'No Aplica'),
    ]
    id_answer = models.AutoField(primary_key=True)
    instance = models.ForeignKey(ChecklistInstance, on_delete=models.CASCADE, related_name='answers')
    item = models.ForeignKey(ChecklistItem, on_delete=models.PROTECT)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES)
    observacion_item = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ('instance', 'item')
        ordering = ['item__orden']

# --- NUEVOS MODELOS PARA AGENDA DE MANTENIMIENTO PREVENTIVO ---

class TiposTarea(models.Model):
    """
    Tipos de tareas de mantenimiento (Inspección, Lubricación, Reemplazo, etc.)
    """
    idtipotarea = models.AutoField(db_column='IDTipoTarea', primary_key=True)
    nombretipotarea = models.CharField(db_column='NombreTipoTarea', unique=True, max_length=100)
    descripcion = models.TextField(db_column='Descripcion', blank=True, null=True)
    def __str__(self): return self.nombretipotarea
    class Meta: 
        db_table = 'tipostarea'
        ordering = ['nombretipotarea']

class TareasEstandar(models.Model):
    """
    Tareas estándar que se pueden asignar a planes de mantenimiento
    """
    idtareaestandar = models.AutoField(db_column='IDTareaEstandar', primary_key=True)
    nombretarea = models.CharField(db_column='NombreTarea', max_length=255)
    descripciontarea = models.TextField(db_column='DescripcionTarea', blank=True, null=True)
    idtipotarea = models.ForeignKey(TiposTarea, on_delete=models.PROTECT, db_column='IDTipoTarea')
    tiempoestimadominutos = models.IntegerField(db_column='TiempoEstimadoMinutos', default=0)
    activa = models.BooleanField(db_column='Activa', default=True)
    def __str__(self): return self.nombretarea
    class Meta: 
        db_table = 'tareasestandar'
        ordering = ['nombretarea']

class PlanesMantenimiento(models.Model):
    """
    Planes de mantenimiento preventivo por tipo de equipo
    """
    idplanmantenimiento = models.AutoField(db_column='IDPlanMantenimiento', primary_key=True)
    nombreplan = models.CharField(db_column='NombrePlan', max_length=255)
    descripcionplan = models.TextField(db_column='DescripcionPlan', blank=True, null=True)
    idtipoequipo = models.ForeignKey(TiposEquipo, on_delete=models.PROTECT, db_column='IDTipoEquipo')
    activo = models.BooleanField(db_column='Activo', default=True)
    fechacreacion = models.DateTimeField(db_column='FechaCreacion', auto_now_add=True)
    def __str__(self): return self.nombreplan
    class Meta: 
        db_table = 'planesmantenimiento'
        ordering = ['nombreplan']

class DetallesPlanMantenimiento(models.Model):
    """
    Detalles de las tareas incluidas en un plan de mantenimiento con sus intervalos
    """
    iddetalleplan = models.AutoField(db_column='IDDetallePlan', primary_key=True)
    idplanmantenimiento = models.ForeignKey(PlanesMantenimiento, on_delete=models.CASCADE, db_column='IDPlanMantenimiento')
    idtareaestandar = models.ForeignKey(TareasEstandar, on_delete=models.PROTECT, db_column='IDTareaEstandar')
    intervalohorasoperacion = models.IntegerField(db_column='IntervaloHorasOperacion', help_text="Cada cuántas horas se debe realizar esta tarea")
    escritic = models.BooleanField(db_column='EsCritica', default=False)
    activo = models.BooleanField(db_column='Activo', default=True)
    def __str__(self): return f"{self.idplanmantenimiento.nombreplan} - {self.idtareaestandar.nombretarea} ({self.intervalohorasoperacion}h)"
    class Meta: 
        db_table = 'detallesplanmantenimiento'
        ordering = ['intervalohorasoperacion']

class TiposMantenimientoOT(models.Model):
    """
    Tipos de mantenimiento para órdenes de trabajo (Preventivo, Correctivo, Predictivo)
    """
    idtipomantenimientoot = models.AutoField(db_column='IDTipoMantenimientoOT', primary_key=True)
    nombretipomantenimientoot = models.CharField(db_column='NombreTipoMantenimientoOT', unique=True, max_length=100)
    descripcion = models.TextField(db_column='Descripcion', blank=True, null=True)
    def __str__(self): return self.nombretipomantenimientoot
    class Meta: 
        db_table = 'tiposmantenimientoot'
        ordering = ['nombretipomantenimientoot']

class EstadosOrdenTrabajo(models.Model):
    """
    Estados de las órdenes de trabajo (Abierta, En Progreso, Completada, Cancelada)
    """
    idestadoot = models.AutoField(db_column='IDEstadoOT', primary_key=True)
    nombreestadoot = models.CharField(db_column='NombreEstadoOT', unique=True, max_length=50)
    descripcion = models.TextField(db_column='Descripcion', blank=True, null=True)
    def __str__(self): return self.nombreestadoot
    class Meta: 
        db_table = 'estadosordentrabajo'
        ordering = ['nombreestadoot']

# --- NUEVOS MODELOS PARA REGISTRO DE MANTENIMIENTOS ---

class OrdenesTrabajo(models.Model):
    """
    Órdenes de trabajo de mantenimiento
    """
    idordentrabajo = models.AutoField(db_column='IDOrdenTrabajo', primary_key=True)
    numeroot = models.CharField(db_column='NumeroOT', unique=True, max_length=50)
    idequipo = models.ForeignKey(Equipos, on_delete=models.PROTECT, db_column='IDEquipo')
    idplanorigen = models.ForeignKey(PlanesMantenimiento, on_delete=models.SET_NULL, db_column='IDPlanOrigen', blank=True, null=True)
    idtipomantenimientoot = models.ForeignKey(TiposMantenimientoOT, on_delete=models.PROTECT, db_column='IDTipoMantenimientoOT')
    idestadoot = models.ForeignKey(EstadosOrdenTrabajo, on_delete=models.PROTECT, db_column='IDEstadoOT')
    
    # Información de programación
    fechacreacionot = models.DateTimeField(db_column='FechaCreacionOT', auto_now_add=True)
    fechaemision = models.DateField(db_column='FechaEmision', blank=True, null=True)
    fechaejecucion = models.DateField(db_column='FechaEjecucion', blank=True, null=True)
    fechacompletado = models.DateTimeField(db_column='FechaCompletado', blank=True, null=True)
    
    # Información de personal
    idsolicitante = models.ForeignKey(User, on_delete=models.PROTECT, db_column='IDSolicitante', related_name='ots_solicitadas')
    idtecnicoasignado = models.ForeignKey(User, on_delete=models.SET_NULL, db_column='IDTecnicoAsignado', related_name='ots_asignadas', blank=True, null=True)
    
    # Información de mantenimiento
    horometro = models.IntegerField(db_column='Horometro', blank=True, null=True)
    prioridad = models.CharField(db_column='Prioridad', max_length=20, choices=[('Baja', 'Baja'), ('Media', 'Media'), ('Alta', 'Alta'), ('Crítica', 'Crítica')], default='Media')
    
    # Información de fallas (para mantenimiento correctivo)
    descripcionproblemareportado = models.TextField(db_column='DescripcionProblemaReportado', blank=True, null=True)
    fechareportefalla = models.DateTimeField(db_column='FechaReporteFalla', blank=True, null=True)
    
    # Información de cierre
    observacionesfinales = models.TextField(db_column='ObservacionesFinales', blank=True, null=True)
    tiempototalminutos = models.IntegerField(db_column='TiempoTotalMinutos', blank=True, null=True)
    
    @property
    def dias_transcurridos(self):
        """Días desde la creación de la OT"""
        from django.utils import timezone
        if self.fechacreacionot:
            return (timezone.now() - self.fechacreacionot).days
        return None
    
    @property
    def esta_vencida(self):
        """Determina si la OT está vencida (>7 días sin completar)"""
        from django.utils import timezone
        if self.fechacompletado:
            return False
        if self.fechacreacionot:
            dias = (timezone.now() - self.fechacreacionot).days
            return dias > 7
        return False
    
    @property
    def tiempo_resolucion_horas(self):
        """Tiempo de resolución en horas"""
        if self.tiempototalminutos:
            return round(self.tiempototalminutos / 60, 1)
        return None
    
    def __str__(self): 
        return f"{self.numeroot} - {self.idequipo.nombreequipo if self.idequipo else 'Sin equipo'}"
    
    class Meta: 
        db_table = 'ordenestrabajo'
        ordering = ['-fechacreacionot']
        indexes = [
            models.Index(fields=['fechareportefalla'], name='idx_ot_fecha_reporte'),
            models.Index(fields=['fechacreacionot'], name='idx_ot_fecha_creacion'),
            models.Index(fields=['idestadoot', 'fechacreacionot'], name='idx_ot_estado_fecha'),
            models.Index(fields=['idequipo', 'idestadoot'], name='idx_ot_equipo_estado'),
            models.Index(fields=['prioridad', 'fechacreacionot'], name='idx_ot_prioridad_fecha'),
        ]

class ActividadesOrdenTrabajo(models.Model):
    """
    Actividades específicas dentro de una orden de trabajo
    """
    idactividadot = models.AutoField(db_column='IDActividadOT', primary_key=True)
    idordentrabajo = models.ForeignKey(OrdenesTrabajo, on_delete=models.CASCADE, db_column='IDOrdenTrabajo')
    idtareaestandar = models.ForeignKey(TareasEstandar, on_delete=models.PROTECT, db_column='IDTareaEstandar', blank=True, null=True)
    secuencia = models.IntegerField(db_column='Secuencia', blank=True, null=True)
    descripcionactividad = models.TextField(db_column='DescripcionActividad')
    
    # Información de ejecución
    fechainicioactividad = models.DateTimeField(db_column='FechaInicioActividad', blank=True, null=True)
    fechafinactividad = models.DateTimeField(db_column='FechaFinActividad', blank=True, null=True)
    tiempoestimadominutos = models.IntegerField(db_column='TiempoEstimadoMinutos', blank=True, null=True)
    tiemporealminutos = models.IntegerField(db_column='TiempoRealMinutos', blank=True, null=True)
    
    # Información de resultados
    observacionesactividad = models.TextField(db_column='ObservacionesActividad', blank=True, null=True)
    completada = models.BooleanField(db_column='Completada', default=False)
    resultadoinspeccion = models.CharField(db_column='ResultadoInspeccion', max_length=50, blank=True, null=True)
    medicionvalor = models.DecimalField(db_column='MedicionValor', max_digits=10, decimal_places=2, blank=True, null=True)
    unidadmedicion = models.CharField(db_column='UnidadMedicion', max_length=20, blank=True, null=True)
    
    # Personal ejecutor
    idtecnicoejecutor = models.ForeignKey(User, on_delete=models.SET_NULL, db_column='IDTecnicoEjecutor', blank=True, null=True)
    
    def __str__(self): return f"{self.idordentrabajo.numeroot} - {self.descripcionactividad[:50]}"
    class Meta: 
        db_table = 'actividadesordentrabajo'
        ordering = ['secuencia']

class Agendas(models.Model):
    """
    Agenda de eventos y mantenimientos programados
    """
    idagenda = models.AutoField(db_column='IDAgenda', primary_key=True)
    tituloevento = models.CharField(db_column='TituloEvento', max_length=255)
    fechahorainicio = models.DateTimeField(db_column='FechaHoraInicio')
    fechahorafin = models.DateTimeField(db_column='FechaHoraFin')
    descripcionevento = models.TextField(db_column='DescripcionEvento', blank=True, null=True)
    tipoevento = models.CharField(db_column='TipoEvento', max_length=50, blank=True, null=True)
    colorevento = models.CharField(db_column='ColorEvento', max_length=7, blank=True, null=True)
    esdiacompleto = models.BooleanField(db_column='EsDiaCompleto', default=False)
    recursivo = models.BooleanField(db_column='Recursivo', default=False)
    reglarecursividad = models.CharField(db_column='ReglaRecursividad', max_length=255, blank=True, null=True)
    fechacreacionevento = models.DateTimeField(db_column='FechaCreacionEvento', auto_now_add=True)
    
    # Relaciones
    idequipo = models.ForeignKey(Equipos, on_delete=models.CASCADE, db_column='IDEquipo', blank=True, null=True)
    idordentrabajo = models.ForeignKey(OrdenesTrabajo, on_delete=models.CASCADE, db_column='IDOrdenTrabajo', blank=True, null=True)
    idplanmantenimiento = models.ForeignKey(PlanesMantenimiento, on_delete=models.CASCADE, db_column='IDPlanMantenimiento', blank=True, null=True)
    idusuarioasignado = models.ForeignKey(User, on_delete=models.SET_NULL, db_column='IDUsuarioAsignado', related_name='eventos_asignados', blank=True, null=True)
    idusuariocreador = models.ForeignKey(User, on_delete=models.PROTECT, db_column='IDUsuarioCreador', related_name='eventos_creados')
    
    def __str__(self): return f"{self.tituloevento} - {self.fechahorainicio.strftime('%Y-%m-%d %H:%M')}"
    class Meta: 
        db_table = 'agendas'
        ordering = ['fechahorainicio']


# --- MODELO PARA EVIDENCIAS FOTOGRÁFICAS EN ÓRDENES DE TRABAJO ---

class EvidenciaOT(models.Model):
    """
    Evidencias fotográficas asociadas a órdenes de trabajo
    """
    idevidencia = models.AutoField(db_column='IDEvidencia', primary_key=True)
    idordentrabajo = models.ForeignKey(OrdenesTrabajo, on_delete=models.CASCADE, db_column='IDOrdenTrabajo', related_name='evidencias')
    descripcion = models.CharField(db_column='Descripcion', max_length=255, blank=True, null=True)
    imagen_base64 = models.TextField(db_column='ImagenBase64', help_text="Imagen almacenada en formato Base64")
    fecha_subida = models.DateTimeField(db_column='FechaSubida', auto_now_add=True)
    usuario_subida = models.ForeignKey(User, on_delete=models.PROTECT, db_column='UsuarioSubida', null=True, blank=True)
    
    def __str__(self):
        return f"Evidencia {self.idevidencia} - OT {self.idordentrabajo.numeroot}"
    
    class Meta:
        db_table = 'evidenciaot'
        ordering = ['-fecha_subida']


# --- MODELO PARA MÚLTIPLES IMÁGENES EN CHECKLISTS ---

class ChecklistImage(models.Model):
    """
    Evidencias fotográficas asociadas a checklists completados
    """
    id_imagen = models.AutoField(primary_key=True)
    instance = models.ForeignKey(ChecklistInstance, on_delete=models.CASCADE, related_name='imagenes')
    descripcion = models.CharField(max_length=255, blank=True, null=True, help_text="Descripción opcional de la imagen")
    imagen_base64 = models.TextField(help_text="Imagen almacenada en formato Base64")
    fecha_subida = models.DateTimeField(auto_now_add=True)
    usuario_subida = models.ForeignKey(User, on_delete=models.PROTECT)
    
    def __str__(self):
        return f"Imagen {self.id_imagen} - Checklist {self.instance.id_instance}"
    
    class Meta:
        db_table = 'checklistimage'
        ordering = ['-fecha_subida']


