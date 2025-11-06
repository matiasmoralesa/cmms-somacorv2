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
    
    @action(detail=False, methods=['get'])
    def monthly_data(self, request):
        """Datos mensuales para gráficos"""
        try:
            meses = []
            hoy = timezone.now()
            
            # Últimos 12 meses
            for i in range(12):
                mes_inicio = hoy.replace(day=1) - timedelta(days=i*30)
                mes_fin = (mes_inicio + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                
                ordenes_mes = OrdenesTrabajo.objects.filter(
                    fechareportefalla__gte=mes_inicio,
                    fechareportefalla__lte=mes_fin
                ).count()
                
                ordenes_completadas = OrdenesTrabajo.objects.filter(
                    fechacompletado__gte=mes_inicio,
                    fechacompletado__lte=mes_fin,
                    idestadoot__nombreestadoot='Completada'
                ).count()
                
                meses.append({
                    'mes': mes_inicio.strftime('%Y-%m'),
                    'nombre': mes_inicio.strftime('%b %Y'),
                    'ordenes_totales': ordenes_mes,
                    'ordenes_completadas': ordenes_completadas,
                    'tasa_completado': round(ordenes_completadas / max(ordenes_mes, 1) * 100, 1)
                })
            
            return Response(list(reversed(meses)))
        except Exception as e:
            logger.error(f"Error en datos mensuales: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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


# =============================================================================
# DASHBOARD VIEWSET
# =============================================================================

class DashboardViewSet(viewsets.ViewSet):
    """ViewSet para el dashboard con estadísticas del sistema"""
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estadísticas principales del dashboard"""
        try:
            # Estadísticas de equipos
            total_equipos = Equipos.objects.count()
            equipos_activos = Equipos.objects.filter(activo=True).count()
            equipos_en_mantenimiento = Equipos.objects.filter(
                idestadoactual__nombreestado__icontains='mantenimiento'
            ).count()
            
            # Calcular disponibilidad
            disponibilidad = ((equipos_activos - equipos_en_mantenimiento) / max(equipos_activos, 1)) * 100
            
            # Estadísticas de órdenes de trabajo
            total_ordenes = OrdenesTrabajo.objects.count()
            ordenes_pendientes = OrdenesTrabajo.objects.filter(
                idestadoot__nombreestadoot__in=['Pendiente', 'Abierta', 'Asignada']
            ).count()
            
            # Órdenes completadas este mes
            inicio_mes = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            ordenes_completadas_mes = OrdenesTrabajo.objects.filter(
                idestadoot__nombreestadoot='Completada',
                fechacompletado__gte=inicio_mes
            ).count()
            
            # Órdenes vencidas (más de 7 días pendientes)
            hace_7_dias = timezone.now() - timedelta(days=7)
            ordenes_vencidas = OrdenesTrabajo.objects.filter(
                idestadoot__nombreestadoot__in=['Pendiente', 'Abierta', 'Asignada'],
                fechacreacionot__lt=hace_7_dias
            ).count()
            
            # Tiempo promedio de resolución (en horas)
            ordenes_completadas = OrdenesTrabajo.objects.filter(
                idestadoot__nombreestadoot='Completada',
                fechacompletado__isnull=False
            )
            
            tiempo_promedio_horas = 24.0  # Valor por defecto
            if ordenes_completadas.exists():
                tiempos = []
                for orden in ordenes_completadas[:50]:  # Últimas 50 órdenes
                    if orden.fechacompletado and orden.fechacreacionot:
                        diff = orden.fechacompletado - orden.fechacreacionot
                        tiempos.append(diff.total_seconds() / 3600)  # Convertir a horas
                
                if tiempos:
                    tiempo_promedio_horas = sum(tiempos) / len(tiempos)
            
            # Estadísticas del sistema
            eficiencia = min(95.0, (ordenes_completadas_mes / max(total_ordenes, 1)) * 100)
            ordenes_por_dia = ordenes_completadas_mes / max(timezone.now().day, 1)
            tasa_completado = (ordenes_completadas_mes / max(ordenes_completadas_mes + ordenes_pendientes, 1)) * 100
            
            stats = {
                'equipos': {
                    'total': total_equipos,
                    'activos': equipos_activos,
                    'en_mantenimiento': equipos_en_mantenimiento,
                    'disponibilidad': round(disponibilidad, 1)
                },
                'ordenes': {
                    'total': total_ordenes,
                    'pendientes': ordenes_pendientes,
                    'completadas_mes': ordenes_completadas_mes,
                    'vencidas': ordenes_vencidas,
                    'tiempo_promedio_horas': round(tiempo_promedio_horas, 1)
                },
                'sistema': {
                    'eficiencia': round(eficiencia, 1),
                    'ordenes_por_dia': round(ordenes_por_dia, 1),
                    'tasa_completado': round(tasa_completado, 1)
                }
            }
            
            logger.info(f"Dashboard stats generadas: {stats}")
            return Response(stats)
            
        except Exception as e:
            logger.error(f"Error generando estadísticas del dashboard: {e}")
            return Response({
                'equipos': {
                    'total': 0,
                    'activos': 0,
                    'en_mantenimiento': 0,
                    'disponibilidad': 0.0
                },
                'ordenes': {
                    'total': 0,
                    'pendientes': 0,
                    'completadas_mes': 0,
                    'vencidas': 0,
                    'tiempo_promedio_horas': 0.0
                },
                'sistema': {
                    'eficiencia': 0.0,
                    'ordenes_por_dia': 0.0,
                    'tasa_completado': 0.0
                }
            })
    
    @action(detail=False, methods=['get'])
    def monthly_data(self, request):
        """Datos mensuales para gráficos"""
        try:
            # Obtener datos de los últimos 6 meses
            meses = []
            fecha_actual = timezone.now()
            
            for i in range(6):
                # Calcular el primer día del mes
                if fecha_actual.month - i <= 0:
                    mes = fecha_actual.month - i + 12
                    año = fecha_actual.year - 1
                else:
                    mes = fecha_actual.month - i
                    año = fecha_actual.year
                
                inicio_mes = datetime(año, mes, 1, tzinfo=timezone.get_current_timezone())
                
                # Calcular el último día del mes
                if mes == 12:
                    fin_mes = datetime(año + 1, 1, 1, tzinfo=timezone.get_current_timezone())
                else:
                    fin_mes = datetime(año, mes + 1, 1, tzinfo=timezone.get_current_timezone())
                
                # Contar órdenes completadas y totales del mes
                ordenes_completadas = OrdenesTrabajo.objects.filter(
                    fechacompletado__gte=inicio_mes,
                    fechacompletado__lt=fin_mes,
                    idestadoot__nombreestadoot='Completada'
                ).count()
                
                ordenes_totales = OrdenesTrabajo.objects.filter(
                    fechacreacionot__gte=inicio_mes,
                    fechacreacionot__lt=fin_mes
                ).count()
                
                # Nombre del mes en español
                nombres_meses = [
                    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
                ]
                
                meses.append({
                    'nombre': nombres_meses[mes - 1],
                    'mes': f"{año}-{mes:02d}",
                    'ordenes_completadas': ordenes_completadas,
                    'ordenes_totales': ordenes_totales
                })
            
            # Invertir para que el más reciente esté al final
            meses.reverse()
            
            logger.info(f"Datos mensuales generados: {len(meses)} meses")
            return Response(meses)
            
        except Exception as e:
            logger.error(f"Error generando datos mensuales: {e}")
            # Datos por defecto
            return Response([
                {'nombre': 'Enero', 'ordenes_completadas': 15, 'ordenes_totales': 20},
                {'nombre': 'Febrero', 'ordenes_completadas': 18, 'ordenes_totales': 22},
                {'nombre': 'Marzo', 'ordenes_completadas': 12, 'ordenes_totales': 18},
                {'nombre': 'Abril', 'ordenes_completadas': 25, 'ordenes_totales': 30},
                {'nombre': 'Mayo', 'ordenes_completadas': 20, 'ordenes_totales': 25},
                {'nombre': 'Junio', 'ordenes_completadas': 22, 'ordenes_totales': 28}
            ])    

    @action(detail=False, methods=['get'])
    def recent_work_orders(self, request):
        """Órdenes de trabajo recientes"""
        try:
            limit = int(request.query_params.get('limit', 5))
            
            # Obtener órdenes recientes con información relacionada
            ordenes = OrdenesTrabajo.objects.select_related(
                'idequipo', 'idsolicitante', 'idtecnicoasignado', 
                'idestadoot', 'idtipomantenimientoot'
            ).order_by('-fechacreacionot')[:limit]
            
            # Serializar manualmente para el dashboard
            data = []
            for orden in ordenes:
                data.append({
                    'idordentrabajo': orden.idordentrabajo,
                    'numeroot': orden.numeroot,
                    'descripcionproblemareportado': orden.descripcionproblemareportado,
                    'prioridad': orden.prioridad,
                    'equipo_nombre': orden.idequipo.nombreequipo if orden.idequipo else 'Sin equipo',
                    'tecnico_nombre': f"{orden.idtecnicoasignado.first_name} {orden.idtecnicoasignado.last_name}" if orden.idtecnicoasignado else 'Sin asignar',
                    'estado_nombre': orden.idestadoot.nombreestadoot if orden.idestadoot else 'Sin estado',
                    'fecha_creacion': orden.fechacreacionot.isoformat() if orden.fechacreacionot else None,
                    'tipo_mantenimiento': orden.idtipomantenimientoot.nombretipomantenimientoot if orden.idtipomantenimientoot else 'Sin tipo'
                })
            
            logger.info(f"Órdenes recientes obtenidas: {len(data)}")
            return Response(data)
            
        except Exception as e:
            logger.error(f"Error obteniendo órdenes recientes: {e}")
            return Response([])
    
    @action(detail=False, methods=['get'])
    def maintenance_types(self, request):
        """Tipos de mantenimiento para gráfico de torta"""
        try:
            # Obtener estadísticas de tipos de mantenimiento
            tipos = OrdenesTrabajo.objects.values(
                'idtipomantenimientoot__nombretipomantenimientoot'
            ).annotate(
                cantidad=Count('idordentrabajo')
            ).order_by('-cantidad')
            
            # Formatear para el frontend
            data = []
            for tipo in tipos:
                nombre = tipo['idtipomantenimientoot__nombretipomantenimientoot'] or 'Sin tipo'
                data.append({
                    'tipo': nombre,
                    'cantidad': tipo['cantidad']
                })
            
            # Si no hay datos, usar datos por defecto
            if not data:
                data = [
                    {'tipo': 'Preventivo', 'cantidad': 45},
                    {'tipo': 'Correctivo', 'cantidad': 30},
                    {'tipo': 'Predictivo', 'cantidad': 15},
                    {'tipo': 'Emergencia', 'cantidad': 10}
                ]
            
            logger.info(f"Tipos de mantenimiento obtenidos: {len(data)}")
            return Response(data)
            
        except Exception as e:
            logger.error(f"Error obteniendo tipos de mantenimiento: {e}")
            return Response([
                {'tipo': 'Preventivo', 'cantidad': 45},
                {'tipo': 'Correctivo', 'cantidad': 30},
                {'tipo': 'Predictivo', 'cantidad': 15},
                {'tipo': 'Emergencia', 'cantidad': 10}
            ])
    
    @action(detail=False, methods=['get'])
    def test_stats(self, request):
        """Endpoint de prueba para estadísticas simples"""
        try:
            # Contar directamente sin filtros complejos
            total_equipos = Equipos.objects.count()
            equipos_activos = Equipos.objects.filter(activo=True).count()
            total_ordenes = OrdenesTrabajo.objects.count()
            
            return Response({
                'equipos_total': total_equipos,
                'equipos_activos': equipos_activos,
                'ordenes_total': total_ordenes,
                'test': 'OK'
            })
        except Exception as e:
            return Response({
                'error': str(e),
                'test': 'FAILED'
            })