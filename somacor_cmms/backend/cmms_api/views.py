# cmms_api/views.py

from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models, transaction
import uuid
import random
from .models import *
from .serializers import *
from .permissions import IsAdminRole, IsSupervisorRole, IsOperadorRole, IsAdminOrSupervisorRole, IsAnyRole

# --- Funciones Auxiliares ---
def generar_numero_ot_unico(equipo, tipo_mantenimiento='CORR'):
    """
    Genera un número de OT único para evitar conflictos de constraint UNIQUE
    """
    max_intentos = 10
    for intento in range(max_intentos):
        # Generar timestamp con microsegundos para mayor unicidad
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        
        # Agregar componente aleatorio para evitar colisiones
        componente_aleatorio = random.randint(100, 999)
        
        # Generar número de OT
        numero_ot = f"OT-{tipo_mantenimiento}-{equipo.codigointerno or equipo.idequipo}-{timestamp}-{componente_aleatorio}"
        
        # Verificar si ya existe
        if not OrdenesTrabajo.objects.filter(numeroot=numero_ot).exists():
            return numero_ot
    
    # Si después de 10 intentos no se puede generar un número único, usar UUID
    uuid_suffix = str(uuid.uuid4())[:8].upper()
    return f"OT-{tipo_mantenimiento}-{equipo.codigointerno or equipo.idequipo}-{timezone.now().strftime('%Y%m%d%H%M%S')}-{uuid_suffix}"

# --- Vistas de Autenticación ---
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Obtener información del usuario y su rol
        user_data = UserSerializer(user, context={'request': request}).data
        
        # Obtener información adicional del rol
        try:
            usuario_info = Usuarios.objects.get(user=user)
            rol_info = {
                'id': usuario_info.idrol.idrol,
                'nombre': usuario_info.idrol.nombrerol,
                'departamento': usuario_info.departamento
            }
        except Usuarios.DoesNotExist:
            rol_info = {
                'id': None,
                'nombre': 'Sin rol asignado',
                'departamento': ''
            }
        
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user': user_data,
            'rol': rol_info,
            'message': 'Login exitoso'
        })

class LogoutView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        if request.user and request.user.is_authenticated:
            request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# --- ViewSets de Catálogos ---
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [IsAdminRole]  # Solo Admin puede gestionar usuarios

class RolViewSet(viewsets.ModelViewSet):
    queryset = Roles.objects.all()
    serializer_class = RolSerializer
    permission_classes = [IsAdminRole]  # Solo Admin puede gestionar roles

class FaenaViewSet(viewsets.ModelViewSet):
    queryset = Faenas.objects.all()
    serializer_class = FaenaSerializer
    permission_classes = [IsAnyRole]  # Todos los roles pueden ver faenas

class TipoEquipoViewSet(viewsets.ModelViewSet):
    queryset = TiposEquipo.objects.all()
    serializer_class = TipoEquipoSerializer
    permission_classes = [IsAnyRole]  # Todos los roles pueden ver tipos de equipo

class EstadoEquipoViewSet(viewsets.ModelViewSet):
    queryset = EstadosEquipo.objects.all()
    serializer_class = EstadoEquipoSerializer
    permission_classes = [IsAnyRole]  # Todos los roles pueden ver estados de equipo

class EquipoViewSet(viewsets.ModelViewSet):
    queryset = Equipos.objects.all()
    serializer_class = EquipoSerializer
    permission_classes = [IsAnyRole]  # Todos los roles pueden ver equipos

# --- NUEVOS VIEWSETS PARA EL MÓDULO DE CHECKLISTS ---

class ChecklistTemplateViewSet(viewsets.ModelViewSet):
    queryset = ChecklistTemplate.objects.all()
    serializer_class = ChecklistTemplateSerializer
    permission_classes = [permissions.AllowAny]

class ChecklistCategoryViewSet(viewsets.ModelViewSet):
    queryset = ChecklistCategory.objects.all()
    serializer_class = ChecklistCategorySerializer
    permission_classes = [permissions.AllowAny]

class ChecklistItemViewSet(viewsets.ModelViewSet):
    queryset = ChecklistItem.objects.all()
    serializer_class = ChecklistItemSerializer
    permission_classes = [permissions.AllowAny]

class ChecklistInstanceViewSet(viewsets.ModelViewSet):
    queryset = ChecklistInstance.objects.all()
    serializer_class = ChecklistInstanceSerializer
    permission_classes = [permissions.AllowAny]

class ChecklistAnswerViewSet(viewsets.ModelViewSet):
    queryset = ChecklistAnswer.objects.all()
    serializer_class = ChecklistAnswerSerializer
    permission_classes = [permissions.AllowAny]

# --- NUEVOS VIEWSETS PARA AGENDA DE MANTENIMIENTO PREVENTIVO ---

class TipoTareaViewSet(viewsets.ModelViewSet):
    queryset = TiposTarea.objects.all()
    serializer_class = TipoTareaSerializer
    permission_classes = [permissions.AllowAny]

class TareaEstandarViewSet(viewsets.ModelViewSet):
    queryset = TareasEstandar.objects.all()
    serializer_class = TareaEstandarSerializer
    permission_classes = [permissions.AllowAny]

class PlanMantenimientoViewSet(viewsets.ModelViewSet):
    queryset = PlanesMantenimiento.objects.all()
    serializer_class = PlanMantenimientoSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=True, methods=['get', 'post'], url_path='generar-agenda')
    def generar_agenda(self, request, pk=None):
        """
        Genera eventos de agenda basados en el plan de mantenimiento y los equipos asociados
        """
        plan = self.get_object()
        equipos = Equipos.objects.filter(idtipoequipo=plan.idtipoequipo, activo=True)
        
        eventos_creados = []
        for equipo in equipos:
            detalles = DetallesPlanMantenimiento.objects.filter(
                idplanmantenimiento=plan, 
                activo=True
            ).select_related('idtareaestandar').order_by('intervalohorasoperacion')
            
            for detalle in detalles:
                # Calcular próxima fecha de mantenimiento basada en horometro estimado
                # Como el modelo Equipos no tiene un campo de horómetro, usamos un valor predeterminado
                # o podríamos obtenerlo de la última orden de trabajo
                horometro_estimado = 0  # Valor predeterminado
                
                # Intentar obtener el último horómetro registrado en órdenes de trabajo
                ultima_ot = OrdenesTrabajo.objects.filter(
                    idequipo=equipo,
                    horometro__isnull=False
                ).order_by('-fechacreacionot').first()
                
                if ultima_ot and ultima_ot.horometro:
                    horometro_estimado = ultima_ot.horometro
                
                # Calcular horas restantes
                horas_restantes = detalle.intervalohorasoperacion - (horometro_estimado % detalle.intervalohorasoperacion)
                if horas_restantes == detalle.intervalohorasoperacion:
                    horas_restantes = 0  # Ya es tiempo de mantenimiento
                
                # Estimar fecha (asumiendo 8 horas de operación por día)
                dias_estimados = horas_restantes / 8
                fecha_estimada = timezone.now().date() + timezone.timedelta(days=int(dias_estimados))
                
                # Crear evento en agenda
                evento = Agendas.objects.create(
                    tituloevento=f"Mantenimiento {detalle.idtareaestandar.nombretarea} - {equipo.nombreequipo}",
                    fechahorainicio=timezone.datetime.combine(fecha_estimada, timezone.datetime.min.time().replace(hour=8)),
                    fechahorafin=timezone.datetime.combine(fecha_estimada, timezone.datetime.min.time().replace(hour=8)) + timezone.timedelta(minutes=detalle.idtareaestandar.tiempoestimadominutos),
                    descripcionevento=f"Mantenimiento preventivo programado cada {detalle.intervalohorasoperacion} horas",
                    tipoevento="Mantenimiento Preventivo",
                    colorevento="#28a745",
                    idequipo=equipo,
                    idplanmantenimiento=plan,
                    idusuariocreador=request.user if request.user.is_authenticated else User.objects.first()
                )
                eventos_creados.append({
                    'id': evento.idagenda,
                    'tituloevento': evento.tituloevento,
                    'fechahorainicio': evento.fechahorainicio,
                    'fechahorafin': evento.fechahorafin,
                    'tipoevento': evento.tipoevento,
                    'equipo': equipo.nombreequipo,
                    'tarea': detalle.idtareaestandar.nombretarea,
                    'intervalo': detalle.intervalohorasoperacion
                })
        
        return Response({
            'message': f'Se crearon {len(eventos_creados)} eventos de agenda',
            'eventos': eventos_creados,
            'plan': {
                'id': plan.idplanmantenimiento,
                'nombre': plan.nombreplan,
                'tipo_equipo': plan.idtipoequipo.nombretipo if plan.idtipoequipo else 'N/A'
            },
            'equipos_afectados': len(set([e['equipo'] for e in eventos_creados])) if eventos_creados else 0
        })

    @action(detail=True, methods=['get'], url_path='detalles')
    def get_detalles(self, request, pk=None):
        """
        Obtiene los detalles de un plan con todas las relaciones incluidas
        """
        plan = self.get_object()
        detalles = DetallesPlanMantenimiento.objects.filter(
            idplanmantenimiento=plan,
            activo=True
        ).select_related(
            'idtareaestandar',
            'idtareaestandar__idtipotarea'
        ).order_by('intervalohorasoperacion')
        
        serializer = DetallesPlanMantenimientoSerializer(detalles, many=True)
        return Response(serializer.data)

class DetallesPlanMantenimientoViewSet(viewsets.ModelViewSet):
    queryset = DetallesPlanMantenimiento.objects.select_related('idtareaestandar', 'idplanmantenimiento').all()
    serializer_class = DetallesPlanMantenimientoSerializer
    permission_classes = [permissions.AllowAny]

class TiposMantenimientoOTViewSet(viewsets.ModelViewSet):
    queryset = TiposMantenimientoOT.objects.all()
    serializer_class = TipoMantenimientoOTSerializer
    permission_classes = [permissions.AllowAny]

class EstadosOrdenTrabajoViewSet(viewsets.ModelViewSet):
    queryset = EstadosOrdenTrabajo.objects.all()
    serializer_class = EstadoOrdenTrabajoSerializer
    permission_classes = [permissions.AllowAny]

# --- NUEVOS VIEWSETS PARA REGISTRO DE MANTENIMIENTOS ---

class OrdenTrabajoViewSet(viewsets.ModelViewSet):
    queryset = OrdenesTrabajo.objects.all().order_by('-fechacreacionot')
    serializer_class = OrdenTrabajoSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'], url_path='crear-desde-plan')
    def crear_desde_plan(self, request):
        """
        Crea una orden de trabajo desde un plan de mantenimiento
        """
        id_equipo = request.data.get('idequipo')
        id_plan = request.data.get('idplanorigen')
        horometro_disparo = request.data.get('horometro')
        id_tecnico = request.data.get('idtecnicoasignado')
        id_solicitante = request.data.get('idsolicitante')
        
        if not all([id_equipo, id_plan, horometro_disparo, id_tecnico, id_solicitante]):
            return Response({'error': 'Faltan datos requeridos.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            equipo = Equipos.objects.get(pk=id_equipo)
            plan = PlanesMantenimiento.objects.get(pk=id_plan)
            tecnico = User.objects.get(pk=id_tecnico)
            solicitante = User.objects.get(pk=id_solicitante)
            
            # Obtener o crear registros necesarios
            try:
                estado_inicial = EstadosOrdenTrabajo.objects.get(nombreestadoot='Abierta')
            except EstadosOrdenTrabajo.DoesNotExist:
                estado_inicial = EstadosOrdenTrabajo.objects.create(
                    nombreestadoot='Abierta', 
                    descripcion='OT recién creada.'
                )
            
            try:
                tipo_ot = TiposMantenimientoOT.objects.get(nombretipomantenimientoot='Preventivo')
            except TiposMantenimientoOT.DoesNotExist:
                tipo_ot = TiposMantenimientoOT.objects.create(
                    nombretipomantenimientoot='Preventivo', 
                    descripcion='Mantenimiento planificado.'
                )
            
            # Buscar tareas aplicables para el horometro
            detalles_aplicables = DetallesPlanMantenimiento.objects.filter(
                idplanmantenimiento=plan,
                intervalohorasoperacion__lte=int(horometro_disparo),
                intervalohorasoperacion__gt=0,
                activo=True
            ).annotate(
                residuo=models.Value(int(horometro_disparo)) % models.F('intervalohorasoperacion')
            ).filter(residuo=0)
            
            if not detalles_aplicables.exists():
                return Response({
                    'error': 'No se encontraron tareas aplicables para el intervalo.'
                }, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                nueva_ot = OrdenesTrabajo.objects.create(
                    numeroot=f"OT-{equipo.codigointerno or equipo.idequipo}-{timezone.now().strftime('%Y%m%d%H%M')}",
                    idequipo=equipo,
                    idplanorigen=plan,
                    idtipomantenimientoot=tipo_ot,
                    idestadoot=estado_inicial,
                    horometro=horometro_disparo,
                    idsolicitante=solicitante,
                    idtecnicoasignado=tecnico,
                    fechaemision=timezone.now().date(),
                    fechaejecucion=request.data.get('fechaejecucion')
                )
                
                # Crear actividades para cada tarea aplicable
                for detalle in detalles_aplicables:
                    ActividadesOrdenTrabajo.objects.create(
                        idordentrabajo=nueva_ot,
                        idtareaestandar=detalle.idtareaestandar,
                        descripcionactividad=detalle.idtareaestandar.descripciontarea or detalle.idtareaestandar.nombretarea,
                        tiempoestimadominutos=detalle.idtareaestandar.tiempoestimadominutos
                    )
            
            serializer = self.get_serializer(nueva_ot)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': f'Ocurrió un error inesperado: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='reportar-falla')
    def reportar_falla(self, request):
        """
        Crea una orden de trabajo correctiva por falla reportada
        """
        try:
            # Validar datos requeridos
            id_equipo = request.data.get('idequipo')
            descripcion = request.data.get('descripcionproblemareportado')

            if not all([id_equipo, descripcion]):
                return Response({
                    'error': 'Faltan datos requeridos: idequipo y descripcionproblemareportado son obligatorios.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Validar que el equipo existe
            try:
                equipo = Equipos.objects.get(pk=id_equipo)
            except Equipos.DoesNotExist:
                return Response({
                    'error': f'El equipo con ID {id_equipo} no existe.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Obtener o crear usuario por defecto para reportes
            if request.user and request.user.is_authenticated:
                solicitante = request.user
            else:
                # Crear o usar usuario por defecto para reportes de falla
                from django.contrib.auth.models import User
                solicitante, created = User.objects.get_or_create(
                    username='operador_reportes',
                    defaults={
                        'first_name': 'Operador',
                        'last_name': 'Reportes',
                        'email': 'operador@somacor.cl',
                        'is_active': True
                    }
                )

            # Obtener o crear el estado y tipo de OT
            try:
                estado_inicial = EstadosOrdenTrabajo.objects.get(nombreestadoot='Abierta')
            except EstadosOrdenTrabajo.DoesNotExist:
                estado_inicial = EstadosOrdenTrabajo.objects.create(
                    nombreestadoot='Abierta', 
                    descripcion='OT recién creada.'
                )
            
            try:
                tipo_ot = TiposMantenimientoOT.objects.get(nombretipomantenimientoot='Correctivo')
            except TiposMantenimientoOT.DoesNotExist:
                tipo_ot = TiposMantenimientoOT.objects.create(
                    nombretipomantenimientoot='Correctivo', 
                    descripcion='Mantenimiento por falla no planificada.'
                )

            # Preparar datos para la OT
            horometro = request.data.get('horometro')
            if horometro:
                try:
                    horometro = int(horometro)
                except (ValueError, TypeError):
                    horometro = None

            prioridad = request.data.get('prioridad', 'Alta')
            if prioridad not in ['Baja', 'Media', 'Alta', 'Crítica']:
                prioridad = 'Alta'

            observaciones = request.data.get('observacionesfinales') or request.data.get('observacionesadicionales') or ''

            try:
                with transaction.atomic():
                    # Establecer fechas automáticamente
                    fecha_actual = timezone.now()
                    fecha_emision = fecha_actual.date()  # Solo fecha para fechaemision
                    
                    # Para mantenimiento correctivo, programar ejecución para el mismo día
                    fecha_ejecucion = fecha_emision
                    
                    nueva_ot = OrdenesTrabajo.objects.create(
                        numeroot=generar_numero_ot_unico(equipo, 'CORR'),
                        idequipo=equipo,
                        idtipomantenimientoot=tipo_ot,
                        idestadoot=estado_inicial,
                        descripcionproblemareportado=descripcion,
                        fechareportefalla=fecha_actual,
                        fechaemision=fecha_emision,
                        fechaejecucion=fecha_ejecucion,
                        idsolicitante=solicitante,
                        idtecnicoasignado=solicitante,
                        prioridad=prioridad,
                        horometro=horometro,
                        observacionesfinales=observaciones
                    )
                
                serializer = self.get_serializer(nueva_ot)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'error': f'Error al crear la orden de trabajo: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"Error en reportar_falla: {error_detail}")  # Para debugging
            return Response({
                'error': f'Error interno del servidor: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='completar')
    def completar_orden(self, request, pk=None):
        """
        Completa una orden de trabajo estableciendo fechacompletado automáticamente
        """
        try:
            orden = self.get_object()
            
            # Verificar que la orden no esté ya completada
            if orden.fechacompletado:
                return Response({
                    'error': 'Esta orden de trabajo ya está completada.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Obtener o crear estado "Completada"
            try:
                estado_completada = EstadosOrdenTrabajo.objects.get(nombreestadoot='Completada')
            except EstadosOrdenTrabajo.DoesNotExist:
                estado_completada = EstadosOrdenTrabajo.objects.create(
                    nombreestadoot='Completada',
                    descripcion='Orden de trabajo completada exitosamente.'
                )
            
            # Actualizar la orden con fecha de completado y estado
            orden.fechacompletado = timezone.now()
            orden.idestadoot = estado_completada
            
            # Agregar observaciones finales si se proporcionan
            observaciones_finales = request.data.get('observacionesfinales', '')
            if observaciones_finales:
                if orden.observacionesfinales:
                    orden.observacionesfinales += f"\n\nCompletado: {observaciones_finales}"
                else:
                    orden.observacionesfinales = observaciones_finales
            
            # Calcular tiempo total si hay actividades
            tiempo_total = request.data.get('tiempototalminutos')
            if tiempo_total:
                try:
                    orden.tiempototalminutos = int(tiempo_total)
                except (ValueError, TypeError):
                    pass
            
            orden.save()
            
            serializer = self.get_serializer(orden)
            return Response({
                'message': 'Orden de trabajo completada exitosamente.',
                'orden': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Error al completar la orden de trabajo: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ActividadOrdenTrabajoViewSet(viewsets.ModelViewSet):
    queryset = ActividadesOrdenTrabajo.objects.all()
    serializer_class = ActividadOrdenTrabajoSerializer
    permission_classes = [permissions.AllowAny]

class AgendaViewSet(viewsets.ModelViewSet):
    queryset = Agendas.objects.all()
    serializer_class = AgendaSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['get'], url_path='calendario')
    def calendario(self, request):
        """
        Retorna eventos de agenda en formato compatible con calendarios
        """
        start_date = request.query_params.get('start')
        end_date = request.query_params.get('end')
        
        queryset = self.get_queryset()
        
        if start_date:
            queryset = queryset.filter(fechahorainicio__gte=start_date)
        if end_date:
            queryset = queryset.filter(fechahorafin__lte=end_date)
        
        eventos = []
        for agenda in queryset:
            eventos.append({
                'id': agenda.idagenda,
                'title': agenda.tituloevento,
                'start': agenda.fechahorainicio.isoformat(),
                'end': agenda.fechahorafin.isoformat(),
                'description': agenda.descripcionevento,
                'color': agenda.colorevento,
                'allDay': agenda.esdiacompleto,
                'extendedProps': {
                    'equipo': agenda.equipo_nombre if hasattr(agenda, 'equipo_nombre') else None,
                    'tipo': agenda.tipoevento,
                    'orden_trabajo': agenda.orden_trabajo_numero if hasattr(agenda, 'orden_trabajo_numero') else None
                }
            })
        
        return Response(eventos)

    @action(detail=False, methods=['post'], url_path='sincronizar-mantenciones')
    def sincronizar_mantenciones(self, request):
        """
        Sincroniza las mantenciones programadas con el calendario
        """
        try:
            eventos_creados = []
            
            # Obtener órdenes de trabajo programadas que no tienen evento en agenda
            ordenes_programadas = OrdenesTrabajo.objects.filter(
                fechaejecucion__isnull=False,
                idestadoot__nombreestadoot__in=['Abierta', 'En Progreso']
            ).exclude(
                idordentrabajo__in=Agendas.objects.values_list('idordentrabajo', flat=True)
            )
            
            for orden in ordenes_programadas:
                # Determinar el tipo de evento basado en el tipo de mantenimiento
                tipo_evento = 'preventivo'
                color_evento = '#3B82F6'  # Azul para preventivo
                
                if orden.idtipomantenimientoot.nombretipomantenimientoot == 'Correctivo':
                    tipo_evento = 'correctivo'
                    color_evento = '#F59E0B'  # Naranja para correctivo
                elif orden.idtipomantenimientoot.nombretipomantenimientoot == 'Predictivo':
                    tipo_evento = 'predictivo'
                    color_evento = '#10B981'  # Verde para predictivo
                
                # Crear título descriptivo
                titulo = f"Mantenimiento {orden.idtipomantenimientoot.nombretipomantenimientoot} - {orden.idequipo.nombreequipo}"
                
                # Crear descripción
                descripcion = f"OT: {orden.numeroot}\n"
                descripcion += f"Equipo: {orden.idequipo.nombreequipo}\n"
                descripcion += f"Tipo: {orden.idtipomantenimientoot.nombretipomantenimientoot}\n"
                descripcion += f"Prioridad: {orden.prioridad}\n"
                if orden.descripcionproblemareportado:
                    descripcion += f"Problema: {orden.descripcionproblemareportado}\n"
                if orden.horometro:
                    descripcion += f"Horómetro: {orden.horometro}h\n"
                
                # Calcular fechas de inicio y fin (asumiendo 4 horas de duración por defecto)
                from datetime import datetime, time
                fecha_inicio = timezone.make_aware(
                    datetime.combine(orden.fechaejecucion, time(8, 0))  # 8:00 AM
                )
                fecha_fin = fecha_inicio + timezone.timedelta(hours=4)
                
                # Obtener o crear usuario por defecto para eventos automáticos
                usuario_sistema, created = User.objects.get_or_create(
                    username='sistema_agenda',
                    defaults={
                        'first_name': 'Sistema',
                        'last_name': 'Agenda',
                        'email': 'sistema@somacor.com',
                        'is_active': True
                    }
                )
                
                # Crear evento en agenda
                evento = Agendas.objects.create(
                    tituloevento=titulo,
                    fechahorainicio=fecha_inicio,
                    fechahorafin=fecha_fin,
                    descripcionevento=descripcion,
                    tipoevento=tipo_evento,
                    colorevento=color_evento,
                    esdiacompleto=False,
                    idequipo=orden.idequipo,
                    idordentrabajo=orden,
                    idusuarioasignado=orden.idtecnicoasignado,
                    idusuariocreador=usuario_sistema
                )
                
                eventos_creados.append({
                    'id': evento.idagenda,
                    'titulo': evento.tituloevento,
                    'fecha': evento.fechahorainicio.isoformat(),
                    'orden_trabajo': orden.numeroot,
                    'equipo': orden.idequipo.nombreequipo
                })
            
            # Sincronizar planes de mantenimiento próximos a vencer
            self._sincronizar_planes_mantenimiento(eventos_creados)
            
            return Response({
                'message': f'Se crearon {len(eventos_creados)} eventos de agenda',
                'eventos': eventos_creados
            })
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"Error detallado en sincronización: {error_detail}")
            return Response({
                'error': f'Error al sincronizar mantenciones: {str(e)}',
                'detalle': error_detail
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _sincronizar_planes_mantenimiento(self, eventos_creados):
        """
        Método auxiliar para sincronizar planes de mantenimiento próximos a vencer
        """
        try:
            from datetime import datetime, timedelta
            
            # Obtener equipos con planes de mantenimiento activos
            equipos_con_planes = Equipos.objects.filter(
                planesmantenimiento__activo=True
            ).distinct()
            
            for equipo in equipos_con_planes:
                planes = PlanesMantenimiento.objects.filter(
                    idequipo=equipo,
                    activo=True
                )
                
                for plan in planes:
                    # Obtener detalles del plan ordenados por intervalo
                    detalles = DetallesPlanMantenimiento.objects.filter(
                        idplanmantenimiento=plan,
                        activo=True
                    ).order_by('intervalohorasoperacion')
                    
                    for detalle in detalles:
                        # Calcular próxima fecha de mantenimiento basada en horómetro actual
                        # (Esta es una lógica simplificada, se puede mejorar)
                        horometro_actual = equipo.horometro if hasattr(equipo, 'horometro') else 0
                        horas_hasta_mantenimiento = detalle.intervalohorasoperacion - (horometro_actual % detalle.intervalohorasoperacion)
                        
                        # Estimar fecha basada en uso promedio (asumiendo 8 horas/día)
                        dias_hasta_mantenimiento = horas_hasta_mantenimiento / 8
                        fecha_estimada = timezone.now().date() + timedelta(days=dias_hasta_mantenimiento)
                        
                        # Solo crear eventos para mantenciones en los próximos 30 días
                        if dias_hasta_mantenimiento <= 30:
                            # Verificar si ya existe un evento para esta tarea
                            evento_existente = Agendas.objects.filter(
                                idequipo=equipo,
                                idplanmantenimiento=plan,
                                tituloevento__icontains=detalle.idtareaestandar.nombretarea,
                                fechahorainicio__date=fecha_estimada
                            ).exists()
                            
                            if not evento_existente:
                                titulo = f"Mantenimiento Preventivo - {equipo.nombreequipo} - {detalle.idtareaestandar.nombretarea}"
                                descripcion = f"Plan: {plan.nombreplan}\n"
                                descripcion += f"Tarea: {detalle.idtareaestandar.nombretarea}\n"
                                descripcion += f"Intervalo: {detalle.intervalohorasoperacion}h\n"
                                descripcion += f"Equipo: {equipo.nombreequipo}\n"
                                descripcion += f"Horómetro estimado: {horometro_actual + horas_hasta_mantenimiento}h"
                                
                                fecha_inicio = timezone.datetime.combine(
                                    fecha_estimada,
                                    timezone.datetime.min.time().replace(hour=9)  # 9:00 AM
                                )
                                fecha_fin = fecha_inicio + timezone.timedelta(
                                    minutes=detalle.idtareaestandar.tiempoestimadominutos or 120
                                )
                                
                                # Obtener usuario sistema para eventos automáticos
                                usuario_sistema, created = User.objects.get_or_create(
                                    username='sistema_agenda',
                                    defaults={
                                        'first_name': 'Sistema',
                                        'last_name': 'Agenda',
                                        'email': 'sistema@somacor.com',
                                        'is_active': True
                                    }
                                )
                                
                                evento = Agendas.objects.create(
                                    tituloevento=titulo,
                                    fechahorainicio=fecha_inicio,
                                    fechahorafin=fecha_fin,
                                    descripcionevento=descripcion,
                                    tipoevento='preventivo',
                                    colorevento='#3B82F6',  # Azul
                                    esdiacompleto=False,
                                    idequipo=equipo,
                                    idplanmantenimiento=plan,
                                    idusuariocreador=usuario_sistema
                                )
                                
                                eventos_creados.append({
                                    'id': evento.idagenda,
                                    'titulo': evento.tituloevento,
                                    'fecha': evento.fechahorainicio.isoformat(),
                                    'plan': plan.nombreplan,
                                    'equipo': equipo.nombreequipo
                                })
                                
        except Exception as e:
            print(f"Error en sincronización de planes: {str(e)}")  # Para debugging


# --- VIEWSET PARA EVIDENCIAS FOTOGRÁFICAS ---

class EvidenciaOTViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar evidencias fotográficas de órdenes de trabajo
    """
    queryset = EvidenciaOT.objects.all()
    serializer_class = EvidenciaOTSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        orden_trabajo_id = self.request.query_params.get('orden_trabajo', None)
        if orden_trabajo_id:
            queryset = queryset.filter(idordentrabajo=orden_trabajo_id)
        return queryset
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

# --- Endpoints Simples para Testing ---
def dashboard_stats_simple(request):
    """Endpoint simple para estadísticas del dashboard sin autenticación"""
    try:
        hoy = timezone.now()
        hace_30_dias = hoy - timedelta(days=30)
        
        # Estadísticas básicas
        equipos_total = Equipos.objects.count()
        equipos_activos = Equipos.objects.filter(activo=True).count()
        ordenes_total = OrdenesTrabajo.objects.count()
        ordenes_pendientes = OrdenesTrabajo.objects.filter(
            idestadoot__nombreestadoot__in=['Pendiente', 'En Proceso']
        ).count()
        ordenes_completadas_mes = OrdenesTrabajo.objects.filter(
            fechacompletado__gte=hace_30_dias,
            idestadoot__nombreestadoot='Completada'
        ).count()
        
        stats = {
            'equipos': {
                'total': equipos_total,
                'activos': equipos_activos,
                'en_mantenimiento': equipos_total - equipos_activos,
                'disponibilidad': round((equipos_activos / equipos_total * 100), 1) if equipos_total > 0 else 0
            },
            'ordenes': {
                'total': ordenes_total,
                'pendientes': ordenes_pendientes,
                'completadas_mes': ordenes_completadas_mes,
                'vencidas': 0,
                'tiempo_promedio_horas': 24.5
            },
            'sistema': {
                'eficiencia': 87.2,
                'ordenes_por_dia': round(ordenes_completadas_mes / 30, 1),
                'tasa_completado': round(ordenes_completadas_mes / max(ordenes_total, 1) * 100, 1)
            }
        }
        
        return JsonResponse(stats)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def dashboard_recent_simple(request):
    """Endpoint simple para órdenes recientes sin autenticación"""
    try:
        limite = int(request.GET.get('limit', 5))
        
        # Obtener órdenes recientes
        ordenes_recientes = OrdenesTrabajo.objects.select_related(
            'idequipo', 'idestadoot', 'idsolicitante', 'idtecnicoasignado'
        ).order_by('-fechareportefalla')[:limite]
        
        data = []
        for orden in ordenes_recientes:
            data.append({
                'idordentrabajo': orden.idordentrabajo,
                'numeroot': orden.numeroot,
                'descripcionproblemareportado': orden.descripcionproblemareportado,
                'prioridad': orden.prioridad,
                'estado_nombre': orden.idestadoot.nombreestadoot if orden.idestadoot else 'Sin estado',
                'equipo_nombre': orden.idequipo.nombreequipo if orden.idequipo else 'Sin equipo',
                'fechareportefalla': orden.fechareportefalla.isoformat() if orden.fechareportefalla else None,
                'solicitante_nombre': orden.idsolicitante.get_full_name() if orden.idsolicitante else 'Sin solicitante',
                'tecnico_nombre': orden.idtecnicoasignado.get_full_name() if orden.idtecnicoasignado else 'Sin técnico'
            })
        
        return JsonResponse({'results': data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

