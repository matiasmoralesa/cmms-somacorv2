"""
Análisis de Series Temporales con Dask
Procesamiento distribuido de datos históricos de órdenes de trabajo
"""

import dask
import dask.dataframe as dd
import pandas as pd
import numpy as np
from dask.distributed import Client, LocalCluster
from typing import Dict, List, Tuple
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Agregar directorios al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'airflow_bot'))
from config.airflow_config import DaskConfig, CMSSConfig
from scripts.cmms_api_client import CMSSAPIClient


class TimeSeriesAnalyzer:
    """Analizador de series temporales con Dask"""
    
    def __init__(self, scheduler_address: str = None):
        """
        Inicializar analizador
        
        Args:
            scheduler_address: Dirección del scheduler de Dask
        """
        self.scheduler_address = scheduler_address or DaskConfig.SCHEDULER_ADDRESS
        self.client = None
        self.cmms_client = CMSSAPIClient()
    
    def connect(self):
        """Conectar al cluster de Dask"""
        try:
            self.client = Client(self.scheduler_address, timeout='10s')
            print(f"✅ Conectado al cluster de Dask: {self.scheduler_address}")
            print(f"   Dashboard: {self.client.dashboard_link}")
        except Exception as e:
            print(f"⚠️ No se pudo conectar al cluster remoto: {str(e)}")
            print("   Iniciando cluster local...")
            cluster = LocalCluster(
                n_workers=DaskConfig.N_WORKERS,
                threads_per_worker=DaskConfig.THREADS_PER_WORKER,
                memory_limit=DaskConfig.MEMORY_LIMIT
            )
            self.client = Client(cluster)
            print(f"✅ Cluster local iniciado")
            print(f"   Dashboard: {self.client.dashboard_link}")
    
    def close(self):
        """Cerrar conexión al cluster"""
        if self.client:
            self.client.close()
            print("✅ Conexión cerrada")
    
    def load_work_orders_to_dask(self) -> dd.DataFrame:
        """
        Cargar órdenes de trabajo en un Dask DataFrame
        
        Returns:
            Dask DataFrame con órdenes de trabajo
        """
        # Obtener órdenes de trabajo desde la API
        ordenes = self.cmms_client.get_ordenes_trabajo()
        
        # Convertir a pandas DataFrame
        df_pandas = pd.DataFrame(ordenes)
        
        # Convertir fechas
        date_columns = ['fechareportefalla', 'fechacompletado']
        for col in date_columns:
            if col in df_pandas.columns:
                df_pandas[col] = pd.to_datetime(df_pandas[col], errors='coerce')
        
        # Convertir a Dask DataFrame
        ddf = dd.from_pandas(df_pandas, npartitions=DaskConfig.N_WORKERS)
        
        print(f"✅ Cargadas {len(df_pandas)} órdenes de trabajo en Dask DataFrame")
        return ddf
    
    def calculate_mtbf_by_equipment(self, ddf: dd.DataFrame) -> pd.DataFrame:
        """
        Calcular MTBF (Mean Time Between Failures) por equipo usando Dask
        
        Args:
            ddf: Dask DataFrame con órdenes de trabajo
        
        Returns:
            DataFrame con MTBF por equipo
        """
        print("Calculando MTBF por equipo...")
        
        # Filtrar solo órdenes correctivas completadas
        ddf_correctivas = ddf[
            (ddf['idtipomantenimientoot'] == 1) &  # Correctivo
            (ddf['idestadoot'] == 3)  # Completada
        ]
        
        # Función para calcular MTBF de un grupo
        def calc_mtbf_group(group):
            if len(group) < 2:
                return pd.Series({
                    'num_fallas': len(group),
                    'mtbf_dias': np.nan,
                    'ultima_falla': group['fechareportefalla'].max() if len(group) > 0 else pd.NaT
                })
            
            # Ordenar por fecha
            group = group.sort_values('fechareportefalla')
            
            # Calcular intervalos entre fallas
            intervalos = group['fechareportefalla'].diff().dropna()
            mtbf_dias = intervalos.mean().total_seconds() / (24 * 3600)
            
            return pd.Series({
                'num_fallas': len(group),
                'mtbf_dias': mtbf_dias,
                'ultima_falla': group['fechareportefalla'].max()
            })
        
        # Agrupar por equipo y calcular MTBF
        mtbf_by_equipment = ddf_correctivas.groupby('idequipo').apply(
            calc_mtbf_group,
            meta={
                'num_fallas': 'int64',
                'mtbf_dias': 'float64',
                'ultima_falla': 'datetime64[ns]'
            }
        ).compute()
        
        print(f"✅ MTBF calculado para {len(mtbf_by_equipment)} equipos")
        return mtbf_by_equipment
    
    def calculate_mttr_by_equipment(self, ddf: dd.DataFrame) -> pd.DataFrame:
        """
        Calcular MTTR (Mean Time To Repair) por equipo usando Dask
        
        Args:
            ddf: Dask DataFrame con órdenes de trabajo
        
        Returns:
            DataFrame con MTTR por equipo
        """
        print("Calculando MTTR por equipo...")
        
        # Filtrar órdenes completadas con ambas fechas
        ddf_completadas = ddf[
            (ddf['idestadoot'] == 3) &  # Completada
            ddf['fechareportefalla'].notna() &
            ddf['fechacompletado'].notna()
        ]
        
        # Calcular tiempo de reparación
        ddf_completadas = ddf_completadas.assign(
            tiempo_reparacion_horas=lambda x: (
                (x['fechacompletado'] - x['fechareportefalla']).dt.total_seconds() / 3600
            )
        )
        
        # Agrupar por equipo y calcular MTTR
        mttr_by_equipment = ddf_completadas.groupby('idequipo').agg({
            'tiempo_reparacion_horas': ['mean', 'median', 'std', 'count']
        }).compute()
        
        # Renombrar columnas
        mttr_by_equipment.columns = ['mttr_mean', 'mttr_median', 'mttr_std', 'num_reparaciones']
        
        print(f"✅ MTTR calculado para {len(mttr_by_equipment)} equipos")
        return mttr_by_equipment
    
    def analyze_failure_trends(
        self,
        ddf: dd.DataFrame,
        period: str = 'M'
    ) -> pd.DataFrame:
        """
        Analizar tendencias de fallas por período
        
        Args:
            ddf: Dask DataFrame con órdenes de trabajo
            period: Período de agregación ('D'=día, 'W'=semana, 'M'=mes)
        
        Returns:
            DataFrame con tendencias de fallas
        """
        print(f"Analizando tendencias de fallas por {period}...")
        
        # Filtrar solo órdenes correctivas
        ddf_correctivas = ddf[ddf['idtipomantenimientoot'] == 1]
        
        # Convertir a pandas para resample (Dask no soporta resample directamente)
        df_correctivas = ddf_correctivas.compute()
        
        # Establecer fecha como índice
        df_correctivas = df_correctivas.set_index('fechareportefalla')
        
        # Resample por período
        tendencias = df_correctivas.resample(period).agg({
            'idordentrabajo': 'count',
            'idequipo': 'nunique',
            'prioridad': lambda x: (x == 'Urgente').sum()
        })
        
        # Renombrar columnas
        tendencias.columns = ['num_fallas', 'equipos_afectados', 'fallas_urgentes']
        
        # Calcular tasa de crecimiento
        tendencias['tasa_crecimiento'] = tendencias['num_fallas'].pct_change() * 100
        
        print(f"✅ Tendencias calculadas para {len(tendencias)} períodos")
        return tendencias
    
    def detect_anomalies(
        self,
        ddf: dd.DataFrame,
        threshold_std: float = 2.0
    ) -> pd.DataFrame:
        """
        Detectar anomalías en patrones de fallas
        
        Args:
            ddf: Dask DataFrame con órdenes de trabajo
            threshold_std: Umbral de desviaciones estándar para anomalías
        
        Returns:
            DataFrame con anomalías detectadas
        """
        print("Detectando anomalías...")
        
        # Calcular frecuencia de fallas por equipo y día
        ddf_correctivas = ddf[ddf['idtipomantenimientoot'] == 1].compute()
        
        if ddf_correctivas.empty:
            return pd.DataFrame()
        
        # Agrupar por equipo y fecha
        ddf_correctivas['fecha'] = ddf_correctivas['fechareportefalla'].dt.date
        frecuencia = ddf_correctivas.groupby(['idequipo', 'fecha']).size().reset_index(name='num_fallas')
        
        # Calcular estadísticas por equipo
        stats = frecuencia.groupby('idequipo')['num_fallas'].agg(['mean', 'std'])
        
        # Identificar anomalías
        anomalias = []
        for _, row in frecuencia.iterrows():
            equipo_id = row['idequipo']
            num_fallas = row['num_fallas']
            
            if equipo_id in stats.index:
                mean = stats.loc[equipo_id, 'mean']
                std = stats.loc[equipo_id, 'std']
                
                if pd.notna(std) and std > 0:
                    z_score = (num_fallas - mean) / std
                    
                    if abs(z_score) > threshold_std:
                        anomalias.append({
                            'equipo_id': equipo_id,
                            'fecha': row['fecha'],
                            'num_fallas': num_fallas,
                            'mean': mean,
                            'std': std,
                            'z_score': z_score,
                            'tipo': 'ALTA' if z_score > 0 else 'BAJA'
                        })
        
        df_anomalias = pd.DataFrame(anomalias)
        
        print(f"✅ Detectadas {len(df_anomalias)} anomalías")
        return df_anomalias
    
    def calculate_equipment_health_score(
        self,
        ddf: dd.DataFrame
    ) -> pd.DataFrame:
        """
        Calcular score de salud de equipos basado en múltiples factores
        
        Args:
            ddf: Dask DataFrame con órdenes de trabajo
        
        Returns:
            DataFrame con scores de salud por equipo
        """
        print("Calculando scores de salud de equipos...")
        
        # Calcular MTBF y MTTR
        mtbf = self.calculate_mtbf_by_equipment(ddf)
        mttr = self.calculate_mttr_by_equipment(ddf)
        
        # Combinar métricas
        health_scores = pd.concat([mtbf, mttr], axis=1)
        
        # Normalizar métricas (0-100)
        # Score MTBF: mayor es mejor
        if 'mtbf_dias' in health_scores.columns:
            mtbf_max = health_scores['mtbf_dias'].max()
            if mtbf_max > 0:
                health_scores['score_mtbf'] = (health_scores['mtbf_dias'] / mtbf_max * 100).fillna(0)
            else:
                health_scores['score_mtbf'] = 0
        else:
            health_scores['score_mtbf'] = 0
        
        # Score MTTR: menor es mejor
        if 'mttr_mean' in health_scores.columns:
            mttr_max = health_scores['mttr_mean'].max()
            if mttr_max > 0:
                health_scores['score_mttr'] = (100 - (health_scores['mttr_mean'] / mttr_max * 100)).fillna(0)
            else:
                health_scores['score_mttr'] = 100
        else:
            health_scores['score_mttr'] = 100
        
        # Score de frecuencia de fallas: menos fallas es mejor
        if 'num_fallas' in health_scores.columns:
            fallas_max = health_scores['num_fallas'].max()
            if fallas_max > 0:
                health_scores['score_frecuencia'] = (100 - (health_scores['num_fallas'] / fallas_max * 100)).fillna(0)
            else:
                health_scores['score_frecuencia'] = 100
        else:
            health_scores['score_frecuencia'] = 100
        
        # Score total (promedio ponderado)
        health_scores['health_score'] = (
            health_scores['score_mtbf'] * 0.4 +
            health_scores['score_mttr'] * 0.3 +
            health_scores['score_frecuencia'] * 0.3
        )
        
        # Clasificar nivel de salud
        health_scores['health_level'] = pd.cut(
            health_scores['health_score'],
            bins=[0, 40, 60, 80, 100],
            labels=['CRÍTICO', 'BAJO', 'MEDIO', 'ALTO']
        )
        
        print(f"✅ Scores de salud calculados para {len(health_scores)} equipos")
        return health_scores
    
    def generate_comprehensive_report(self) -> Dict:
        """
        Generar reporte comprensivo de análisis de series temporales
        
        Returns:
            Diccionario con resultados de análisis
        """
        print("=" * 60)
        print("ANÁLISIS DE SERIES TEMPORALES CON DASK")
        print("=" * 60)
        
        # Conectar al cluster
        self.connect()
        
        try:
            # Cargar datos
            ddf = self.load_work_orders_to_dask()
            
            # Realizar análisis
            mtbf = self.calculate_mtbf_by_equipment(ddf)
            mttr = self.calculate_mttr_by_equipment(ddf)
            tendencias = self.analyze_failure_trends(ddf, period='M')
            anomalias = self.detect_anomalies(ddf)
            health_scores = self.calculate_equipment_health_score(ddf)
            
            # Generar reporte
            reporte = {
                'fecha_analisis': datetime.now().isoformat(),
                'total_ordenes_analizadas': len(ddf),
                'equipos_analizados': len(health_scores),
                'mtbf_promedio': float(mtbf['mtbf_dias'].mean()) if not mtbf.empty else 0,
                'mttr_promedio': float(mttr['mttr_mean'].mean()) if not mttr.empty else 0,
                'anomalias_detectadas': len(anomalias),
                'equipos_criticos': int((health_scores['health_level'] == 'CRÍTICO').sum()) if not health_scores.empty else 0,
                'health_score_promedio': float(health_scores['health_score'].mean()) if not health_scores.empty else 0,
                'tendencias': tendencias.to_dict('records') if not tendencias.empty else [],
                'top_equipos_riesgo': health_scores.nsmallest(10, 'health_score').to_dict('records') if not health_scores.empty else []
            }
            
            print("=" * 60)
            print("RESULTADOS DEL ANÁLISIS")
            print("=" * 60)
            print(f"Órdenes analizadas: {reporte['total_ordenes_analizadas']}")
            print(f"Equipos analizados: {reporte['equipos_analizados']}")
            print(f"MTBF promedio: {reporte['mtbf_promedio']:.2f} días")
            print(f"MTTR promedio: {reporte['mttr_promedio']:.2f} horas")
            print(f"Anomalías detectadas: {reporte['anomalias_detectadas']}")
            print(f"Equipos críticos: {reporte['equipos_criticos']}")
            print(f"Health score promedio: {reporte['health_score_promedio']:.2f}")
            print("=" * 60)
            
            return reporte
            
        finally:
            # Cerrar conexión
            self.close()


if __name__ == '__main__':
    # Ejecutar análisis
    analyzer = TimeSeriesAnalyzer()
    reporte = analyzer.generate_comprehensive_report()
    
    print("\n✅ Análisis completado")

