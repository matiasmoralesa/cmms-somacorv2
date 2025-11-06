# cmms_api/views_checklist.py
# Vistas especializadas para el módulo de checklist

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from django.db import transaction
from django.db.models import Q, Count
from .models import *
from .serializers_v2 import *
import datetime
import json

class ChecklistWorkflowViewSet(viewsets.ViewSet):
    """
    ViewSet para manejar el flujo completo de checklists
    """
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['get'], url_path='templates-por-equipo/(?P<equipo_id>[^/.]+)')
    def templates_por_equipo(self, request, equipo_id=None):
        """
        Retorna las plantillas de checklist disponibles para un equipo específico
        """
        try:
            equipo = Equipos.objects.get(idequipo=equipo_id)
            templates = ChecklistTemplate.objects.filter(
                tipo_equipo=equipo.idtipoequipo,
                activo=True
            ).prefetch_related('categories__items')
            
            return Response({
                'equipo': {
                    'idequipo': equipo.idequipo,
                    'nombreequipo': equipo.nombreequipo,
                    'codigointerno': equipo.codigointerno,
                    'tipo_equipo': equipo.idtipoequipo.nombretipo
                },
                'templates': [{
                    'id_template': t.id_template,
                    'nombre': t.nombre,
                    'tipo_equipo_nombre': t.tipo_equipo.nombretipo,
                    'activo': t.activo,
                    'categories': [{
                        'id_category': cat.id_category,
                        'nombre': cat.nombre,
                        'orden': cat.orden,
                        'items': [{
                            'id_item': item.id_item,
                            'texto': item.texto,
                            'es_critico': item.es_critico,
                            'orden': item.orden
                        } for item in cat.items.all().order_by('orden')]
                    } for cat in t.categories.all().order_by('orden')]
                } for t in templates]
            })
            
        except Equipos.DoesNotExist:
            return Response(
                {'error': 'Equipo no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'], url_path='completar-checklist')
    def completar_checklist(self, request):
        """
        Completa un checklist y analiza los resultados para generar alertas.
        """
        # Copiamos los datos para poder modificarlos.
        data = request.data.copy()

        # El campo 'answers' viene como un string JSON, lo convertimos a un objeto Python.
        if 'answers' in data and isinstance(data['answers'], str):
            try:
                data['answers'] = json.loads(data['answers'])
            except json.JSONDecodeError:
                return Response({'error': 'Formato de "answers" inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        # Pasamos los datos modificados al serializador.
        serializer = ChecklistInstanceSerializer(data=data, context={'request': request})

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    instance = serializer.save()
                    # Análisis de respuestas y creación de OT
                    alertas = self._analizar_respuestas_criticas(instance)
                    
                    if alertas.get('elementos_criticos_malos'):
                        ot_creada = self._crear_ot_correctiva_desde_checklist(instance, alertas)
                        alertas['ot_creada'] = ot_creada
                    
                    # Devolvemos la instancia serializada
                    response_data = ChecklistInstanceSerializer(instance).data
                    response_data['alertas'] = alertas
                    
                    return Response(response_data, status=status.HTTP_201_CREATED)
                    
            except Exception as e:
                return Response(
                    {'error': f'Error al procesar checklist: {str(e)}'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _analizar_respuestas_criticas(self, instance):
        """
        Analiza las respuestas del checklist para identificar elementos críticos en mal estado
        """
        respuestas_malas = instance.answers.filter(estado='malo')
        elementos_criticos_malos = []
        elementos_no_criticos_malos = []
        
        for respuesta in respuestas_malas:
            if respuesta.item.es_critico:
                elementos_criticos_malos.append({
                    'item': respuesta.item.texto,
                    'categoria': respuesta.item.category.nombre,
                    'observacion': respuesta.observacion_item
                })
            else:
                elementos_no_criticos_malos.append({
                    'item': respuesta.item.texto,
                    'categoria': respuesta.item.category.nombre,
                    'observacion': respuesta.observacion_item
                })
        
        return {
            'elementos_criticos_malos': elementos_criticos_malos,
            'elementos_no_criticos_malos': elementos_no_criticos_malos,
            'requiere_atencion_inmediata': len(elementos_criticos_malos) > 0,
            'total_elementos_malos': len(elementos_criticos_malos) + len(elementos_no_criticos_malos)
        }

    def _crear_ot_correctiva_desde_checklist(self, instance, alertas):
        """
        Crea una orden de trabajo correctiva basada en los elementos críticos fallidos del checklist
        """
        try:
            # Obtener tipos y estados necesarios
            tipo_correctivo = TiposMantenimientoOT.objects.get_or_create(
                nombretipomantenimientoot='Correctivo',
                defaults={'descripcion': 'Mantenimiento por falla no planificada'}
            )[0]
            
            estado_abierta = EstadosOrdenTrabajo.objects.get_or_create(
                nombreestadoot='Abierta',
                defaults={'descripcion': 'OT recién creada'}
            )[0]
            
            # Crear descripción del problema
            elementos_criticos = [item['item'] for item in alertas['elementos_criticos_malos']]
            descripcion = (
                f"Fallas críticas detectadas en checklist diario del {instance.fecha_inspeccion}:\n"
                f"- {chr(10).join(elementos_criticos)}\n\n"
                f"Operador: {instance.operador.get_full_name()}\n"
                f"Lugar: {instance.lugar_inspeccion or 'No especificado'}\n"
                f"Horómetro: {instance.horometro_inspeccion}h"
            )
            
            # Crear la OT
            ot = OrdenesTrabajo.objects.create(
                numeroot=f"OT-CHK-{instance.equipo.codigointerno or instance.equipo.idequipo}-{timezone.now().strftime('%Y%m%d%H%M')}",
                idequipo=instance.equipo,
                idtipomantenimientoot=tipo_correctivo,
                idestadoot=estado_abierta,
                descripcionproblemareportado=descripcion,
                fechareportefalla=timezone.now(),
                idsolicitante=instance.operador,
                horometro=instance.horometro_inspeccion,
                prioridad='Crítica'
            )
            
            # Crear actividades para cada elemento crítico fallido
            for elemento in alertas['elementos_criticos_malos']:
                ActividadesOrdenTrabajo.objects.create(
                    idordentrabajo=ot,
                    descripcionactividad=f"Revisar y reparar: {elemento['item']}",
                    observacionesactividad=elemento['observacion'] or 'Detectado en checklist diario',
                    tiempoestimadominutos=60  # Tiempo estimado por defecto
                )
            
            return {
                'numero_ot': ot.numeroot,
                'id_ot': ot.idordentrabajo,
                'mensaje': f'OT correctiva creada automáticamente: {ot.numeroot}'
            }
            
        except Exception as e:
            return {
                'error': f'Error al crear OT correctiva: {str(e)}'
            }

    @action(detail=False, methods=['get'], url_path='historial-equipo/(?P<equipo_id>[^/.]+)')
    def historial_equipo(self, request, equipo_id=None):
        """
        Retorna el historial de checklists de un equipo
        """
        try:
            equipo = Equipos.objects.get(idequipo=equipo_id)
            
            # Parámetros de filtrado
            fecha_inicio = request.query_params.get('fecha_inicio')
            fecha_fin = request.query_params.get('fecha_fin')
            
            queryset = ChecklistInstance.objects.filter(equipo=equipo)
            
            if fecha_inicio:
                queryset = queryset.filter(fecha_inspeccion__gte=fecha_inicio)
            if fecha_fin:
                queryset = queryset.filter(fecha_inspeccion__lte=fecha_fin)
            
            queryset = queryset.order_by('-fecha_inspeccion')
            
            # Estadísticas del período
            total_checklists = queryset.count()
            checklists_con_fallas = queryset.filter(
                answers__estado='malo'
            ).distinct().count()
            
            checklists_con_fallas_criticas = queryset.filter(
                answers__estado='malo',
                answers__item__es_critico=True
            ).distinct().count()
            
            return Response({
                'equipo': {
                    'idequipo': equipo.idequipo,
                    'nombreequipo': equipo.nombreequipo,
                    'codigointerno': equipo.codigointerno,
                    'tipo_equipo': equipo.idtipoequipo.nombretipo
                },
                'estadisticas': {
                    'total_checklists': total_checklists,
                    'checklists_con_fallas': checklists_con_fallas,
                    'checklists_con_fallas_criticas': checklists_con_fallas_criticas,
                    'porcentaje_conformidad': round(
                        ((total_checklists - checklists_con_fallas) / total_checklists * 100) 
                        if total_checklists > 0 else 0, 2
                    )
                },
                'historial': ChecklistInstanceSerializer(queryset[:50], many=True).data  # Últimos 50
            })
            
        except Equipos.DoesNotExist:
            return Response(
                {'error': 'Equipo no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'], url_path='reportes/conformidad')
    def reporte_conformidad(self, request):
        """
        Genera reporte de conformidad de checklists por período
        """
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        tipo_equipo_id = request.query_params.get('tipo_equipo')
        
        if not fecha_inicio or not fecha_fin:
            fecha_fin = timezone.now().date()
            fecha_inicio = fecha_fin - datetime.timedelta(days=30)
        
        queryset = ChecklistInstance.objects.filter(
            fecha_inspeccion__range=[fecha_inicio, fecha_fin]
        )
        
        if tipo_equipo_id:
            queryset = queryset.filter(equipo__idtipoequipo_id=tipo_equipo_id)
        
        # Conformidad por equipo
        conformidad_por_equipo = {}
        for instance in queryset:
            equipo_key = f"{instance.equipo.nombreequipo} ({instance.equipo.codigointerno})"
            
            if equipo_key not in conformidad_por_equipo:
                conformidad_por_equipo[equipo_key] = {
                    'total_checklists': 0,
                    'checklists_conformes': 0,
                    'fallas_criticas': 0,
                    'fallas_no_criticas': 0
                }
            
            conformidad_por_equipo[equipo_key]['total_checklists'] += 1
            
            # Verificar si tiene fallas
            fallas_criticas = instance.answers.filter(
                estado='malo', 
                item__es_critico=True
            ).count()
            
            fallas_no_criticas = instance.answers.filter(
                estado='malo', 
                item__es_critico=False
            ).count()
            
            conformidad_por_equipo[equipo_key]['fallas_criticas'] += fallas_criticas
            conformidad_por_equipo[equipo_key]['fallas_no_criticas'] += fallas_no_criticas
            
            # Si no tiene fallas críticas, se considera conforme
            if fallas_criticas == 0:
                conformidad_por_equipo[equipo_key]['checklists_conformes'] += 1
        
        # Calcular porcentajes
        for equipo_data in conformidad_por_equipo.values():
            total = equipo_data['total_checklists']
            if total > 0:
                equipo_data['porcentaje_conformidad'] = round(
                    (equipo_data['checklists_conformes'] / total) * 100, 2
                )
            else:
                equipo_data['porcentaje_conformidad'] = 0

        return Response({
            'periodo': {
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin
            },
            'total_checklists_periodo': queryset.count(),
            'conformidad_por_equipo': conformidad_por_equipo
        })

    @action(detail=False, methods=['get'], url_path='elementos-mas-fallidos')
    def elementos_mas_fallidos(self, request):
        """
        Retorna los elementos de checklist que más fallan
        """
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        
        if not fecha_inicio or not fecha_fin:
            fecha_fin = timezone.now().date()
            fecha_inicio = fecha_fin - datetime.timedelta(days=30)
        
        # Buscar respuestas "malo" en el período
        respuestas_malas = ChecklistAnswer.objects.filter(
            estado='malo',
            instance__fecha_inspeccion__range=[fecha_inicio, fecha_fin]
        ).select_related('item', 'item__category')
        
        # Agrupar por elemento
        elementos_fallidos = {}
        for respuesta in respuestas_malas:
            item_key = f"{respuesta.item.category.nombre} - {respuesta.item.texto}"
            
            if item_key not in elementos_fallidos:
                elementos_fallidos[item_key] = {
                    'elemento': respuesta.item.texto,
                    'categoria': respuesta.item.category.nombre,
                    'es_critico': respuesta.item.es_critico,
                    'cantidad_fallas': 0,
                    'equipos_afectados': set()
                }
            
            elementos_fallidos[item_key]['cantidad_fallas'] += 1
            elementos_fallidos[item_key]['equipos_afectados'].add(
                respuesta.instance.equipo.nombreequipo
            )
        
        # Convertir sets a listas y ordenar por cantidad de fallas
        resultado = []
        for item_data in elementos_fallidos.values():
            item_data['equipos_afectados'] = list(item_data['equipos_afectados'])
            item_data['cantidad_equipos_afectados'] = len(item_data['equipos_afectados'])
            resultado.append(item_data)
        
        resultado.sort(key=lambda x: x['cantidad_fallas'], reverse=True)
        
        return Response({
            'periodo': {
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin
            },
            'elementos_mas_fallidos': resultado[:20]  # Top 20
        })