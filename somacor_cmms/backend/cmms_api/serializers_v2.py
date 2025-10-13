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
    ChecklistItem, ChecklistInstance, ChecklistAnswer, EvidenciaOT
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
    tipo_equipo_nombre = serializers.CharField(source='idtipoequipo.nombretipo', read_only=True)
    estado_nombre = serializers.CharField(source='idestadoactual.nombreestado', read_only=True)
    faena_nombre = serializers.CharField(source='idfaenaactual.nombrefaena', read_only=True)
    
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
    
    def get_total_ordenes(self, obj):
        return OrdenesTrabajo.objects.filter(idequipo=obj).count()
    
    def get_ordenes_pendientes(self, obj):
        return OrdenesTrabajo.objects.filter(
            idequipo=obj,
            idestadoot__nombreestadoot__in=['Pendiente', 'En Proceso']
        ).count()
    
    def get_ultima_mantenimiento(self, obj):
        ultima_ot = OrdenesTrabajo.objects.filter(
            idequipo=obj,
            idestadoot__nombreestadoot='Completada'
        ).order_by('-fechacompletado').first()
        
        if ultima_ot:
            return ultima_ot.fechacompletado
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
    tipo_mantenimiento_nombre = serializers.CharField(source='idtipomantenimientoot.nombretipo', read_only=True)
    
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

class ChecklistTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChecklistTemplate
        fields = '__all__'

class ChecklistCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChecklistCategory
        fields = '__all__'

class ChecklistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChecklistItem
        fields = '__all__'

class ChecklistInstanceSerializer(serializers.ModelSerializer):
    orden_nombre = serializers.CharField(source='orden_trabajo.numeroot', read_only=True)
    tecnico_nombre = serializers.CharField(source='tecnico.user.get_full_name', read_only=True)
    
    class Meta:
        model = ChecklistInstance
        fields = '__all__'

class ChecklistAnswerSerializer(serializers.ModelSerializer):
    item_nombre = serializers.CharField(source='checklist_item.nombre', read_only=True)
    
    class Meta:
        model = ChecklistAnswer
        fields = '__all__'

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
            'numeroserie', 'aniofabricacion', 'tipoequipo', 'estadoactual',
            'faena', 'horometro', 'fechacreacion', 'observaciones',
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
            'codigointerno', 'nombreequipo', 'marca', 'modelo', 'numeroserie',
            'aniofabricacion', 'idtipoequipo', 'idestadoactual', 'idfaena',
            'horometro', 'observaciones'
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
