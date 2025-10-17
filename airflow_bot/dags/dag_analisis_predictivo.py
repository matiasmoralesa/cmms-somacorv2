"""
DAG de Análisis Predictivo de Fallas
Ejecuta análisis predictivo diario para identificar equipos en riesgo de falla
"""

from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, List
import joblib

# Agregar directorios al path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.airflow_config import (
    ScheduleConfig,
    BusinessLogicConfig,
    MLConfig,
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
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}


@dag(
    dag_id='analisis_predictivo_fallas',
    default_args=default_args,
    description='Análisis predictivo diario de fallas de equipos',
    schedule=ScheduleConfig.DAG_PREDICTIVO,
    start_date=days_ago(1),
    catchup=False,
    tags=['cmms', 'predictivo', 'ml', 'alertas'],
)
def analisis_predictivo_dag():
    """
    DAG para análisis predictivo de fallas de equipos
    
    Flujo:
    1. Extraer datos históricos de equipos y órdenes de trabajo
    2. Calcular métricas de confiabilidad (MTBF, MTTR)
    3. Ejecutar modelo predictivo de fallas
    4. Identificar equipos en riesgo
    5. Generar alertas y recomendaciones
    6. Enviar notificaciones vía Telegram
    """
    
    @task
    def extract_equipment_data() -> List[Dict]:
        """
        Extraer datos de equipos activos
        
        Returns:
            Lista de equipos con sus datos
        """
        client = CMSSAPIClient()
        equipos = client.get_equipos(params={'activo': True})
        
        print(f"✅ Extraídos {len(equipos)} equipos activos")
        return equipos
    
    @task
    def extract_work_orders_history() -> List[Dict]:
        """
        Extraer historial de órdenes de trabajo
        
        Returns:
            Lista de órdenes de trabajo históricas
        """
        client = CMSSAPIClient()
        ordenes = client.get_ordenes_trabajo()
        
        print(f"✅ Extraídas {len(ordenes)} órdenes de trabajo")
        return ordenes
    
    @task
    def calculate_reliability_metrics(
        equipos: List[Dict],
        ordenes: List[Dict]
    ) -> Dict[int, Dict]:
        """
        Calcular métricas de confiabilidad por equipo
        
        Args:
            equipos: Lista de equipos
            ordenes: Lista de órdenes de trabajo
        
        Returns:
            Diccionario con métricas por equipo
        """
        # Convertir a DataFrames
        df_ordenes = pd.DataFrame(ordenes)
        
        # Filtrar solo órdenes correctivas completadas
        df_correctivas = df_ordenes[
            (df_ordenes['idtipomantenimientoot'] == BusinessLogicConfig.TIPOS_MANTENIMIENTO['CORRECTIVO']) &
            (df_ordenes['idestadoot'] == BusinessLogicConfig.ESTADOS_OT['COMPLETADA'])
        ].copy()
        
        # Convertir fechas
        df_correctivas['fechareportefalla'] = pd.to_datetime(
            df_correctivas['fechareportefalla'],
            errors='coerce'
        )
        df_correctivas['fechacompletado'] = pd.to_datetime(
            df_correctivas['fechacompletado'],
            errors='coerce'
        )
        
        metricas = {}
        
        for equipo in equipos:
            equipo_id = equipo['idequipo']
            
            # Filtrar órdenes del equipo
            ordenes_equipo = df_correctivas[df_correctivas['idequipo'] == equipo_id]
            
            if len(ordenes_equipo) < 2:
                # No hay suficientes datos
                metricas[equipo_id] = {
                    'equipo_id': equipo_id,
                    'nombre_equipo': equipo.get('nombreequipo', 'N/A'),
                    'mtbf_dias': None,
                    'mttr_horas': None,
                    'num_fallas': len(ordenes_equipo),
                    'ultima_falla': ordenes_equipo['fechareportefalla'].max() if len(ordenes_equipo) > 0 else None,
                    'tiene_datos_suficientes': False
                }
                continue
            
            # Ordenar por fecha
            ordenes_equipo = ordenes_equipo.sort_values('fechareportefalla')
            
            # Calcular MTBF (Mean Time Between Failures)
            fechas_fallas = ordenes_equipo['fechareportefalla'].dropna()
            if len(fechas_fallas) >= 2:
                intervalos = fechas_fallas.diff().dropna()
                mtbf_dias = intervalos.mean().total_seconds() / (24 * 3600)
            else:
                mtbf_dias = None
            
            # Calcular MTTR (Mean Time To Repair)
            ordenes_con_fechas = ordenes_equipo.dropna(subset=['fechareportefalla', 'fechacompletado'])
            if len(ordenes_con_fechas) > 0:
                tiempos_reparacion = (
                    ordenes_con_fechas['fechacompletado'] - 
                    ordenes_con_fechas['fechareportefalla']
                )
                mttr_horas = tiempos_reparacion.mean().total_seconds() / 3600
            else:
                mttr_horas = None
            
            # Calcular días desde última falla
            ultima_falla = fechas_fallas.max()
            if pd.notna(ultima_falla):
                dias_desde_ultima_falla = (datetime.now() - ultima_falla).days
            else:
                dias_desde_ultima_falla = None
            
            metricas[equipo_id] = {
                'equipo_id': equipo_id,
                'nombre_equipo': equipo.get('nombreequipo', 'N/A'),
                'codigo_interno': equipo.get('codigointerno', 'N/A'),
                'tipo_equipo': equipo.get('idtipoequipo'),
                'faena': equipo.get('idfaenaactual'),
                'mtbf_dias': mtbf_dias,
                'mttr_horas': mttr_horas,
                'num_fallas': len(ordenes_equipo),
                'ultima_falla': ultima_falla,
                'dias_desde_ultima_falla': dias_desde_ultima_falla,
                'tiene_datos_suficientes': True
            }
        
        print(f"✅ Calculadas métricas para {len(metricas)} equipos")
        return metricas
    
    @task
    def predict_failures(metricas: Dict[int, Dict]) -> List[Dict]:
        """
        Predecir probabilidad de falla usando modelo de ML
        
        Args:
            metricas: Métricas de confiabilidad por equipo
        
        Returns:
            Lista de equipos con predicciones
        """
        predicciones = []
        
        # TODO: Cargar modelo de ML entrenado
        # Por ahora, usar heurística basada en umbrales
        
        for equipo_id, metrica in metricas.items():
            if not metrica['tiene_datos_suficientes']:
                continue
            
            mtbf = metrica['mtbf_dias']
            mttr = metrica['mttr_horas']
            dias_desde_falla = metrica['dias_desde_ultima_falla']
            
            # Calcular probabilidad de falla (heurística simple)
            probabilidad = 0.0
            
            # Factor 1: MTBF bajo
            if mtbf is not None and mtbf < BusinessLogicConfig.MTBF_THRESHOLD_DAYS:
                probabilidad += 0.3
            
            # Factor 2: MTTR alto
            if mttr is not None and mttr > BusinessLogicConfig.MTTR_THRESHOLD_HOURS:
                probabilidad += 0.2
            
            # Factor 3: Proximidad a MTBF
            if mtbf is not None and dias_desde_falla is not None:
                ratio_mtbf = dias_desde_falla / mtbf
                if ratio_mtbf > 0.8:
                    probabilidad += 0.3 * ratio_mtbf
            
            # Factor 4: Frecuencia de fallas
            if metrica['num_fallas'] > 5:
                probabilidad += 0.2
            
            # Normalizar probabilidad
            probabilidad = min(probabilidad, 1.0)
            
            # Solo incluir equipos con probabilidad significativa
            if probabilidad >= BusinessLogicConfig.FAILURE_PROBABILITY_THRESHOLD:
                predicciones.append({
                    'equipo_id': equipo_id,
                    'nombre_equipo': metrica['nombre_equipo'],
                    'codigo_interno': metrica['codigo_interno'],
                    'probabilidad_falla': probabilidad,
                    'mtbf_dias': mtbf,
                    'mttr_horas': mttr,
                    'num_fallas': metrica['num_fallas'],
                    'dias_desde_ultima_falla': dias_desde_falla,
                    'nivel_riesgo': 'ALTO' if probabilidad >= 0.8 else 'MEDIO'
                })
        
        # Ordenar por probabilidad descendente
        predicciones.sort(key=lambda x: x['probabilidad_falla'], reverse=True)
        
        print(f"✅ Identificados {len(predicciones)} equipos en riesgo")
        return predicciones
    
    @task
    def generate_alerts(predicciones: List[Dict]) -> List[Dict]:
        """
        Generar alertas para equipos en riesgo
        
        Args:
            predicciones: Lista de equipos con predicciones
        
        Returns:
            Lista de alertas generadas
        """
        alertas = []
        
        for pred in predicciones:
            alerta = {
                'equipo_id': pred['equipo_id'],
                'nombre_equipo': pred['nombre_equipo'],
                'tipo_alerta': 'PREDICCION_FALLA',
                'nivel': pred['nivel_riesgo'],
                'probabilidad': pred['probabilidad_falla'],
                'mensaje': f"Equipo {pred['nombre_equipo']} tiene {pred['probabilidad_falla']*100:.1f}% de probabilidad de falla",
                'recomendacion': 'Programar mantenimiento preventivo urgente',
                'mtbf_dias': pred['mtbf_dias'],
                'mttr_horas': pred['mttr_horas'],
                'fecha_generacion': datetime.now().isoformat()
            }
            alertas.append(alerta)
        
        print(f"✅ Generadas {len(alertas)} alertas")
        return alertas
    
    @task
    def create_preventive_orders(predicciones: List[Dict]) -> List[Dict]:
        """
        Crear órdenes de trabajo preventivas para equipos en alto riesgo
        
        Args:
            predicciones: Lista de equipos con predicciones
        
        Returns:
            Lista de órdenes creadas
        """
        client = CMSSAPIClient()
        ordenes_creadas = []
        
        # Filtrar solo equipos con riesgo ALTO
        equipos_alto_riesgo = [
            p for p in predicciones 
            if p['nivel_riesgo'] == 'ALTO'
        ]
        
        for pred in equipos_alto_riesgo:
            try:
                # Crear orden de trabajo preventiva
                orden_data = {
                    'idequipo': pred['equipo_id'],
                    'idtipomantenimientoot': BusinessLogicConfig.TIPOS_MANTENIMIENTO['PREDICTIVO'],
                    'descripcionproblemareportado': f"Mantenimiento predictivo - Probabilidad de falla: {pred['probabilidad_falla']*100:.1f}%",
                    'prioridad': 'Alta',
                    'idestadoot': BusinessLogicConfig.ESTADOS_OT['PENDIENTE'],
                    'fechareportefalla': datetime.now().isoformat(),
                }
                
                orden = client.create_orden_trabajo(orden_data)
                ordenes_creadas.append(orden)
                
                print(f"✅ Orden creada para equipo {pred['nombre_equipo']}: {orden.get('codigoot')}")
                
            except Exception as e:
                print(f"❌ Error al crear orden para equipo {pred['equipo_id']}: {str(e)}")
        
        print(f"✅ Creadas {len(ordenes_creadas)} órdenes preventivas")
        return ordenes_creadas
    
    @task
    def send_telegram_notifications(
        alertas: List[Dict],
        ordenes_creadas: List[Dict]
    ):
        """
        Enviar notificaciones vía Telegram
        
        Args:
            alertas: Lista de alertas generadas
            ordenes_creadas: Lista de órdenes creadas
        """
        notifier = TelegramNotifier()
        
        # TODO: Obtener lista de chat_ids de administradores/supervisores
        # Por ahora, usar un chat_id de ejemplo
        admin_chat_ids = []  # Configurar con IDs reales
        
        if not admin_chat_ids:
            print("⚠️ No hay chat_ids configurados para notificaciones")
            return
        
        # Crear mensaje resumen
        mensaje = f"""
🤖 **REPORTE DE ANÁLISIS PREDICTIVO**

📅 **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}

⚠️ **Alertas Generadas:** {len(alertas)}
🔴 **Riesgo Alto:** {sum(1 for a in alertas if a['nivel'] == 'ALTO')}
🟡 **Riesgo Medio:** {sum(1 for a in alertas if a['nivel'] == 'MEDIO')}

📋 **Órdenes Creadas:** {len(ordenes_creadas)}

**Equipos en Riesgo Alto:**
"""
        
        # Agregar top 5 equipos en riesgo
        alertas_alto = [a for a in alertas if a['nivel'] == 'ALTO'][:5]
        for alerta in alertas_alto:
            mensaje += f"\n🔴 {alerta['nombre_equipo']} - {alerta['probabilidad']*100:.1f}%"
        
        mensaje += "\n\n✅ Revisa el dashboard de Airflow para más detalles."
        
        # Enviar a todos los administradores
        for chat_id in admin_chat_ids:
            try:
                notifier.send_message(chat_id, mensaje)
            except Exception as e:
                print(f"❌ Error al enviar notificación a {chat_id}: {str(e)}")
        
        print(f"✅ Notificaciones enviadas a {len(admin_chat_ids)} administradores")
    
    @task
    def generate_summary_report(
        equipos: List[Dict],
        predicciones: List[Dict],
        alertas: List[Dict],
        ordenes_creadas: List[Dict]
    ) -> Dict:
        """
        Generar reporte resumen de la ejecución
        
        Args:
            equipos: Lista de equipos analizados
            predicciones: Lista de predicciones
            alertas: Lista de alertas
            ordenes_creadas: Lista de órdenes creadas
        
        Returns:
            Diccionario con resumen de ejecución
        """
        resumen = {
            'fecha_ejecucion': datetime.now().isoformat(),
            'total_equipos_analizados': len(equipos),
            'equipos_con_datos_suficientes': len(predicciones),
            'total_alertas': len(alertas),
            'alertas_alto_riesgo': sum(1 for a in alertas if a['nivel'] == 'ALTO'),
            'alertas_medio_riesgo': sum(1 for a in alertas if a['nivel'] == 'MEDIO'),
            'ordenes_preventivas_creadas': len(ordenes_creadas),
            'top_equipos_riesgo': predicciones[:10] if predicciones else []
        }
        
        print("=" * 60)
        print("RESUMEN DE ANÁLISIS PREDICTIVO")
        print("=" * 60)
        print(f"Equipos analizados: {resumen['total_equipos_analizados']}")
        print(f"Alertas generadas: {resumen['total_alertas']}")
        print(f"  - Alto riesgo: {resumen['alertas_alto_riesgo']}")
        print(f"  - Medio riesgo: {resumen['alertas_medio_riesgo']}")
        print(f"Órdenes creadas: {resumen['ordenes_preventivas_creadas']}")
        print("=" * 60)
        
        return resumen
    
    # Definir flujo del DAG
    equipos = extract_equipment_data()
    ordenes = extract_work_orders_history()
    metricas = calculate_reliability_metrics(equipos, ordenes)
    predicciones = predict_failures(metricas)
    alertas = generate_alerts(predicciones)
    ordenes_creadas = create_preventive_orders(predicciones)
    notificaciones = send_telegram_notifications(alertas, ordenes_creadas)
    resumen = generate_summary_report(equipos, predicciones, alertas, ordenes_creadas)
    
    # Definir dependencias
    [equipos, ordenes] >> metricas >> predicciones >> alertas
    predicciones >> ordenes_creadas
    alertas >> notificaciones
    ordenes_creadas >> notificaciones
    [equipos, predicciones, alertas, ordenes_creadas] >> resumen


# Instanciar el DAG
dag_instance = analisis_predictivo_dag()

