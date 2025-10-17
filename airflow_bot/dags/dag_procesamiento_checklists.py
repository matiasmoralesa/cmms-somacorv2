"""
DAG de Procesamiento de Checklists
Analiza checklists completados diariamente y genera acciones correctivas
"""

from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.utils.dates import days_ago
import sys
from pathlib import Path
import pandas as pd
from typing import Dict, List

# Agregar directorios al path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.airflow_config import (
    ScheduleConfig,
    BusinessLogicConfig,
    CMSSConfig
)
from scripts.cmms_api_client import CMSSAPIClient

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'telegram_integration'))
from notifications.telegram_notifier import TelegramNotifier

# Configuración por defecto del DAG
default_args = {
    'owner': 'cmms_bot',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}


@dag(
    dag_id='procesamiento_checklists_diario',
    default_args=default_args,
    description='Procesamiento diario de checklists completados',
    schedule=ScheduleConfig.DAG_CHECKLISTS,
    start_date=days_ago(1),
    catchup=False,
    tags=['cmms', 'checklists', 'correctivo'],
)
def procesamiento_checklists_dag():
    """
    DAG para procesamiento de checklists completados
    
    Flujo:
    1. Obtener checklists completados del día anterior
    2. Analizar items fallidos
    3. Identificar items críticos
    4. Generar órdenes de trabajo correctivas
    5. Notificar a supervisores
    """
    
    @task
    def get_completed_checklists() -> List[Dict]:
        """
        Obtener checklists completados del día anterior
        
        Returns:
            Lista de checklists completados
        """
        client = CMSSAPIClient()
        
        # Calcular rango de fechas (día anterior)
        fecha_fin = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_inicio = fecha_fin - timedelta(days=1)
        
        try:
            # Obtener todas las instancias de checklist
            checklists = client.get_checklist_instances()
            
            # Filtrar por fecha (si la API lo soporta)
            # Por ahora, obtener todos y filtrar localmente
            df_checklists = pd.DataFrame(checklists)
            
            if df_checklists.empty:
                print("⚠️ No se encontraron checklists")
                return []
            
            # Convertir fecha
            if 'fecha_completado' in df_checklists.columns:
                df_checklists['fecha_completado'] = pd.to_datetime(
                    df_checklists['fecha_completado'],
                    errors='coerce'
                )
                
                # Filtrar por día anterior
                mask = (
                    (df_checklists['fecha_completado'] >= fecha_inicio) &
                    (df_checklists['fecha_completado'] < fecha_fin)
                )
                checklists_dia = df_checklists[mask].to_dict('records')
            else:
                # Si no hay campo de fecha, tomar todos
                checklists_dia = checklists
            
            print(f"✅ Obtenidos {len(checklists_dia)} checklists del día anterior")
            return checklists_dia
            
        except Exception as e:
            print(f"❌ Error al obtener checklists: {str(e)}")
            return []
    
    @task
    def analyze_checklist_items(checklists: List[Dict]) -> List[Dict]:
        """
        Analizar items de checklists para identificar fallidos
        
        Args:
            checklists: Lista de checklists completados
        
        Returns:
            Lista de checklists con análisis de items
        """
        client = CMSSAPIClient()
        checklists_analizados = []
        
        for checklist in checklists:
            checklist_id = checklist.get('id') or checklist.get('idchecklist')
            
            if not checklist_id:
                continue
            
            try:
                # Obtener detalles completos del checklist
                checklist_detalle = client.get_checklist_instance(checklist_id)
                
                # Analizar items
                items = checklist_detalle.get('items', [])
                items_fallidos = []
                items_criticos_fallidos = []
                
                for item in items:
                    # Verificar si el item falló
                    estado = item.get('estado') or item.get('resultado')
                    es_critico = item.get('es_critico', False) or item.get('criticidad') == 'ALTA'
                    
                    # Considerar fallido si estado es False, "NO", "FAIL", etc.
                    if estado in [False, 'NO', 'FAIL', 'Fallido', 0]:
                        items_fallidos.append(item)
                        
                        if es_critico:
                            items_criticos_fallidos.append(item)
                
                # Agregar análisis al checklist
                checklist_analizado = {
                    'checklist_id': checklist_id,
                    'equipo_id': checklist_detalle.get('idequipo'),
                    'equipo_nombre': checklist_detalle.get('equipo_nombre', 'N/A'),
                    'template_id': checklist_detalle.get('idtemplate'),
                    'template_nombre': checklist_detalle.get('template_nombre', 'N/A'),
                    'fecha_completado': checklist.get('fecha_completado'),
                    'completado_por': checklist_detalle.get('completado_por', 'N/A'),
                    'total_items': len(items),
                    'items_fallidos': len(items_fallidos),
                    'items_criticos_fallidos': len(items_criticos_fallidos),
                    'items_fallidos_detalle': items_fallidos,
                    'items_criticos_detalle': items_criticos_fallidos,
                    'requiere_accion': len(items_criticos_fallidos) > 0
                }
                
                checklists_analizados.append(checklist_analizado)
                
                print(f"✅ Checklist {checklist_id}: {len(items_fallidos)} items fallidos, {len(items_criticos_fallidos)} críticos")
                
            except Exception as e:
                print(f"❌ Error al analizar checklist {checklist_id}: {str(e)}")
        
        print(f"✅ Analizados {len(checklists_analizados)} checklists")
        return checklists_analizados
    
    @task
    def identify_critical_issues(checklists_analizados: List[Dict]) -> List[Dict]:
        """
        Identificar checklists con problemas críticos
        
        Args:
            checklists_analizados: Lista de checklists analizados
        
        Returns:
            Lista de checklists con problemas críticos
        """
        checklists_criticos = [
            c for c in checklists_analizados 
            if c['requiere_accion']
        ]
        
        # Ordenar por cantidad de items críticos fallidos
        checklists_criticos.sort(
            key=lambda x: x['items_criticos_fallidos'],
            reverse=True
        )
        
        print(f"✅ Identificados {len(checklists_criticos)} checklists con problemas críticos")
        return checklists_criticos
    
    @task
    def create_corrective_orders(checklists_criticos: List[Dict]) -> List[Dict]:
        """
        Crear órdenes de trabajo correctivas para problemas críticos
        
        Args:
            checklists_criticos: Lista de checklists con problemas críticos
        
        Returns:
            Lista de órdenes creadas
        """
        client = CMSSAPIClient()
        ordenes_creadas = []
        
        for checklist in checklists_criticos:
            try:
                # Generar descripción con items fallidos
                items_criticos = checklist['items_criticos_detalle']
                descripcion_items = "\n".join([
                    f"- {item.get('nombre', 'N/A')}: {item.get('observacion', 'Sin observación')}"
                    for item in items_criticos[:5]  # Limitar a 5 items
                ])
                
                descripcion = f"""Checklist con items críticos fallidos:
Checklist: {checklist['template_nombre']}
Fecha: {checklist['fecha_completado']}

Items críticos fallidos ({checklist['items_criticos_fallidos']}):
{descripcion_items}

Acción requerida: Revisar y corregir items críticos."""
                
                # Crear orden de trabajo correctiva
                orden_data = {
                    'idequipo': checklist['equipo_id'],
                    'idtipomantenimientoot': BusinessLogicConfig.TIPOS_MANTENIMIENTO['CORRECTIVO'],
                    'descripcionproblemareportado': descripcion,
                    'prioridad': 'Alta',
                    'idestadoot': BusinessLogicConfig.ESTADOS_OT['PENDIENTE'],
                    'fechareportefalla': datetime.now().isoformat(),
                }
                
                orden = client.create_orden_trabajo(orden_data)
                
                orden_creada = {
                    'orden_id': orden.get('idordentrabajo'),
                    'codigo_ot': orden.get('codigoot'),
                    'checklist_id': checklist['checklist_id'],
                    'equipo_id': checklist['equipo_id'],
                    'equipo_nombre': checklist['equipo_nombre'],
                    'items_criticos': checklist['items_criticos_fallidos']
                }
                
                ordenes_creadas.append(orden_creada)
                
                print(f"✅ Orden creada: {orden.get('codigoot')} para checklist {checklist['checklist_id']}")
                
            except Exception as e:
                print(f"❌ Error al crear orden para checklist {checklist['checklist_id']}: {str(e)}")
        
        print(f"✅ Creadas {len(ordenes_creadas)} órdenes correctivas")
        return ordenes_creadas
    
    @task
    def generate_patterns_analysis(checklists_analizados: List[Dict]) -> Dict:
        """
        Analizar patrones en items fallidos
        
        Args:
            checklists_analizados: Lista de checklists analizados
        
        Returns:
            Análisis de patrones
        """
        # Recopilar todos los items fallidos
        todos_items_fallidos = []
        for checklist in checklists_analizados:
            for item in checklist['items_fallidos_detalle']:
                item_con_contexto = item.copy()
                item_con_contexto['equipo_id'] = checklist['equipo_id']
                item_con_contexto['equipo_nombre'] = checklist['equipo_nombre']
                todos_items_fallidos.append(item_con_contexto)
        
        if not todos_items_fallidos:
            return {
                'total_items_fallidos': 0,
                'items_mas_comunes': [],
                'equipos_mas_afectados': []
            }
        
        # Convertir a DataFrame para análisis
        df_items = pd.DataFrame(todos_items_fallidos)
        
        # Items más comunes
        if 'nombre' in df_items.columns:
            items_comunes = df_items['nombre'].value_counts().head(10).to_dict()
        else:
            items_comunes = {}
        
        # Equipos más afectados
        if 'equipo_nombre' in df_items.columns:
            equipos_afectados = df_items['equipo_nombre'].value_counts().head(10).to_dict()
        else:
            equipos_afectados = {}
        
        analisis = {
            'total_items_fallidos': len(todos_items_fallidos),
            'items_mas_comunes': [
                {'nombre': k, 'frecuencia': v}
                for k, v in items_comunes.items()
            ],
            'equipos_mas_afectados': [
                {'equipo': k, 'items_fallidos': v}
                for k, v in equipos_afectados.items()
            ]
        }
        
        print(f"✅ Análisis de patrones completado: {len(todos_items_fallidos)} items fallidos")
        return analisis
    
    @task
    def send_notifications(
        checklists_criticos: List[Dict],
        ordenes_creadas: List[Dict],
        patrones: Dict
    ):
        """
        Enviar notificaciones a supervisores
        
        Args:
            checklists_criticos: Lista de checklists críticos
            ordenes_creadas: Lista de órdenes creadas
            patrones: Análisis de patrones
        """
        notifier = TelegramNotifier()
        
        # TODO: Obtener chat_ids de supervisores
        supervisor_chat_ids = []  # Configurar con IDs reales
        
        if not supervisor_chat_ids:
            print("⚠️ No hay chat_ids configurados para notificaciones")
            return
        
        # Crear mensaje
        mensaje = f"""
📋 **REPORTE DE CHECKLISTS - DÍA ANTERIOR**

📅 **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}

⚠️ **Checklists con Problemas Críticos:** {len(checklists_criticos)}
🔧 **Órdenes Correctivas Creadas:** {len(ordenes_creadas)}

**Items Más Comunes Fallidos:**
"""
        
        # Agregar top 5 items más comunes
        for item in patrones['items_mas_comunes'][:5]:
            mensaje += f"\n• {item['nombre']}: {item['frecuencia']} veces"
        
        if checklists_criticos:
            mensaje += "\n\n**Equipos Afectados:**"
            for checklist in checklists_criticos[:5]:
                mensaje += f"\n🔴 {checklist['equipo_nombre']}: {checklist['items_criticos_fallidos']} items críticos"
        
        mensaje += "\n\n✅ Se han generado órdenes correctivas automáticamente."
        
        # Enviar a supervisores
        for chat_id in supervisor_chat_ids:
            try:
                notifier.send_message(chat_id, mensaje)
            except Exception as e:
                print(f"❌ Error al enviar notificación a {chat_id}: {str(e)}")
        
        print(f"✅ Notificaciones enviadas")
    
    @task
    def generate_summary(
        checklists: List[Dict],
        checklists_analizados: List[Dict],
        checklists_criticos: List[Dict],
        ordenes_creadas: List[Dict],
        patrones: Dict
    ) -> Dict:
        """
        Generar resumen de ejecución
        
        Args:
            checklists: Lista de checklists procesados
            checklists_analizados: Lista de checklists analizados
            checklists_criticos: Lista de checklists críticos
            ordenes_creadas: Lista de órdenes creadas
            patrones: Análisis de patrones
        
        Returns:
            Diccionario con resumen
        """
        resumen = {
            'fecha_ejecucion': datetime.now().isoformat(),
            'checklists_procesados': len(checklists),
            'checklists_analizados': len(checklists_analizados),
            'checklists_con_problemas_criticos': len(checklists_criticos),
            'ordenes_correctivas_creadas': len(ordenes_creadas),
            'total_items_fallidos': patrones['total_items_fallidos'],
            'items_mas_comunes': patrones['items_mas_comunes'][:5],
            'equipos_mas_afectados': patrones['equipos_mas_afectados'][:5]
        }
        
        print("=" * 60)
        print("RESUMEN DE PROCESAMIENTO DE CHECKLISTS")
        print("=" * 60)
        print(f"Checklists procesados: {resumen['checklists_procesados']}")
        print(f"Checklists con problemas críticos: {resumen['checklists_con_problemas_criticos']}")
        print(f"Órdenes correctivas creadas: {resumen['ordenes_correctivas_creadas']}")
        print(f"Total items fallidos: {resumen['total_items_fallidos']}")
        print("=" * 60)
        
        return resumen
    
    # Definir flujo del DAG
    checklists = get_completed_checklists()
    checklists_analizados = analyze_checklist_items(checklists)
    checklists_criticos = identify_critical_issues(checklists_analizados)
    ordenes_creadas = create_corrective_orders(checklists_criticos)
    patrones = generate_patterns_analysis(checklists_analizados)
    notificaciones = send_notifications(checklists_criticos, ordenes_creadas, patrones)
    resumen = generate_summary(
        checklists,
        checklists_analizados,
        checklists_criticos,
        ordenes_creadas,
        patrones
    )
    
    # Definir dependencias
    checklists >> checklists_analizados >> checklists_criticos >> ordenes_creadas
    checklists_analizados >> patrones
    checklists_criticos >> notificaciones
    ordenes_creadas >> notificaciones
    patrones >> notificaciones
    [checklists, checklists_analizados, checklists_criticos, ordenes_creadas, patrones] >> resumen


# Instanciar el DAG
dag_instance = procesamiento_checklists_dag()

