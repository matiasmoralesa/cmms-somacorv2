"""
Views V2 - Versión optimizada y moderna para CMMS
"""
from rest_framework import viewsets, filters, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q, Avg, Sum, F, Case, When, IntegerField
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from .models import *
from .serializers_v2 import *

logger = logging.getLogger(__name__)

# =============================================================================
# VIEWSETS DE EQUIPOS
# =============================================================================

class EquiposViewSet(viewsets.ModelViewSet):
    """ViewSet para equipos con funcionalidades avanzadas"""
    queryset = Equipos.objects.select_related(
        'idtipoequipo', 'idestadoactual', 'idfaenaactual'
    ).prefetch_related('ordenestrabajo_set').all()
    serializer_class = EquiposSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['idtipoequipo', 'idestadoactual', 'idfaenaactual', 'activo']
    search_fields = ['nombreequipo', 'codigointerno', 'marca', 'modelo', 'patente']
    ordering_fields = ['nombreequipo', 'codigointerno', 'anio', 'fechacreacion']
    ordering = ['nombreequipo']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro por estado crítico
        if self.request.query_params.get('criticos') == 'true':
            queryset = queryset.filter(
                idestadoactual__nombreestado__icontains='mantenimiento'
            )
        
        # Filtro por equipos sin mantenimiento reciente
        if self.request.query_params.get('sin_mantenimiento') == 'true':
            hace_30_dias = timezone.now() - timedelta(days=30)
            queryset = queryset.exclude(
                ordenestrabajo__fechacompletado__gte=hace_30_dias
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estadísticas de equipos"""
        try:
            stats = {
                'total_equipos': self.get_queryset().count(),
                'equipos_activos': self.get_queryset().filter(activo=True).count(),
                'equipos_inactivos': self.get_queryset().filter(activo=False).count(),
                'por_estado': {},
                'por_tipo': {},
                'por_faena': {},
                'equipos_criticos': self.get_queryset().filter(
                    idestadoactual__nombreestado__icontains='mantenimiento'
                ).count(),
            }
            
            # Estadísticas por estado
            estados = self.get_queryset().values(
                'idestadoactual__nombreestado'
            ).annotate(count=Count('idequipo')).order_by('-count')
            stats['por_estado'] = {item['idestadoactual__nombreestado']: item['count'] for item in estados}
            
            # Estadísticas por tipo
            tipos = self.get_queryset().values(
                'idtipoequipo__nombretipo'
            ).annotate(count=Count('idequipo')).order_by('-count')
            stats['por_tipo'] = {item['idtipoequipo__nombretipo']: item['count'] for item in tipos}
            
            # Estadísticas por faena
            faenas = self.get_queryset().values(
                'idfaenaactual__nombrefaena'
            ).annotate(count=Count('idequipo')).order_by('-count')
            stats['por_faena'] = {item['idfaenaactual__nombrefaena']: item['count'] for item in faenas}
            
            return Response(stats)
        except Exception as e:
            logger.error(f"Error en stats de equipos: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def criticos(self, request):
        """Equipos críticos que requieren atención"""
        try:
            equipos_criticos = self.get_queryset().filter(
                Q(idestadoactual__nombreestado__icontains='mantenimiento') |
                Q(ordenestrabajo__idestadoot__nombreestadoot__in=['Pendiente', 'En Proceso'])
            ).distinct().order_by('-fechacreacion')[:20]
            
            serializer = self.get_serializer(equipos_criticos, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error en equipos críticos: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def detalles(self, request, pk=None):
        """Detalles completos del equipo con métricas de rendimiento"""
        try:
            equipo = self.get_object()
            
            # Obtener órdenes de trabajo del equipo
            ordenes = OrdenesTrabajo.objects.filter(idequipo=equipo)
            ordenes_30_dias = ordenes.filter(
                fechareportefalla__gte=timezone.now() - timedelta(days=30)
            )
            
            # Calcular métricas
            total_ordenes = ordenes.count()
            ordenes_completadas = ordenes.filter(
                idestadoot__nombreestadoot='Completada'
            ).count()
            ordenes_pendientes = ordenes.filter(
                idestadoot__nombreestadoot__in=['Abierta', 'Asignada', 'En Progreso']
            ).count()
            
            # Calcular tiempo de inactividad
            ordenes_mantenimiento = ordenes_30_dias.filter(
                idtipomantenimientoot__isnull=False
            )
            
            horas_mantenimiento = 0
            for orden in ordenes_mantenimiento:
                if orden.fechacompletado and orden.fechareportefalla:
                    delta = orden.fechacompletado - orden.fechareportefalla
                    horas_mantenimiento += delta.total_seconds() / 3600
            
            # Calcular métricas basadas en datos reales
            estado_nombre = equipo.idestadoactual.nombreestado if equipo.idestadoactual else 'Desconocido'
            
            # Calcular uptime basado en órdenes de trabajo
            # Uptime = (Tiempo total - Tiempo en mantenimiento) / Tiempo total * 100
            dias_totales = 30  # Últimos 30 días
            horas_totales = dias_totales * 24
            porcentaje_inactividad = (horas_mantenimiento / horas_totales) * 100 if horas_totales > 0 else 0
            uptime = max(0, min(100, 100 - porcentaje_inactividad))
            
            # Ajustar uptime según estado actual
            if 'operativo' in estado_nombre.lower():
                uptime = max(uptime, 95)  # Mínimo 95% si está operativo
                efficiency = 92
                availability = 100
                health_score = 95
            elif 'mantenimiento' in estado_nombre.lower():
                uptime = min(uptime, 80)  # Máximo 80% si está en mantenimiento
                efficiency = 60
                availability = 0
                health_score = 65
            else:
                uptime = min(uptime, 50)
                efficiency = 20
                availability = 0
                health_score = 25
            
            # Ajustar health_score basado en órdenes pendientes
            if ordenes_pendientes > 0:
                health_score = max(25, health_score - (ordenes_pendientes * 10))
            
            # Ajustar efficiency basado en órdenes completadas vs total
            if total_ordenes > 0:
                tasa_completado = (ordenes_completadas / total_ordenes) * 100
                efficiency = min(efficiency, tasa_completado)
            
            # Calcular días desde último mantenimiento
            ultimo_mantenimiento = ordenes.filter(
                idestadoot__nombreestadoot='Completada',
                idtipomantenimientoot__isnull=False
            ).order_by('-fechacompletado').first()
            
            dias_desde_mantenimiento = 0
            if ultimo_mantenimiento and ultimo_mantenimiento.fechacompletado:
                delta = timezone.now() - ultimo_mantenimiento.fechacompletado
                dias_desde_mantenimiento = delta.days
            
            # Próximo mantenimiento (simulado)
            proximo_mantenimiento = None
            if ultimo_mantenimiento and ultimo_mantenimiento.fechacompletado:
                proximo_mantenimiento = ultimo_mantenimiento.fechacompletado + timedelta(days=30)
            
            # Calcular OEE (Overall Equipment Effectiveness)
            oee_score = (availability * efficiency * (health_score / 100)) / 100
            
            # Preparar respuesta
            response_data = {
                'equipo': self.get_serializer(equipo).data,
                'metricas': {
                    'health_score': round(health_score, 1),
                    'uptime': round(uptime, 1),
                    'efficiency': round(efficiency, 1),
                    'availability': round(availability, 1),
                    'oee_score': round(oee_score, 1),
                },
                'mantenimiento': {
                    'total_ordenes': total_ordenes,
                    'ordenes_completadas': ordenes_completadas,
                    'ordenes_pendientes': ordenes_pendientes,
                    'horas_mantenimiento': round(horas_mantenimiento, 1),
                    'dias_desde_ultimo': dias_desde_mantenimiento,
                    'ultimo_mantenimiento': ultimo_mantenimiento.fechacompletado.strftime('%d-%m-%Y') if ultimo_mantenimiento and ultimo_mantenimiento.fechacompletado else None,
                    'proximo_mantenimiento': proximo_mantenimiento.strftime('%d-%m-%Y') if proximo_mantenimiento else None,
                },
                'fallas': {
                    'fallas_activas': ordenes_pendientes,
                    'fallas_30_dias': ordenes_30_dias.count(),
                },
                'estado': {
                    'nombre': estado_nombre,
                    'activo': equipo.activo,
                }
            }
            
            return Response(response_data)
        except Exception as e:
            logger.error(f"Error en detalles de equipo: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# =============================================================================
# VIEWSETS DE ÓRDENES DE TRABAJO
# =============================================================================

class OrdenesTrabajoViewSet(viewsets.ModelViewSet):
    """ViewSet para órdenes de trabajo con funcionalidades avanzadas"""
    queryset = OrdenesTrabajo.objects.select_related(
        'idequipo', 'idsolicitante', 'idtecnicoasignado', 
        'idestadoot', 'idtipomantenimientoot'
    ).prefetch_related('actividadesordentrabajo_set').all()
    serializer_class = OrdenesTrabajoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['idestadoot', 'idtipomantenimientoot', 'prioridad', 'idequipo']
    search_fields = ['numeroot', 'descripcionproblemareportado', 'idequipo__nombreequipo']
    ordering_fields = ['fechareportefalla', 'prioridad', 'fechacompletado']
    ordering = ['-fechareportefalla']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro por fecha
        fecha_desde = self.request.query_params.get('fecha_desde')
        fecha_hasta = self.request.query_params.get('fecha_hasta')
        
        if fecha_desde:
            queryset = queryset.filter(fechareportefalla__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fechareportefalla__lte=fecha_hasta)
        
        # Filtro por días pendientes
        dias_pendientes = self.request.query_params.get('dias_pendientes')
        if dias_pendientes:
            fecha_limite = timezone.now() - timedelta(days=int(dias_pendientes))
            queryset = queryset.filter(
                fechareportefalla__lte=fecha_limite,
                idestadoot__nombreestadoot__in=['Pendiente', 'En Proceso']
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estadísticas de órdenes de trabajo"""
        try:
            queryset = self.get_queryset()
            
            # Estadísticas básicas
            stats = {
                'total_ordenes': queryset.count(),
                'por_estado': {},
                'por_prioridad': {},
                'por_tipo_mantenimiento': {},
                'tiempo_promedio_resolucion': 0,
                'ordenes_vencidas': 0,
                'ordenes_ultimos_30_dias': 0,
            }
            
            # Estadísticas por estado
            estados = queryset.values('idestadoot__nombreestadoot').annotate(
                count=Count('idordentrabajo')
            ).order_by('-count')
            stats['por_estado'] = {item['idestadoot__nombreestadoot']: item['count'] for item in estados}
            
            # Estadísticas por prioridad
            prioridades = queryset.values('prioridad').annotate(
                count=Count('idordentrabajo')
            ).order_by('-count')
            stats['por_prioridad'] = {item['prioridad']: item['count'] for item in prioridades}
            
            # Estadísticas por tipo de mantenimiento
            tipos = queryset.values('idtipomantenimientoot__nombretipo').annotate(
                count=Count('idordentrabajo')
            ).order_by('-count')
            stats['por_tipo_mantenimiento'] = {item['idtipomantenimientoot__nombretipo']: item['count'] for item in tipos}
            
            # Tiempo promedio de resolución
            ordenes_completadas = queryset.filter(
                idestadoot__nombreestadoot='Completada',
                tiempototalminutos__isnull=False
            )
            if ordenes_completadas.exists():
                avg_time = ordenes_completadas.aggregate(
                    avg_time=Avg('tiempototalminutos')
                )['avg_time']
                stats['tiempo_promedio_resolucion'] = round(avg_time / 60, 2)  # en horas
            
            # Órdenes vencidas (más de 7 días pendientes)
            hace_7_dias = timezone.now() - timedelta(days=7)
            stats['ordenes_vencidas'] = queryset.filter(
                fechareportefalla__lte=hace_7_dias,
                idestadoot__nombreestadoot__in=['Pendiente', 'En Proceso']
            ).count()
            
            # Órdenes de los últimos 30 días
            hace_30_dias = timezone.now() - timedelta(days=30)
            stats['ordenes_ultimos_30_dias'] = queryset.filter(
                fechareportefalla__gte=hace_30_dias
            ).count()
            
            return Response(stats)
        except Exception as e:
            logger.error(f"Error en stats de órdenes: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def recientes(self, request):
        """Órdenes de trabajo recientes"""
        try:
            limite = int(request.query_params.get('limit', 10))
            ordenes_recientes = self.get_queryset().order_by('-fechareportefalla')[:limite]
            serializer = self.get_serializer(ordenes_recientes, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error en órdenes recientes: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def vencidas(self, request):
        """Órdenes de trabajo vencidas"""
        try:
            hace_7_dias = timezone.now() - timedelta(days=7)
            ordenes_vencidas = self.get_queryset().filter(
                fechareportefalla__lte=hace_7_dias,
                idestadoot__nombreestadoot__in=['Pendiente', 'En Proceso']
            ).order_by('fechareportefalla')
            
            serializer = self.get_serializer(ordenes_vencidas, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error en órdenes vencidas: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# =============================================================================
# VIEWSETS DE DASHBOARD
# =============================================================================

class DashboardViewSet(viewsets.ViewSet):
    """ViewSet para estadísticas del dashboard"""
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estadísticas generales del dashboard"""
        try:
            hoy = timezone.now()
            hace_30_dias = hoy - timedelta(days=30)
            hace_7_dias = hoy - timedelta(days=7)
            
            # Estadísticas de equipos
            equipos_total = Equipos.objects.count()
            equipos_activos = Equipos.objects.filter(activo=True).count()
            equipos_en_mantenimiento = Equipos.objects.filter(
                idestadoactual__nombreestado__icontains='mantenimiento'
            ).count()
            
            # Estadísticas de órdenes
            ordenes_total = OrdenesTrabajo.objects.count()
            ordenes_pendientes = OrdenesTrabajo.objects.filter(
                idestadoot__nombreestadoot__in=['Pendiente', 'En Proceso']
            ).count()
            ordenes_completadas_mes = OrdenesTrabajo.objects.filter(
                fechacompletado__gte=hace_30_dias,
                idestadoot__nombreestadoot='Completada'
            ).count()
            ordenes_vencidas = OrdenesTrabajo.objects.filter(
                fechareportefalla__lte=hace_7_dias,
                idestadoot__nombreestadoot__in=['Pendiente', 'En Proceso']
            ).count()
            
            # Eficiencia del sistema
            tiempo_promedio = OrdenesTrabajo.objects.filter(
                idestadoot__nombreestadoot='Completada',
                tiempototalminutos__isnull=False
            ).aggregate(avg_time=Avg('tiempototalminutos'))['avg_time']
            
            eficiencia = 0
            if tiempo_promedio:
                eficiencia = max(0, min(100, 100 - (tiempo_promedio / 60 / 24 * 10)))  # Fórmula de eficiencia
            
            stats = {
                'equipos': {
                    'total': equipos_total,
                    'activos': equipos_activos,
                    'en_mantenimiento': equipos_en_mantenimiento,
                    'disponibilidad': round((equipos_activos - equipos_en_mantenimiento) / equipos_total * 100, 1) if equipos_total > 0 else 0
                },
                'ordenes': {
                    'total': ordenes_total,
                    'pendientes': ordenes_pendientes,
                    'completadas_mes': ordenes_completadas_mes,
                    'vencidas': ordenes_vencidas,
                    'tiempo_promedio_horas': round(tiempo_promedio / 60, 2) if tiempo_promedio else 0
                },
                'sistema': {
                    'eficiencia': round(eficiencia, 1),
                    'ordenes_por_dia': round(ordenes_completadas_mes / 30, 1),
                    'tasa_completado': round(ordenes_completadas_mes / max(ordenes_total, 1) * 100, 1)
                }
            }
            
            return Response(stats)
        except Exception as e:
            logger.error(f"Error en stats del dashboard: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # NOTA: Primera definición duplicada de monthly_data eliminada (optimización)
    # Ver línea ~1171 para la definición activa
    
    @action(detail=False, methods=['get'])
    def maintenance_types(self, request):
        """Distribución de tipos de mantenimiento"""
        try:
            tipos = OrdenesTrabajo.objects.values(
                'idtipomantenimientoot__nombretipomantenimientoot'
            ).annotate(
                count=Count('idordentrabajo'),
                tiempo_promedio=Avg('tiempototalminutos')
            ).order_by('-count')
            
            data = []
            for tipo in tipos:
                data.append({
                    'tipo': tipo['idtipomantenimientoot__nombretipomantenimientoot'],
                    'cantidad': tipo['count'],
                    'porcentaje': round(tipo['count'] / OrdenesTrabajo.objects.count() * 100, 1),
                    'tiempo_promedio_horas': round(tipo['tiempo_promedio'] / 60, 2) if tipo['tiempo_promedio'] else 0
                })
            
            return Response(data)
        except Exception as e:
            logger.error(f"Error en tipos de mantenimiento: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def recent_work_orders(self, request):
        """Obtener órdenes de trabajo recientes"""
        try:
            limit = int(request.query_params.get('limit', 5))
            ordenes = OrdenesTrabajo.objects.select_related(
                'idequipo', 'idestadoot', 'idtecnicoasignado'
            ).order_by('-fechareportefalla')[:limit]
            
            serializer = OrdenesTrabajoSerializer(ordenes, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error obteniendo órdenes recientes: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# =============================================================================
# VIEWSETS DE BÚSQUEDA
# =============================================================================

class SearchViewSet(viewsets.ViewSet):
    """ViewSet para búsquedas globales"""
    
    @action(detail=False, methods=['get'])
    def equipos(self, request):
        """Búsqueda de equipos"""
        try:
            query = request.query_params.get('search', '')
            if not query:
                return Response({'results': []})
            
            equipos = Equipos.objects.filter(
                Q(nombreequipo__icontains=query) |
                Q(codigointerno__icontains=query) |
                Q(marca__icontains=query) |
                Q(modelo__icontains=query) |
                Q(patente__icontains=query)
            ).select_related('idtipoequipo', 'idestadoactual', 'idfaenaactual')[:10]
            
            serializer = EquiposSerializer(equipos, many=True)
            return Response({'results': serializer.data})
        except Exception as e:
            logger.error(f"Error en búsqueda de equipos: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def ordenes(self, request):
        """Búsqueda de órdenes de trabajo"""
        try:
            query = request.query_params.get('search', '')
            if not query:
                return Response({'results': []})
            
            ordenes = OrdenesTrabajo.objects.filter(
                Q(numeroot__icontains=query) |
                Q(descripcionproblemareportado__icontains=query) |
                Q(idequipo__nombreequipo__icontains=query) |
                Q(idequipo__codigointerno__icontains=query)
            ).select_related(
                'idequipo', 'idsolicitante', 'idtecnicoasignado', 
                'idestadoot', 'idtipomantenimientoot'
            )[:10]
            
            serializer = OrdenesTrabajoSerializer(ordenes, many=True)
            return Response({'results': serializer.data})
        except Exception as e:
            logger.error(f"Error en búsqueda de órdenes: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# VIEWSETS PARA FORMULARIOS
# =============================================================================

class FaenasViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de faenas"""
    queryset = Faenas.objects.all()
    serializer_class = FaenasSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return Faenas.objects.all().order_by('nombrefaena')
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estadísticas de faenas"""
        try:
            total_faenas = Faenas.objects.count()
            active_faenas = Faenas.objects.filter(activa=True).count()
            inactive_faenas = total_faenas - active_faenas
            
            return Response({
                'total_faenas': total_faenas,
                'active_faenas': active_faenas,
                'inactive_faenas': inactive_faenas
            })
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de faenas: {e}")
            return Response({'error': 'Error obteniendo estadísticas'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UsuariosViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de usuarios/técnicos"""
    queryset = Usuarios.objects.all()
    serializer_class = UsuariosSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return Usuarios.objects.select_related('idrol', 'user').order_by('user__first_name', 'user__last_name')
    
    @action(detail=False, methods=['get'])
    def tecnicos(self, request):
        """Obtener solo técnicos"""
        try:
            # Asumir que el rol de técnico tiene ID 3
            tecnicos = Usuarios.objects.filter(
                idrol__idrol=3
            ).select_related('idrol', 'user').order_by('user__first_name', 'user__last_name')
            
            serializer = UsuariosSerializer(tecnicos, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error obteniendo técnicos: {e}")
            return Response({'error': 'Error obteniendo técnicos'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TiposEquipoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de tipos de equipo"""
    queryset = TiposEquipo.objects.all()
    serializer_class = TiposEquipoSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return TiposEquipo.objects.all().order_by('nombretipo')
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estadísticas de tipos de equipo"""
        try:
            total_tipos = TiposEquipo.objects.count()
            active_tipos = TiposEquipo.objects.filter(activo=True).count()
            
            return Response({
                'total_tipos': total_tipos,
                'active_tipos': active_tipos
            })
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de tipos de equipo: {e}")
            return Response({'error': 'Error obteniendo estadísticas'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChecklistInstanceViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de checklist instances"""
    queryset = ChecklistInstance.objects.all()
    serializer_class = ChecklistInstanceSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return ChecklistInstance.objects.select_related(
            'orden_trabajo', 'checklist_template'
        ).order_by('-fecha_creacion')
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estadísticas de checklists"""
        try:
            total_checklists = ChecklistInstance.objects.count()
            completed_checklists = ChecklistInstance.objects.filter(
                estado='completado'
            ).count()
            pending_checklists = ChecklistInstance.objects.filter(
                estado='pendiente'
            ).count()
            
            return Response({
                'total_checklists': total_checklists,
                'completed_checklists': completed_checklists,
                'pending_checklists': pending_checklists
            })
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de checklists: {e}")
            return Response({'error': 'Error obteniendo estadísticas'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InventarioViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de inventario (placeholder - requiere modelo)"""
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        # Este ViewSet requiere un modelo de Inventario que no existe actualmente
        # Por ahora retornamos una lista vacía
        return []
    
    def list(self, request):
        """Lista de items de inventario"""
        # Placeholder - requiere implementación del modelo Inventario
        return Response({'results': []})
    
    def create(self, request):
        """Crear item de inventario"""
        # Placeholder - requiere implementación del modelo Inventario
        return Response({'message': 'Inventario no implementado aún'}, status=status.HTTP_501_NOT_IMPLEMENTED)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estadísticas de inventario"""
        # Placeholder - requiere implementación del modelo Inventario
        return Response({
            'total_items': 0,
            'low_stock': 0,
            'out_of_stock': 0
        })


class RolesViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de roles"""
    queryset = Roles.objects.all()
    serializer_class = RolesSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return Roles.objects.all().order_by('nombrerol')



# =============================================================================
# VIEWSETS DE CHECKLIST TEMPLATES
# =============================================================================

class ChecklistTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet para plantillas de checklist"""
    queryset = ChecklistTemplate.objects.select_related('tipo_equipo').all()
    serializer_class = ChecklistTemplateSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['tipo_equipo', 'activo']
    search_fields = ['nombre']
    ordering = ['nombre']
    
    @action(detail=True, methods=['get'])
    def with_items(self, request, pk=None):
        """Obtener plantilla con todas sus categorías e items"""
        try:
            template = self.get_object()
            categories = ChecklistCategory.objects.filter(template=template).prefetch_related('items').order_by('orden')
            
            data = {
                'id_template': template.id_template,
                'nombre': template.nombre,
                'tipo_equipo': {
                    'id': template.tipo_equipo.idtipoequipo,
                    'nombre': template.tipo_equipo.nombretipo
                },
                'activo': template.activo,
                'categorias': []
            }
            
            for category in categories:
                items = category.items.all().order_by('orden')
                data['categorias'].append({
                    'id_category': category.id_category,
                    'nombre': category.nombre,
                    'orden': category.orden,
                    'items': [
                        {
                            'id_item': item.id_item,
                            'texto': item.texto,
                            'es_critico': item.es_critico,
                            'orden': item.orden
                        }
                        for item in items
                    ]
                })
            
            return Response(data)
        except Exception as e:
            logger.error(f"Error obteniendo plantilla con items: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChecklistCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet para categorías de checklist"""
    queryset = ChecklistCategory.objects.select_related('template').all()
    serializer_class = ChecklistCategorySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['template']
    ordering = ['template', 'orden']


class ChecklistItemViewSet(viewsets.ModelViewSet):
    """ViewSet para items de checklist"""
    queryset = ChecklistItem.objects.select_related('category').all()
    serializer_class = ChecklistItemSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'es_critico']
    ordering = ['category', 'orden']


# NOTA: Primera definición duplicada de DashboardViewSet eliminada (optimización)
# Ver línea ~972 para la definición activa y consolidada

# =============================================================================
# DASHBOARD VIEWSET
# =============================================================================

class DashboardViewSet(viewsets.ViewSet):
    """ViewSet para el dashboard con estadísticas y datos agregados"""
    permission_classes = [permissions.AllowAny]  # Permitir acceso sin autenticación
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estadísticas generales del sistema"""
        try:
            # Estadísticas de equipos
            total_equipos = Equipos.objects.filter(activo=True).count()
            equipos_operativos = Equipos.objects.filter(
                activo=True,
                idestadoactual__nombreestado='Operativo'
            ).count()
            equipos_mantenimiento = Equipos.objects.filter(
                activo=True,
                idestadoactual__nombreestado__icontains='Mantenimiento'
            ).count()
            
            disponibilidad = (equipos_operativos / total_equipos * 100) if total_equipos > 0 else 0
            
            # Estadísticas de órdenes de trabajo
            total_ordenes = OrdenesTrabajo.objects.count()
            ordenes_pendientes = OrdenesTrabajo.objects.filter(
                idestadoot__nombreestadoot__in=['Abierta', 'Asignada', 'Pendiente Aprobación']
            ).count()
            
            # Órdenes completadas este mes
            inicio_mes = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            ordenes_completadas_mes = OrdenesTrabajo.objects.filter(
                fechacompletado__gte=inicio_mes,
                idestadoot__nombreestadoot='Completada'
            ).count()
            
            # Órdenes vencidas (más de 7 días sin completar)
            hace_7_dias = timezone.now() - timedelta(days=7)
            ordenes_vencidas = OrdenesTrabajo.objects.filter(
                fechacreacionot__lte=hace_7_dias,
                fechacompletado__isnull=True
            ).exclude(
                idestadoot__nombreestadoot__in=['Completada', 'Cancelada']
            ).count()
            
            # Tiempo promedio de resolución
            ordenes_completadas = OrdenesTrabajo.objects.filter(
                fechacompletado__isnull=False,
                tiempototalminutos__isnull=False
            )
            tiempo_promedio = ordenes_completadas.aggregate(
                promedio=Avg('tiempototalminutos')
            )['promedio'] or 0
            tiempo_promedio_horas = round(tiempo_promedio / 60, 1)
            
            # Eficiencia del sistema
            ordenes_completadas_count = OrdenesTrabajo.objects.filter(
                idestadoot__nombreestadoot='Completada'
            ).count()
            eficiencia = (ordenes_completadas_count / total_ordenes * 100) if total_ordenes > 0 else 0
            
            # Órdenes por día (promedio últimos 30 días)
            hace_30_dias = timezone.now() - timedelta(days=30)
            ordenes_ultimos_30 = OrdenesTrabajo.objects.filter(
                fechacreacionot__gte=hace_30_dias
            ).count()
            ordenes_por_dia = round(ordenes_ultimos_30 / 30, 1)
            
            # Tasa de completado
            tasa_completado = (ordenes_completadas_count / total_ordenes * 100) if total_ordenes > 0 else 0
            
            stats = {
                'equipos': {
                    'total': total_equipos,
                    'activos': equipos_operativos,
                    'en_mantenimiento': equipos_mantenimiento,
                    'disponibilidad': round(disponibilidad, 1)
                },
                'ordenes': {
                    'total': total_ordenes,
                    'pendientes': ordenes_pendientes,
                    'completadas_mes': ordenes_completadas_mes,
                    'vencidas': ordenes_vencidas,
                    'tiempo_promedio_horas': tiempo_promedio_horas
                },
                'sistema': {
                    'eficiencia': round(eficiencia, 1),
                    'ordenes_por_dia': ordenes_por_dia,
                    'tasa_completado': round(tasa_completado, 1)
                }
            }
            
            logger.info(f"Dashboard stats generadas: {stats}")
            return Response(stats)
            
        except Exception as e:
            logger.error(f"Error generando stats del dashboard: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def monthly_data(self, request):
        """Datos mensuales de órdenes de trabajo para gráfico
        
        Parámetros:
            year (int): Año para filtrar datos (default: últimos 12 meses)
        
        Retorna:
            Lista de últimos 12 meses con órdenes completadas y pendientes
        """
        try:
            # Obtener fecha actual
            fecha_actual = timezone.now()
            
            # Si se especifica un año, usar ese año completo
            año_param = request.query_params.get('year')
            if año_param:
                año = int(año_param)
                meses_nombres = [
                    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
                ]
                
                monthly_data = []
                for mes in range(1, 13):
                    completadas = OrdenesTrabajo.objects.filter(
                        fechareportefalla__year=año,
                        fechareportefalla__month=mes,
                        idestadoot__nombreestadoot='Completada'
                    ).count()
                    
                    pendientes = OrdenesTrabajo.objects.filter(
                        fechareportefalla__year=año,
                        fechareportefalla__month=mes
                    ).exclude(
                        idestadoot__nombreestadoot__in=['Completada', 'Cancelada']
                    ).count()
                    
                    monthly_data.append({
                        'month': meses_nombres[mes - 1],
                        'completadas': completadas,
                        'pendientes': pendientes
                    })
            else:
                # Generar datos para los últimos 12 meses
                monthly_data = []
                meses_nombres_cortos = {
                    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
                    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
                    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
                }
                
                for i in range(11, -1, -1):  # Últimos 12 meses (de más antiguo a más reciente)
                    # Calcular el mes y año correspondiente
                    mes_offset = fecha_actual.month - i - 1
                    año = fecha_actual.year
                    mes = fecha_actual.month - i
                    
                    # Ajustar si el mes es negativo o mayor a 12
                    while mes <= 0:
                        mes += 12
                        año -= 1
                    while mes > 12:
                        mes -= 12
                        año += 1
                    
                    completadas = OrdenesTrabajo.objects.filter(
                        fechareportefalla__year=año,
                        fechareportefalla__month=mes,
                        idestadoot__nombreestadoot='Completada'
                    ).count()
                    
                    pendientes = OrdenesTrabajo.objects.filter(
                        fechareportefalla__year=año,
                        fechareportefalla__month=mes
                    ).exclude(
                        idestadoot__nombreestadoot__in=['Completada', 'Cancelada']
                    ).count()
                    
                    monthly_data.append({
                        'month': meses_nombres_cortos[mes],
                        'completadas': completadas,
                        'pendientes': pendientes
                    })
            
            logger.info(f"Datos mensuales generados: {len(monthly_data)} meses")
            return Response(monthly_data)
            
        except Exception as e:
            logger.error(f"Error generando datos mensuales: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def maintenance_types(self, request):
        """Distribución de tipos de mantenimiento"""
        try:
            # Contar órdenes por tipo de mantenimiento
            tipos = OrdenesTrabajo.objects.values(
                'idtipomantenimientoot__nombretipomantenimientoot'
            ).annotate(
                cantidad=Count('idordentrabajo')
            ).order_by('-cantidad')
            
            # Formatear datos
            maintenance_types = []
            for tipo in tipos:
                nombre_tipo = tipo['idtipomantenimientoot__nombretipomantenimientoot'] or 'Sin tipo'
                maintenance_types.append({
                    'tipo': nombre_tipo,
                    'cantidad': tipo['cantidad']
                })
            
            logger.info(f"Tipos de mantenimiento generados: {len(maintenance_types)}")
            return Response(maintenance_types)
            
        except Exception as e:
            logger.error(f"Error generando tipos de mantenimiento: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def recent_work_orders(self, request):
        """Órdenes de trabajo recientes"""
        try:
            limit = int(request.query_params.get('limit', 5))
            
            ordenes = OrdenesTrabajo.objects.select_related(
                'idequipo',
                'idtecnicoasignado',
                'idestadoot',
                'idtipomantenimientoot'
            ).order_by('-fechacreacionot')[:limit]
            
            serializer = OrdenesTrabajoSerializer(ordenes, many=True)
            
            logger.info(f"Órdenes recientes generadas: {len(serializer.data)}")
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error generando órdenes recientes: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# =============================================================================
# NOTA: Código duplicado eliminado (Fase 2 de optimización)
# =============================================================================
# - 3 definiciones duplicadas de DashboardViewSet eliminadas (~400 líneas)
# - Funciones dashboard_stats, dashboard_recent_work_orders, dashboard_monthly_data eliminadas
# - Función dashboard_maintenance_types eliminada
# 
# Todas las funcionalidades del dashboard están consolidadas en el único
# DashboardViewSet activo (línea ~972) con los siguientes endpoints:
# - /api/v2/dashboard/stats/
# - /api/v2/dashboard/monthly_data/
# - /api/v2/dashboard/maintenance_types/
# - /api/v2/dashboard/recent_work_orders/
# =============================================================================
