"""
Serializers V2 - Versión optimizada y moderna para CMMS
Adaptados al nuevo formato del backend y formularios
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Roles, Usuarios, TiposEquipo, Faenas, EstadosEquipo, Equipos,
    EstadosOrdenTrabajo, OrdenesTrabajo, ActividadesOrdenTrabajo,
    TiposMantenimientoOT, TiposTarea, TareasEstandar, PlanesMantenimiento,
    DetallesPlanMantenimiento, Agendas, ChecklistTemplate, ChecklistCategory,
    ChecklistItem, ChecklistInstance, ChecklistAnswer, ChecklistImage, EvidenciaOT,
    Especialidades, Tecnicos, CategoriasInventario, Proveedores, Inventario, MovimientosInventario
)
from datetime import datetime, date


# =============================================================================
# SERIALIZERS DE USUARIOS Y ROLES
# =============================================================================

class RolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields = '__all__'

class UsuariosSerializer(serializers.ModelSerializer):
    rol_nombre = serializers.CharField(source='idrol.nombrerol', read_only=True)
    usuario_nombre = serializers.CharField(source='user.get_full_name', read_only=True)
    usuario_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = Usuarios
        fields = '__all__'

# =============================================================================
# SERIALIZERS DE EQUIPOS
# =============================================================================

class TiposEquipoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TiposEquipo
        fields = '__all__'

class EstadosEquipoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadosEquipo
        fields = '__all__'

class FaenasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faenas
        fields = '__all__'

class EquiposSerializer(serializers.ModelSerializer):
    tipo_equipo_nombre = serializers.SerializerMethodField()
    estado_nombre = serializers.SerializerMethodField()
    faena_nombre = serializers.SerializerMethodField()
    
    # Campos calculados
    total_ordenes = serializers.SerializerMethodField()
    ordenes_pendientes = serializers.SerializerMethodField()
    ultima_mantenimiento = serializers.SerializerMethodField()
    
    class Meta:
        model = Equipos
        fields = [
            'idequipo', 'codigointerno', 'nombreequipo', 'marca', 'modelo', 
            'anio', 'patente', 'idtipoequipo', 'idfaenaactual', 'idestadoactual', 
            'activo', 'tipo_equipo_nombre', 'estado_nombre', 'faena_nombre',
            'total_ordenes', 'ordenes_pendientes', 'ultima_mantenimiento'
        ]
    
    def get_tipo_equipo_nombre(self, obj):
        return obj.idtipoequipo.nombretipo if obj.idtipoequipo else 'Sin categoría'
    
    def get_estado_nombre(self, obj):
        return obj.idestadoactual.nombreestado if obj.idestadoactual else 'Sin estado'
    
    def get_faena_nombre(self, obj):
        return obj.idfaenaactual.nombrefaena if obj.idfaenaactual else 'Sin ubicación'
    
    def get_total_ordenes(self, obj):
        try:
            return OrdenesTrabajo.objects.filter(idequipo=obj).count()
        except:
            return 0
    
    def get_ordenes_pendientes(self, obj):
        try:
            return OrdenesTrabajo.objects.filter(
                idequipo=obj,
                idestadoot__nombreestadoot__in=['Pendiente', 'En Proceso']
            ).count()
        except:
            return 0
    
    def get_ultima_mantenimiento(self, obj):
        try:
            ultima_ot = OrdenesTrabajo.objects.filter(
                idequipo=obj,
                idestadoot__nombreestadoot='Completada'
            ).order_by('-fechacompletado').first()
            
            if ultima_ot and ultima_ot.fechacompletado:
                return ultima_ot.fechacompletado
        except:
            pass
        return None

# =============================================================================
# SERIALIZERS DE ÓRDENES DE TRABAJO
# =============================================================================

class EstadosOrdenTrabajoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadosOrdenTrabajo
        fields = '__all__'

class TiposMantenimientoOTSerializer(serializers.ModelSerializer):
    class Meta:
        model = TiposMantenimientoOT
        fields = '__all__'

class OrdenesTrabajoSerializer(serializers.ModelSerializer):
    equipo_nombre = serializers.CharField(source='idequipo.nombreequipo', read_only=True)
    equipo_codigo = serializers.CharField(source='idequipo.codigointerno', read_only=True)
    solicitante_nombre = serializers.CharField(source='idsolicitante.get_full_name', read_only=True)
    tecnico_nombre = serializers.CharField(source='idtecnicoasignado.get_full_name', read_only=True)
    estado_nombre = serializers.CharField(source='idestadoot.nombreestadoot', read_only=True)
    tipo_mantenimiento_nombre = serializers.CharField(source='idtipomantenimientoot.nombretipomantenimientoot', read_only=True)
    
    # Campos calculados
    dias_transcurridos = serializers.SerializerMethodField()
    tiempo_transcurrido = serializers.SerializerMethodField()
    prioridad_nivel = serializers.SerializerMethodField()
    
    class Meta:
        model = OrdenesTrabajo
        fields = [
            'idordentrabajo', 'numeroot', 'descripcionproblemareportado', 'prioridad',
            'idequipo', 'idsolicitante', 'idtecnicoasignado', 'idestadoot', 
            'idtipomantenimientoot', 'fechareportefalla', 'fechaejecucion', 
            'fechacompletado', 'tiempototalminutos', 'observacionesfinales',
            'horometro', 'equipo_nombre', 'equipo_codigo', 'solicitante_nombre',
            'tecnico_nombre', 'estado_nombre', 'tipo_mantenimiento_nombre',
            'dias_transcurridos', 'tiempo_transcurrido', 'prioridad_nivel'
        ]
    
    def get_dias_transcurridos(self, obj):
        if obj.fechareportefalla:
            delta = datetime.now().date() - obj.fechareportefalla.date()
            return delta.days
        return 0
    
    def get_tiempo_transcurrido(self, obj):
        if obj.fechacompletado and obj.fechareportefalla:
            delta = obj.fechacompletado - obj.fechareportefalla
            return delta.total_seconds() / 3600  # horas
        return None
    
    def get_prioridad_nivel(self, obj):
        prioridades = {
            'Crítica': 4,
            'Alta': 3,
            'Media': 2,
            'Baja': 1
        }
        return prioridades.get(obj.prioridad, 0)

# =============================================================================
# SERIALIZERS DE ACTIVIDADES
# =============================================================================

class TareasEstandarSerializer(serializers.ModelSerializer):
    class Meta:
        model = TareasEstandar
        fields = '__all__'

class ActividadesOrdenTrabajoSerializer(serializers.ModelSerializer):
    tecnico_nombre = serializers.CharField(source='idtecnico.user.get_full_name', read_only=True)
    tarea_nombre = serializers.CharField(source='idtareaestandar.nombretarea', read_only=True)
    
    class Meta:
        model = ActividadesOrdenTrabajo
        fields = '__all__'

# =============================================================================
# SERIALIZERS DE PLANES DE MANTENIMIENTO
# =============================================================================

class PlanesMantenimientoSerializer(serializers.ModelSerializer):
    equipo_nombre = serializers.CharField(source='idequipo.nombreequipo', read_only=True)
    equipo_codigo = serializers.CharField(source='idequipo.codigointerno', read_only=True)
    
    class Meta:
        model = PlanesMantenimiento
        fields = '__all__'

class DetallesPlanMantenimientoSerializer(serializers.ModelSerializer):
    plan_nombre = serializers.CharField(source='idplan.nombreplan', read_only=True)
    tarea_nombre = serializers.CharField(source='idtarea.nombretarea', read_only=True)
    
    class Meta:
        model = DetallesPlanMantenimiento
        fields = '__all__'

# =============================================================================
# SERIALIZERS DE AGENDAS
# =============================================================================

class AgendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agendas
        fields = '__all__'

# =============================================================================
# SERIALIZERS DE CHECKLISTS
# =============================================================================

# --- SERIALIZERS PARA EL MÓDULO DE CHECKLISTS ---

class ChecklistItemSerializer(serializers.ModelSerializer):
    """ Serializer para un ítem individual del checklist. """
    class Meta:
        model = ChecklistItem
        fields = ['id_item', 'texto', 'es_critico', 'orden']

class ChecklistCategorySerializer(serializers.ModelSerializer):
    """ Serializer para una categoría, incluyendo sus ítems anidados. """
    items = ChecklistItemSerializer(many=True, read_only=True)
    class Meta:
        model = ChecklistCategory
        fields = ['id_category', 'nombre', 'orden', 'items']

class ChecklistTemplateSerializer(serializers.ModelSerializer):
    """
    Serializer para la plantilla de checklist. Se usa para leer la plantilla
    completa con todas sus categorías e ítems.
    """
    categories = ChecklistCategorySerializer(many=True, read_only=True)
    tipo_equipo_nombre = serializers.CharField(source='tipo_equipo.nombretipo', read_only=True)
    class Meta:
        model = ChecklistTemplate
        fields = ['id_template', 'nombre', 'tipo_equipo', 'tipo_equipo_nombre', 'activo', 'categories']

class ChecklistAnswerSerializer(serializers.ModelSerializer):
    """ Serializer para procesar las respuestas de un checklist. """
    item = serializers.IntegerField()
    class Meta:
        model = ChecklistAnswer
        fields = ['item', 'estado', 'observacion_item']

class ChecklistImageSerializer(serializers.ModelSerializer):
    """ Serializer para procesar las imágenes de un checklist. """
    usuario_subida_nombre = serializers.CharField(source='usuario_subida.get_full_name', read_only=True)
    
    class Meta:
        model = ChecklistImage
        fields = ['id_imagen', 'descripcion', 'imagen_base64', 'fecha_subida', 'usuario_subida_nombre']
        read_only_fields = ['id_imagen', 'fecha_subida', 'usuario_subida_nombre']

class ChecklistInstanceSerializer(serializers.ModelSerializer):
    """
    Serializer principal para crear y leer un checklist completado.
    Maneja la creación anidada de las respuestas y la subida de múltiples imágenes.
    """
    answers = ChecklistAnswerSerializer(many=True, write_only=True)
    imagenes = ChecklistImageSerializer(many=True, write_only=True, required=False)
    
    # Campos de solo lectura para visualizar la información relacionada
    operador_nombre = serializers.CharField(source='operador.get_full_name', read_only=True)
    equipo_nombre = serializers.CharField(source='equipo.nombreequipo', read_only=True)
    template_nombre = serializers.CharField(source='template.nombre', read_only=True)
    imagenes_list = ChecklistImageSerializer(source='imagenes', many=True, read_only=True)
    
    # Mantener compatibilidad con imagen_evidencia para casos legacy
    imagen_evidencia = serializers.CharField(allow_null=True, allow_blank=True, required=False)

    class Meta:
        model = ChecklistInstance
        fields = [
            'id_instance', 'template', 'equipo', 'fecha_inspeccion', 
            'horometro_inspeccion', 'lugar_inspeccion', 'observaciones_generales', 
            'fecha_creacion', 'answers', 'imagenes', 'operador_nombre', 'equipo_nombre', 
            'template_nombre', 'imagenes_list', 'imagen_evidencia'
        ]

    def create(self, validated_data):
        """
        Sobrescribe el método de creación para manejar la creación anidada de
        la instancia del checklist, sus respuestas y múltiples imágenes.
        """
        from django.db import transaction
        
        answers_data = validated_data.pop('answers')
        imagenes_data = validated_data.pop('imagenes', [])
        
        # Asignamos el usuario de la solicitud actual como el operador.
        user = self.context["request"].user
        if user and user.is_authenticated:
            validated_data["operador"] = user
        else:
            raise serializers.ValidationError("Usuario no autenticado para asignar como operador.")
        
        with transaction.atomic():
            instance = ChecklistInstance.objects.create(**validated_data)

            # Crear las respuestas del checklist
            for answer_data in answers_data:
                item_id = answer_data.pop('item')
                item = ChecklistItem.objects.get(id_item=item_id)
                ChecklistAnswer.objects.create(
                    instance=instance,
                    item=item,
                    **answer_data
                )

            # Crear las imágenes del checklist
            for imagen_data in imagenes_data:
                ChecklistImage.objects.create(
                    instance=instance,
                    usuario_subida=user,
                    **imagen_data
                )

            return instance

# =============================================================================
# SERIALIZERS DE EVIDENCIAS
# =============================================================================

class EvidenciaOTSerializer(serializers.ModelSerializer):
    orden_nombre = serializers.CharField(source='idordentrabajo.numeroot', read_only=True)
    tecnico_nombre = serializers.CharField(source='idtecnico.user.get_full_name', read_only=True)
    
    class Meta:
        model = EvidenciaOT
        fields = '__all__'
# =============================================================================

class RolSerializer(serializers.ModelSerializer):
    """Serializer para roles de usuario"""
    
    class Meta:
        model = Roles
        fields = ['idrol', 'nombrerol']
        read_only_fields = ['idrol']


class UserSerializer(serializers.ModelSerializer):
    """Serializer para usuarios del sistema"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer para usuarios CMMS con información extendida"""
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    rol_nombre = serializers.CharField(source='idrol.nombrerol', read_only=True)
    
    class Meta:
        model = Usuarios
        fields = ['user_id', 'user', 'idrol', 'rol_nombre', 'departamento']
        read_only_fields = []


# =============================================================================
# SERIALIZERS DE EQUIPOS
# =============================================================================

class TipoEquipoSerializer(serializers.ModelSerializer):
    """Serializer para tipos de equipo"""
    
    class Meta:
        model = TiposEquipo
        fields = ['idtipoequipo', 'nombretipo']
        read_only_fields = ['idtipoequipo']


class EstadoEquipoSerializer(serializers.ModelSerializer):
    """Serializer para estados de equipo"""
    
    class Meta:
        model = EstadosEquipo
        fields = ['idestadoequipo', 'nombreestado']
        read_only_fields = ['idestadoequipo']


class FaenaSerializer(serializers.ModelSerializer):
    """Serializer para faenas"""
    
    class Meta:
        model = Faenas
        fields = ['idfaena', 'nombrefaena', 'ubicacion', 'activa']
        read_only_fields = ['idfaena']


class EquipoSerializer(serializers.ModelSerializer):
    """Serializer para equipos con información relacionada"""
    tipo_nombre = serializers.CharField(source='idtipoequipo.nombretipo', read_only=True)
    estado_nombre = serializers.CharField(source='idestadoactual.nombreestado', read_only=True)
    faena_nombre = serializers.CharField(source='idfaena.nombrefaena', read_only=True)
    
    # Campos para escritura
    tipo_id = serializers.IntegerField(write_only=True, required=False)
    estado_id = serializers.IntegerField(write_only=True, required=False)
    faena_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Equipos
        fields = [
            'idequipo', 'codigointerno', 'nombreequipo', 'marca', 'modelo',
            'anio', 'patente', 'tipoequipo', 'estadoactual',
            'faena', 'activo',
            # Campos calculados
            'tipo_nombre', 'estado_nombre', 'faena_nombre',
            # Campos para escritura
            'tipo_id', 'estado_id', 'faena_id'
        ]
        read_only_fields = ['idequipo', 'fechacreacion']
    
    def create(self, validated_data):
        # Mapear campos de escritura a campos del modelo
        if 'tipo_id' in validated_data:
            validated_data['idtipoequipo_id'] = validated_data.pop('tipo_id')
        if 'estado_id' in validated_data:
            validated_data['idestadoactual_id'] = validated_data.pop('estado_id')
        if 'faena_id' in validated_data:
            validated_data['idfaena_id'] = validated_data.pop('faena_id')
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Mapear campos de escritura a campos del modelo
        if 'tipo_id' in validated_data:
            instance.idtipoequipo_id = validated_data.pop('tipo_id')
        if 'estado_id' in validated_data:
            instance.idestadoactual_id = validated_data.pop('estado_id')
        if 'faena_id' in validated_data:
            instance.idfaena_id = validated_data.pop('faena_id')
        
        return super().update(instance, validated_data)


# =============================================================================
# SERIALIZERS DE ÓRDENES DE TRABAJO
# =============================================================================

class EstadoOrdenTrabajoSerializer(serializers.ModelSerializer):
    """Serializer para estados de orden de trabajo"""
    
    class Meta:
        model = EstadosOrdenTrabajo
        fields = ['idestadoot', 'nombreestadoot']
        read_only_fields = ['idestadoot']


class TipoMantenimientoOTSerializer(serializers.ModelSerializer):
    """Serializer para tipos de mantenimiento de OT"""
    
    class Meta:
        model = TiposMantenimientoOT
        fields = ['idtipomantenimientoot', 'nombretipomantenimientoot']
        read_only_fields = ['idtipomantenimientoot']


class OrdenTrabajoSerializer(serializers.ModelSerializer):
    """Serializer para órdenes de trabajo con información relacionada"""
    estado_nombre = serializers.CharField(source='idestadoot.nombreestadoot', read_only=True)
    equipo_nombre = serializers.CharField(source='idequipo.nombreequipo', read_only=True)
    solicitante_nombre = serializers.CharField(source='idsolicitante.username', read_only=True)
    tecnico_nombre = serializers.CharField(source='idtecnicoasignado.username', read_only=True)
    tipo_mantenimiento_nombre = serializers.CharField(source='idtipomantenimientoot.nombretipomantenimientoot', read_only=True)
    
    # Campos para escritura
    estado_id = serializers.IntegerField(write_only=True, required=False)
    equipo_id = serializers.IntegerField(write_only=True, required=False)
    solicitante_id = serializers.IntegerField(write_only=True, required=False)
    tecnico_id = serializers.IntegerField(write_only=True, required=False)
    tipo_mantenimiento_id = serializers.IntegerField(write_only=True, required=False)
    
    # Campos calculados
    duracion_horas = serializers.SerializerMethodField()
    dias_abierta = serializers.SerializerMethodField()
    
    class Meta:
        model = OrdenesTrabajo
        fields = [
            'idordentrabajo', 'numeroot', 'descripcionproblemareportado',
            'prioridad', 'fechacreacionot', 'fechaejecucion', 'fechacompletado',
            'tiempototalminutos', 'observacionesfinales', 'horometro',
            'fechareportefalla', 'fechaejecucion', 'fechacompletado',
            # Campos relacionados (solo lectura)
            'estado_nombre', 'equipo_nombre', 'solicitante_nombre', 
            'tecnico_nombre', 'tipo_mantenimiento_nombre',
            # Campos para escritura
            'estado_id', 'equipo_id', 'solicitante_id', 'tecnico_id', 'tipo_mantenimiento_id',
            # Campos calculados
            'duracion_horas', 'dias_abierta'
        ]
        read_only_fields = ['idordentrabajo', 'fechacreacionot']
    
    def get_duracion_horas(self, obj):
        """Calcular duración en horas"""
        if obj.tiempototalminutos:
            return round(obj.tiempototalminutos / 60, 2)
        return None
    
    def get_dias_abierta(self, obj):
        """Calcular días que lleva abierta la orden"""
        if obj.fechacreacionot:
            delta = date.today() - obj.fechacreacionot.date()
            return delta.days
        return None
    
    def create(self, validated_data):
        # Mapear campos de escritura
        field_mapping = {
            'estado_id': 'idestadoot_id',
            'equipo_id': 'idequipo_id',
            'solicitante_id': 'idsolicitante_id',
            'tecnico_id': 'idtecnicoasignado_id',
            'tipo_mantenimiento_id': 'idtipomantenimientoot_id'
        }
        
        for write_field, model_field in field_mapping.items():
            if write_field in validated_data:
                validated_data[model_field] = validated_data.pop(write_field)
        
        return super().create(validated_data)


# =============================================================================
# SERIALIZERS DE MANTENIMIENTO PREVENTIVO
# =============================================================================

class TipoTareaSerializer(serializers.ModelSerializer):
    """Serializer para tipos de tarea"""
    
    class Meta:
        model = TiposTarea
        fields = ['idtipotarea', 'nombretipotarea']
        read_only_fields = ['idtipotarea']


class TareaEstandarSerializer(serializers.ModelSerializer):
    """Serializer para tareas estándar"""
    tipo_nombre = serializers.CharField(source='idtipotarea.nombretipotarea', read_only=True)
    
    class Meta:
        model = TareasEstandar
        fields = ['idtareaestandar', 'nombretarea', 'descripcion', 'tiempoestimadominutos', 'tipo_nombre']
        read_only_fields = ['idtareaestandar']


class PlanMantenimientoSerializer(serializers.ModelSerializer):
    """Serializer para planes de mantenimiento"""
    equipo_nombre = serializers.CharField(source='idequipo.nombreequipo', read_only=True)
    total_tareas = serializers.SerializerMethodField()
    
    class Meta:
        model = PlanesMantenimiento
        fields = [
            'idplanmantenimiento', 'nombreplan', 'descripcionplan', 'intervalohorometro',
            'intervalotiempo', 'equipo_nombre', 'total_tareas'
        ]
        read_only_fields = ['idplanmantenimiento']
    
    def get_total_tareas(self, obj):
        """Contar total de tareas en el plan"""
        return obj.detalles.count()


class DetallePlanSerializer(serializers.ModelSerializer):
    """Serializer para detalles de plan de mantenimiento"""
    tarea_nombre = serializers.CharField(source='idtareaestandar.nombretarea', read_only=True)
    
    class Meta:
        model = DetallesPlanMantenimiento
        fields = ['iddetalleplan', 'idtareaestandar', 'tarea_nombre', 'orden']
        read_only_fields = ['iddetalleplan']


# =============================================================================
# SERIALIZERS DE CHECKLIST
# =============================================================================

class ChecklistCategorySerializer(serializers.ModelSerializer):
    """Serializer para categorías de checklist"""
    
    class Meta:
        model = ChecklistCategory
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']


class ChecklistItemSerializer(serializers.ModelSerializer):
    """Serializer para items de checklist"""
    category_nombre = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = ChecklistItem
        fields = ['id', 'template', 'category', 'category_nombre', 'question', 'question_type', 'order']
        read_only_fields = ['id']


class ChecklistTemplateSerializer(serializers.ModelSerializer):
    """Serializer para templates de checklist"""
    equipo_nombre = serializers.CharField(source='equipment.nombreequipo', read_only=True)
    total_items = serializers.SerializerMethodField()
    
    class Meta:
        model = ChecklistTemplate
        fields = ['id', 'name', 'description', 'equipment', 'equipo_nombre', 'total_items', 'is_active']
        read_only_fields = ['id']
    
    def get_total_items(self, obj):
        """Contar total de items en el template"""
        return obj.items.count()


class ChecklistAnswerSerializer(serializers.ModelSerializer):
    """Serializer para respuestas de checklist"""
    item_pregunta = serializers.CharField(source='item.question', read_only=True)
    
    class Meta:
        model = ChecklistAnswer
        fields = ['id', 'instance', 'item', 'item_pregunta', 'answer', 'notes']
        read_only_fields = ['id']


class ChecklistInstanceSerializer(serializers.ModelSerializer):
    """Serializer para instancias de checklist"""
    template_nombre = serializers.CharField(source='template.name', read_only=True)
    equipo_nombre = serializers.CharField(source='template.equipment.nombreequipo', read_only=True)
    completado_por_nombre = serializers.CharField(source='completed_by.username', read_only=True)
    total_respuestas = serializers.SerializerMethodField()
    
    class Meta:
        model = ChecklistInstance
        fields = [
            'id', 'template', 'template_nombre', 'equipment', 'equipo_nombre',
            'completed_by', 'completado_por_nombre', 'completion_date', 'notes',
            'total_respuestas'
        ]
        read_only_fields = ['id', 'completion_date']
    
    def get_total_respuestas(self, obj):
        """Contar total de respuestas en la instancia"""
        return obj.answers.count()


# =============================================================================
# SERIALIZERS DE ACTIVIDADES
# =============================================================================

class ActividadOrdenTrabajoSerializer(serializers.ModelSerializer):
    """Serializer para actividades de orden de trabajo"""
    orden_numero = serializers.CharField(source='idordentrabajo.numeroot', read_only=True)
    tecnico_nombre = serializers.CharField(source='idtecnico.username', read_only=True)
    tarea_nombre = serializers.CharField(source='idtareaestandar.nombretarea', read_only=True)
    
    class Meta:
        model = ActividadesOrdenTrabajo
        fields = [
            'idactividad', 'idordentrabajo', 'orden_numero', 'idtareaestandar',
            'tarea_nombre', 'idtecnico', 'tecnico_nombre', 'fechainicio',
            'fechafin', 'tiemporealminutos', 'observaciones', 'estado'
        ]
        read_only_fields = ['idactividad']


# =============================================================================
# SERIALIZERS PARA DASHBOARD Y ESTADÍSTICAS
# =============================================================================

class DashboardStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas del dashboard"""
    equipos_total = serializers.IntegerField()
    equipos_activos = serializers.IntegerField()
    equipos_mantenimiento = serializers.IntegerField()
    ordenes_total = serializers.IntegerField()
    ordenes_pendientes = serializers.IntegerField()
    ordenes_en_proceso = serializers.IntegerField()
    ordenes_completadas = serializers.IntegerField()
    ordenes_recientes = OrdenTrabajoSerializer(many=True, read_only=True)
    equipos_criticos = EquipoSerializer(many=True, read_only=True)


class EquipoStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas de equipos"""
    total = serializers.IntegerField()
    activos = serializers.IntegerField()
    mantenimiento = serializers.IntegerField()
    disponibles = serializers.IntegerField()
    por_tipo = serializers.DictField()
    por_estado = serializers.DictField()


class OrdenStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas de órdenes"""
    total = serializers.IntegerField()
    pendientes = serializers.IntegerField()
    en_proceso = serializers.IntegerField()
    completadas = serializers.IntegerField()
    por_prioridad = serializers.DictField()
    por_tipo = serializers.DictField()


# =============================================================================
# SERIALIZERS PARA FORMULARIOS
# =============================================================================

class EquipoFormSerializer(serializers.ModelSerializer):
    """Serializer optimizado para formularios de equipos"""
    
    class Meta:
        model = Equipos
        fields = [
            'codigointerno', 'nombreequipo', 'marca', 'modelo', 'anio',
            'patente', 'idtipoequipo', 'idestadoactual', 'idfaenaactual',
            'activo'
        ]


class OrdenTrabajoFormSerializer(serializers.ModelSerializer):
    """Serializer optimizado para formularios de órdenes de trabajo"""
    
    class Meta:
        model = OrdenesTrabajo
        fields = [
            'numeroot', 'descripcionproblemareportado', 'prioridad',
            'idequipo', 'idsolicitante', 'idtecnicoasignado',
            'idestadoot', 'idtipomantenimientoot', 'observacionesfinales'
        ]


class ChecklistFormSerializer(serializers.ModelSerializer):
    """Serializer para completar checklist"""
    
    class Meta:
        model = ChecklistInstance
        fields = ['template', 'equipment', 'completed_by', 'notes']


# =============================================================================
# SERIALIZERS PARA BÚSQUEDAS Y FILTROS
# =============================================================================

class EquipoSearchSerializer(serializers.ModelSerializer):
    """Serializer para búsquedas de equipos"""
    tipo_nombre = serializers.CharField(source='idtipoequipo.nombretipo', read_only=True)
    estado_nombre = serializers.CharField(source='idestadoactual.nombreestado', read_only=True)
    
    class Meta:
        model = Equipos
        fields = ['idequipo', 'codigointerno', 'nombreequipo', 'tipo_nombre', 'estado_nombre']


class OrdenSearchSerializer(serializers.ModelSerializer):
    """Serializer para búsquedas de órdenes"""
    estado_nombre = serializers.CharField(source='idestadoot.nombreestadoot', read_only=True)
    equipo_nombre = serializers.CharField(source='idequipo.nombreequipo', read_only=True)
    
    class Meta:
        model = OrdenesTrabajo
        fields = [
            'idordentrabajo', 'numeroot', 'descripcionproblemareportado',
            'prioridad', 'estado_nombre', 'equipo_nombre', 'fechacreacionot'
        ]



# =============================================================================
# SERIALIZERS DE TÉCNICOS
# =============================================================================

class EspecialidadesSerializer(serializers.ModelSerializer):
    """Serializer para especialidades técnicas"""
    
    class Meta:
        model = Especialidades
        fields = '__all__'


class TecnicosListSerializer(serializers.ModelSerializer):
    """Serializer para listar técnicos con información básica"""
    nombre_completo = serializers.CharField(read_only=True)
    username = serializers.CharField(source='usuario.username', read_only=True)
    first_name = serializers.CharField(source='usuario.first_name', read_only=True)
    last_name = serializers.CharField(source='usuario.last_name', read_only=True)
    email_usuario = serializers.EmailField(source='usuario.email', read_only=True)
    especialidades_list = serializers.ListField(read_only=True)
    ordenes_activas = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Tecnicos
        fields = [
            'idtecnico', 'usuario', 'nombre_completo', 'username', 
            'first_name', 'last_name', 'telefono', 'email', 'email_usuario',
            'cargo', 'estado', 'activo', 'fecha_ingreso',
            'especialidades_list', 'ordenes_activas'
        ]
        read_only_fields = ['idtecnico', 'ordenes_activas']


class TecnicosDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para técnicos con toda la información"""
    nombre_completo = serializers.CharField(read_only=True)
    username = serializers.CharField(source='usuario.username', read_only=True)
    first_name = serializers.CharField(source='usuario.first_name', read_only=True)
    last_name = serializers.CharField(source='usuario.last_name', read_only=True)
    email_usuario = serializers.EmailField(source='usuario.email', read_only=True)
    especialidades_list = serializers.ListField(read_only=True)
    especialidades_detalle = EspecialidadesSerializer(source='especialidades', many=True, read_only=True)
    ordenes_activas = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Tecnicos
        fields = [
            'idtecnico', 'usuario', 'nombre_completo', 'username',
            'first_name', 'last_name', 'telefono', 'email', 'email_usuario',
            'cargo', 'estado', 'activo', 'fecha_ingreso',
            'especialidades', 'especialidades_list', 'especialidades_detalle',
            'ordenes_activas'
        ]
        read_only_fields = ['idtecnico', 'ordenes_activas']


class TecnicosCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear y actualizar técnicos"""
    
    class Meta:
        model = Tecnicos
        fields = [
            'idtecnico', 'usuario', 'especialidades', 'telefono', 
            'email', 'cargo', 'estado', 'activo', 'fecha_ingreso'
        ]
        read_only_fields = ['idtecnico']
    
    def validate_usuario(self, value):
        """Validar que el usuario no esté ya asignado a otro técnico"""
        if self.instance is None:  # Solo en creación
            if Tecnicos.objects.filter(usuario=value).exists():
                raise serializers.ValidationError("Este usuario ya está asignado como técnico.")
        return value



# =============================================================================
# SERIALIZERS DE INVENTARIO
# =============================================================================

class CategoriasInventarioSerializer(serializers.ModelSerializer):
    """Serializer para categorías de inventario"""
    
    class Meta:
        model = CategoriasInventario
        fields = '__all__'


class ProveedoresSerializer(serializers.ModelSerializer):
    """Serializer para proveedores"""
    
    class Meta:
        model = Proveedores
        fields = '__all__'


class InventarioListSerializer(serializers.ModelSerializer):
    """Serializer para listar items de inventario"""
    categoria_nombre = serializers.CharField(read_only=True)
    proveedor_nombre = serializers.CharField(read_only=True)
    estado_stock = serializers.CharField(read_only=True)
    valor_total = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    
    class Meta:
        model = Inventario
        fields = [
            'idinventario', 'codigointerno', 'codigobarras', 'nombreitem',
            'descripcion', 'idcategoria', 'categoria_nombre', 'idproveedor', 'proveedor_nombre',
            'cantidad', 'stockminimo', 'stockmaximo', 'unidadmedida', 'ubicacion',
            'costounitario', 'precioventa', 'estado', 'estado_stock', 'valor_total',
            'fechacreacion', 'fechaactualizacion'
        ]
        read_only_fields = ['idinventario', 'fechacreacion', 'fechaactualizacion']


class InventarioDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para items de inventario"""
    categoria_nombre = serializers.CharField(read_only=True)
    proveedor_nombre = serializers.CharField(read_only=True)
    estado_stock = serializers.CharField(read_only=True)
    valor_total = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    categoria_detalle = CategoriasInventarioSerializer(source='idcategoria', read_only=True)
    proveedor_detalle = ProveedoresSerializer(source='idproveedor', read_only=True)
    usuario_creacion_nombre = serializers.CharField(source='usuariocreacion.get_full_name', read_only=True)
    
    class Meta:
        model = Inventario
        fields = [
            'idinventario', 'codigointerno', 'codigobarras', 'nombreitem',
            'descripcion', 'idcategoria', 'categoria_nombre', 'categoria_detalle',
            'idproveedor', 'proveedor_nombre', 'proveedor_detalle',
            'cantidad', 'stockminimo', 'stockmaximo', 'unidadmedida', 'ubicacion',
            'costounitario', 'precioventa', 'estado', 'estado_stock', 'valor_total',
            'fechacreacion', 'fechaactualizacion', 'usuariocreacion', 'usuario_creacion_nombre'
        ]
        read_only_fields = ['idinventario', 'fechacreacion', 'fechaactualizacion']


class InventarioCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear y actualizar items de inventario"""
    
    class Meta:
        model = Inventario
        fields = [
            'codigointerno', 'codigobarras', 'nombreitem', 'descripcion',
            'idcategoria', 'idproveedor', 'cantidad', 'stockminimo', 'stockmaximo',
            'unidadmedida', 'ubicacion', 'costounitario', 'precioventa', 'estado'
        ]
    
    def validate_codigointerno(self, value):
        """Validar que el código interno sea único"""
        if self.instance is None:  # Solo en creación
            if Inventario.objects.filter(codigointerno=value).exists():
                raise serializers.ValidationError("Este código interno ya existe.")
        else:  # En actualización, excluir el item actual
            if Inventario.objects.filter(codigointerno=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("Este código interno ya existe.")
        return value
    
    def validate(self, data):
        """Validaciones adicionales"""
        # Validar que stock mínimo no sea mayor que stock máximo
        if data.get('stockmaximo') and data.get('stockminimo'):
            if data['stockminimo'] > data['stockmaximo']:
                raise serializers.ValidationError({
                    'stockminimo': 'El stock mínimo no puede ser mayor que el stock máximo.'
                })
        
        # Validar que la cantidad no sea negativa
        if data.get('cantidad', 0) < 0:
            raise serializers.ValidationError({
                'cantidad': 'La cantidad no puede ser negativa.'
            })
        
        return data


class MovimientosInventarioSerializer(serializers.ModelSerializer):
    """Serializer para movimientos de inventario"""
    item_nombre = serializers.CharField(source='idinventario.nombreitem', read_only=True)
    item_codigo = serializers.CharField(source='idinventario.codigointerno', read_only=True)
    usuario_nombre = serializers.CharField(source='usuariomovimiento.get_full_name', read_only=True)
    proveedor_nombre = serializers.CharField(source='idproveedor.nombreproveedor', read_only=True)
    orden_numero = serializers.CharField(source='idordentrabajo.numeroot', read_only=True)
    
    class Meta:
        model = MovimientosInventario
        fields = [
            'idmovimiento', 'idinventario', 'item_nombre', 'item_codigo',
            'tipomovimiento', 'cantidad', 'cantidadanterior', 'cantidadnueva',
            'motivo', 'observaciones', 'documento', 'idordentrabajo', 'orden_numero',
            'idproveedor', 'proveedor_nombre', 'fechamovimiento', 'usuariomovimiento', 'usuario_nombre'
        ]
        read_only_fields = ['idmovimiento', 'fechamovimiento']


class InventarioStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas de inventario"""
    total_items = serializers.IntegerField()
    items_activos = serializers.IntegerField()
    items_stock_bajo = serializers.IntegerField()
    items_sin_stock = serializers.IntegerField()
    valor_total_inventario = serializers.DecimalField(max_digits=15, decimal_places=2)
    categorias_count = serializers.IntegerField()
    proveedores_count = serializers.IntegerField()
