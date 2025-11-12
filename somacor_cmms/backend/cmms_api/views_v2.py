"""
Views V2 - Versión optimizada y moderna para CMMS
"""
from rest_framework import viewsets, filters, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
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


# InventarioViewSet movido al final del archivo con implementación completa
    
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



# =============================================================================
# VIEWSETS DE TÉCNICOS
# =============================================================================

class EspecialidadesViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar especialidades técnicas
    """
    queryset = Especialidades.objects.filter(activa=True)
    serializer_class = EspecialidadesSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por activas/inactivas
        activa = self.request.query_params.get('activa', None)
        if activa is not None:
            queryset = queryset.filter(activa=activa.lower() == 'true')
        
        return queryset.order_by('nombreespecialidad')


class TecnicosViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar técnicos del sistema
    
    Endpoints:
    - GET /api/v2/tecnicos/ - Listar todos los técnicos
    - GET /api/v2/tecnicos/{id}/ - Obtener detalle de un técnico
    - POST /api/v2/tecnicos/ - Crear nuevo técnico
    - PUT /api/v2/tecnicos/{id}/ - Actualizar técnico completo
    - PATCH /api/v2/tecnicos/{id}/ - Actualizar técnico parcial
    - DELETE /api/v2/tecnicos/{id}/ - Eliminar técnico
    - GET /api/v2/tecnicos/disponibles/ - Listar técnicos disponibles
    - PATCH /api/v2/tecnicos/{id}/cambiar_estado/ - Cambiar estado del técnico
    """
    queryset = Tecnicos.objects.select_related('usuario').prefetch_related('especialidades').filter(activo=True)
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TecnicosListSerializer
        elif self.action == 'retrieve':
            return TecnicosDetailSerializer
        else:
            return TecnicosCreateUpdateSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por estado
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)
        
        # Filtrar por especialidad
        especialidad = self.request.query_params.get('especialidad', None)
        if especialidad:
            queryset = queryset.filter(especialidades__idespecialidad=especialidad)
        
        # Filtrar por activos/inactivos
        activo = self.request.query_params.get('activo', None)
        if activo is not None:
            queryset = queryset.filter(activo=activo.lower() == 'true')
        
        # Búsqueda por nombre
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                models.Q(usuario__first_name__icontains=search) |
                models.Q(usuario__last_name__icontains=search) |
                models.Q(usuario__username__icontains=search) |
                models.Q(cargo__icontains=search)
            )
        
        return queryset.order_by('usuario__first_name', 'usuario__last_name')
    
    @action(detail=False, methods=['get'])
    def disponibles(self, request):
        """
        Endpoint para obtener solo técnicos disponibles
        GET /api/v2/tecnicos/disponibles/
        """
        tecnicos = self.get_queryset().filter(estado='disponible')
        serializer = self.get_serializer(tecnicos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def cambiar_estado(self, request, pk=None):
        """
        Endpoint para cambiar el estado de un técnico
        PATCH /api/v2/tecnicos/{id}/cambiar_estado/
        Body: {"estado": "disponible|ocupado|no_disponible"}
        """
        tecnico = self.get_object()
        nuevo_estado = request.data.get('estado')
        
        if nuevo_estado not in ['disponible', 'ocupado', 'no_disponible']:
            return Response(
                {'error': 'Estado inválido. Debe ser: disponible, ocupado o no_disponible'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tecnico.estado = nuevo_estado
        tecnico.save()
        
        serializer = self.get_serializer(tecnico)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Endpoint para obtener estadísticas de técnicos
        GET /api/v2/tecnicos/estadisticas/
        """
        total = self.get_queryset().count()
        disponibles = self.get_queryset().filter(estado='disponible').count()
        ocupados = self.get_queryset().filter(estado='ocupado').count()
        no_disponibles = self.get_queryset().filter(estado='no_disponible').count()
        
        # Calcular total de órdenes activas
        from django.db.models import Q, Count
        ordenes_activas = OrdenesTrabajo.objects.filter(
            Q(idestadoot__nombreestadoot='Abierta') |
            Q(idestadoot__nombreestadoot='En Progreso') |
            Q(idestadoot__nombreestadoot='Asignada')
        ).count()
        
        return Response({
            'total': total,
            'disponibles': disponibles,
            'ocupados': ocupados,
            'no_disponibles': no_disponibles,
            'ordenes_activas_total': ordenes_activas
        })



# =============================================================================
# VIEWSETS ADICIONALES - GESTIÓN DE CATÁLOGOS
# =============================================================================

class EstadosEquipoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar estados de equipos
    """
    queryset = EstadosEquipo.objects.all()
    serializer_class = EstadosEquipoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return self.queryset.order_by('nombreestado')


class EstadosOrdenTrabajoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar estados de órdenes de trabajo
    """
    queryset = EstadosOrdenTrabajo.objects.all()
    serializer_class = EstadosOrdenTrabajoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return self.queryset.order_by('nombreestadoot')


class TiposMantenimientoOTViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar tipos de mantenimiento de OT
    """
    queryset = TiposMantenimientoOT.objects.all()
    serializer_class = TiposMantenimientoOTSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return self.queryset.order_by('nombretipomantenimientoot')


class TiposTareaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar tipos de tarea
    """
    queryset = TiposTarea.objects.all()
    serializer_class = TipoTareaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return self.queryset.order_by('nombretipotarea')


class TareasEstandarViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar tareas estándar
    """
    queryset = TareasEstandar.objects.select_related('idtipotarea').all()
    serializer_class = TareasEstandarSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['idtipotarea']
    search_fields = ['nombretarea', 'descripciontarea']
    
    def get_queryset(self):
        return self.queryset.order_by('nombretarea')


# =============================================================================
# VIEWSETS DE PLANES DE MANTENIMIENTO
# =============================================================================

class PlanesMantenimientoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar planes de mantenimiento
    """
    queryset = PlanesMantenimiento.objects.all()
    serializer_class = PlanesMantenimientoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['nombreplan', 'descripcionplan']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por equipo si se proporciona
        equipo_id = self.request.query_params.get('equipo', None)
        if equipo_id:
            queryset = queryset.filter(idequipo_id=equipo_id)
        
        return queryset.order_by('nombreplan')
    
    @action(detail=True, methods=['get'])
    def detalles(self, request, pk=None):
        """
        Obtener detalles del plan con sus tareas
        """
        plan = self.get_object()
        detalles = DetallesPlanMantenimiento.objects.filter(
            idplanmantenimiento=plan
        ).select_related('idtareaestandar')
        
        serializer = DetallesPlanMantenimientoSerializer(detalles, many=True)
        return Response(serializer.data)


class DetallesPlanMantenimientoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar detalles de planes de mantenimiento
    """
    queryset = DetallesPlanMantenimiento.objects.select_related(
        'idplanmantenimiento', 'idtareaestandar'
    ).all()
    serializer_class = DetallesPlanMantenimientoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['idplanmantenimiento']
    
    def get_queryset(self):
        return self.queryset.order_by('iddetalleplan')


# =============================================================================
# VIEWSETS DE ACTIVIDADES Y EVIDENCIAS
# =============================================================================

class ActividadesOrdenTrabajoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar actividades de órdenes de trabajo
    """
    queryset = ActividadesOrdenTrabajo.objects.select_related(
        'idordentrabajo', 'idtareaestandar', 'idtecnicoejecutor'
    ).all()
    serializer_class = ActividadesOrdenTrabajoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['idordentrabajo', 'idtecnicoejecutor', 'completada']
    search_fields = ['observacionesactividad']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por orden de trabajo
        orden_id = self.request.query_params.get('orden', None)
        if orden_id:
            queryset = queryset.filter(idordentrabajo_id=orden_id)
        
        # Filtrar por técnico
        tecnico_id = self.request.query_params.get('tecnico', None)
        if tecnico_id:
            queryset = queryset.filter(idtecnicoejecutor_id=tecnico_id)
        
        # Filtrar por estado completada
        completada = self.request.query_params.get('completada', None)
        if completada is not None:
            queryset = queryset.filter(completada=completada.lower() == 'true')
        
        return queryset.order_by('-fechainicioactividad')
    
    @action(detail=False, methods=['get'])
    def por_orden(self, request):
        """
        Obtener actividades de una orden específica
        """
        orden_id = request.query_params.get('orden_id')
        if not orden_id:
            return Response(
                {'error': 'Se requiere el parámetro orden_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        actividades = self.get_queryset().filter(idordentrabajo_id=orden_id)
        serializer = self.get_serializer(actividades, many=True)
        return Response(serializer.data)


class EvidenciaOTViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar evidencias de órdenes de trabajo
    """
    queryset = EvidenciaOT.objects.select_related(
        'idordentrabajo'
    ).all()
    serializer_class = EvidenciaOTSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['idordentrabajo']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por orden de trabajo
        orden_id = self.request.query_params.get('orden', None)
        if orden_id:
            queryset = queryset.filter(idordentrabajo_id=orden_id)
        
        return queryset.order_by('-fecha_subida')


# =============================================================================
# VIEWSETS DE AGENDAS
# =============================================================================

class AgendasViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar agendas de mantenimiento
    """
    queryset = Agendas.objects.select_related(
        'idplanmantenimiento', 'idequipo', 'idusuarioasignado'
    ).all()
    serializer_class = AgendaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['idequipo', 'idusuarioasignado', 'tipoevento']
    search_fields = ['tituloevento', 'descripcionevento']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por equipo
        equipo_id = self.request.query_params.get('equipo', None)
        if equipo_id:
            queryset = queryset.filter(idequipo_id=equipo_id)
        
        # Filtrar por usuario asignado
        usuario_id = self.request.query_params.get('usuario', None)
        if usuario_id:
            queryset = queryset.filter(idusuarioasignado_id=usuario_id)
        
        # Filtrar por tipo de evento
        tipo_evento = self.request.query_params.get('tipo', None)
        if tipo_evento:
            queryset = queryset.filter(tipoevento=tipo_evento)
        
        # Filtrar por rango de fechas
        fecha_desde = self.request.query_params.get('fecha_desde', None)
        fecha_hasta = self.request.query_params.get('fecha_hasta', None)
        
        if fecha_desde:
            queryset = queryset.filter(fechahorainicio__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fechahorainicio__lte=fecha_hasta)
        
        return queryset.order_by('fechahorainicio')
    
    @action(detail=False, methods=['get'])
    def proximas(self, request):
        """
        Obtener agendas próximas (próximos 7 días)
        """
        from datetime import date, timedelta
        
        hoy = date.today()
        fecha_limite = hoy + timedelta(days=7)
        
        agendas = self.get_queryset().filter(
            fechaprogramada__gte=hoy,
            fechaprogramada__lte=fecha_limite,
            estado='Pendiente'
        )
        
        serializer = self.get_serializer(agendas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def vencidas(self, request):
        """
        Obtener agendas vencidas
        """
        from datetime import date
        
        hoy = date.today()
        agendas = self.get_queryset().filter(
            fechaprogramada__lt=hoy,
            estado='Pendiente'
        )
        
        serializer = self.get_serializer(agendas, many=True)
        return Response(serializer.data)



# =============================================================================
# VIEWSETS DE INVENTARIO
# =============================================================================

class CategoriasInventarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar categorías de inventario
    """
    queryset = CategoriasInventario.objects.filter(activa=True)
    serializer_class = CategoriasInventarioSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['nombrecategoria', 'descripcion']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por activas/inactivas
        activa = self.request.query_params.get('activa', None)
        if activa is not None:
            queryset = queryset.filter(activa=activa.lower() == 'true')
        
        return queryset.order_by('nombrecategoria')


class ProveedoresViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar proveedores
    """
    queryset = Proveedores.objects.filter(activo=True)
    serializer_class = ProveedoresSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['nombreproveedor', 'rut', 'contacto', 'email']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por activos/inactivos
        activo = self.request.query_params.get('activo', None)
        if activo is not None:
            queryset = queryset.filter(activo=activo.lower() == 'true')
        
        return queryset.order_by('nombreproveedor')


class InventarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar items de inventario
    
    Endpoints:
    - GET /api/v2/inventario/ - Listar todos los items
    - GET /api/v2/inventario/{id}/ - Obtener detalle de un item
    - POST /api/v2/inventario/ - Crear nuevo item
    - PUT /api/v2/inventario/{id}/ - Actualizar item completo
    - PATCH /api/v2/inventario/{id}/ - Actualizar item parcial
    - DELETE /api/v2/inventario/{id}/ - Eliminar item
    - GET /api/v2/inventario/stock_bajo/ - Items con stock bajo
    - GET /api/v2/inventario/sin_stock/ - Items sin stock
    - GET /api/v2/inventario/estadisticas/ - Estadísticas generales
    - POST /api/v2/inventario/{id}/movimiento/ - Registrar movimiento
    """
    queryset = Inventario.objects.select_related(
        'idcategoria', 'idproveedor', 'usuariocreacion'
    ).filter(estado='activo')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['idcategoria', 'idproveedor', 'estado', 'unidadmedida']
    search_fields = ['codigointerno', 'codigobarras', 'nombreitem', 'descripcion']
    ordering_fields = ['codigointerno', 'nombreitem', 'cantidad', 'costounitario', 'fechacreacion']
    ordering = ['codigointerno']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return InventarioListSerializer
        elif self.action == 'retrieve':
            return InventarioDetailSerializer
        else:
            return InventarioCreateUpdateSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por estado de stock
        estado_stock = self.request.query_params.get('estado_stock', None)
        if estado_stock == 'stock_bajo':
            queryset = queryset.extra(
                where=["cantidad <= stockminimo"]
            )
        elif estado_stock == 'sin_stock':
            queryset = queryset.filter(cantidad=0)
        elif estado_stock == 'stock_alto':
            queryset = queryset.extra(
                where=["stockmaximo IS NOT NULL AND cantidad >= stockmaximo"]
            )
        
        # Filtrar por rango de cantidad
        cantidad_min = self.request.query_params.get('cantidad_min', None)
        cantidad_max = self.request.query_params.get('cantidad_max', None)
        if cantidad_min:
            queryset = queryset.filter(cantidad__gte=cantidad_min)
        if cantidad_max:
            queryset = queryset.filter(cantidad__lte=cantidad_max)
        
        # Filtrar por rango de costo
        costo_min = self.request.query_params.get('costo_min', None)
        costo_max = self.request.query_params.get('costo_max', None)
        if costo_min:
            queryset = queryset.filter(costounitario__gte=costo_min)
        if costo_max:
            queryset = queryset.filter(costounitario__lte=costo_max)
        
        return queryset
    
    def perform_create(self, serializer):
        """Asignar el usuario actual al crear item"""
        serializer.save(usuariocreacion=self.request.user)
    
    @action(detail=False, methods=['get'])
    def stock_bajo(self, request):
        """
        Endpoint para obtener items con stock bajo
        GET /api/v2/inventario/stock_bajo/
        """
        items = self.get_queryset().extra(
            where=["cantidad <= stockminimo AND cantidad > 0"]
        )
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def sin_stock(self, request):
        """
        Endpoint para obtener items sin stock
        GET /api/v2/inventario/sin_stock/
        """
        items = self.get_queryset().filter(cantidad=0)
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Endpoint para obtener estadísticas de inventario
        GET /api/v2/inventario/estadisticas/
        """
        from django.db.models import Sum, Count, Q
        
        queryset = self.get_queryset()
        
        # Calcular estadísticas
        total_items = queryset.count()
        items_activos = queryset.filter(estado='activo').count()
        items_stock_bajo = queryset.extra(
            where=["cantidad <= stockminimo AND cantidad > 0"]
        ).count()
        items_sin_stock = queryset.filter(cantidad=0).count()
        
        # Calcular valor total del inventario
        valor_total = 0
        for item in queryset:
            valor_total += item.valor_total
        
        # Contar categorías y proveedores
        categorias_count = CategoriasInventario.objects.filter(activa=True).count()
        proveedores_count = Proveedores.objects.filter(activo=True).count()
        
        stats = {
            'total_items': total_items,
            'items_activos': items_activos,
            'items_stock_bajo': items_stock_bajo,
            'items_sin_stock': items_sin_stock,
            'valor_total_inventario': valor_total,
            'categorias_count': categorias_count,
            'proveedores_count': proveedores_count
        }
        
        serializer = InventarioStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def movimiento(self, request, pk=None):
        """
        Endpoint para registrar un movimiento de inventario
        POST /api/v2/inventario/{id}/movimiento/
        Body: {
            "tipomovimiento": "entrada|salida|ajuste_positivo|ajuste_negativo",
            "cantidad": 10,
            "motivo": "Compra de repuestos",
            "observaciones": "Factura #12345",
            "documento": "FAC-12345",
            "idproveedor": 1
        }
        """
        item = self.get_object()
        
        # Validar datos del movimiento
        tipo_movimiento = request.data.get('tipomovimiento')
        cantidad = request.data.get('cantidad', 0)
        
        if not tipo_movimiento:
            return Response(
                {'error': 'El tipo de movimiento es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cantidad = float(cantidad)
        except (ValueError, TypeError):
            return Response(
                {'error': 'La cantidad debe ser un número válido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calcular nueva cantidad
        cantidad_anterior = float(item.cantidad)
        
        if tipo_movimiento in ['entrada', 'ajuste_positivo']:
            cantidad_nueva = cantidad_anterior + cantidad
        elif tipo_movimiento in ['salida', 'ajuste_negativo']:
            cantidad_nueva = cantidad_anterior - cantidad
            if cantidad_nueva < 0:
                return Response(
                    {'error': 'No hay suficiente stock para realizar esta operación'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {'error': 'Tipo de movimiento no válido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear el movimiento
        movimiento = MovimientosInventario.objects.create(
            idinventario=item,
            tipomovimiento=tipo_movimiento,
            cantidad=cantidad,
            cantidadanterior=cantidad_anterior,
            cantidadnueva=cantidad_nueva,
            motivo=request.data.get('motivo', ''),
            observaciones=request.data.get('observaciones', ''),
            documento=request.data.get('documento', ''),
            idproveedor_id=request.data.get('idproveedor'),
            idordentrabajo_id=request.data.get('idordentrabajo'),
            usuariomovimiento=request.user
        )
        
        # Actualizar la cantidad del item
        item.cantidad = cantidad_nueva
        item.save()
        
        # Serializar y retornar
        serializer = MovimientosInventarioSerializer(movimiento)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MovimientosInventarioViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para consultar movimientos de inventario (solo lectura)
    """
    queryset = MovimientosInventario.objects.select_related(
        'idinventario', 'usuariomovimiento', 'idproveedor', 'idordentrabajo'
    ).all()
    serializer_class = MovimientosInventarioSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['idinventario', 'tipomovimiento', 'idproveedor', 'idordentrabajo']
    ordering = ['-fechamovimiento']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por item de inventario
        item_id = self.request.query_params.get('item', None)
        if item_id:
            queryset = queryset.filter(idinventario_id=item_id)
        
        # Filtrar por tipo de movimiento
        tipo = self.request.query_params.get('tipo', None)
        if tipo:
            queryset = queryset.filter(tipomovimiento=tipo)
        
        # Filtrar por rango de fechas
        fecha_desde = self.request.query_params.get('fecha_desde', None)
        fecha_hasta = self.request.query_params.get('fecha_hasta', None)
        
        if fecha_desde:
            queryset = queryset.filter(fechamovimiento__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fechamovimiento__lte=fecha_hasta)
        
        return queryset
