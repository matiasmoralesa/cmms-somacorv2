"""
Modelo de Predicción de Fallas con Machine Learning
Entrenamiento con Dask-ML para procesamiento distribuido
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import joblib
import sys
from pathlib import Path
from typing import Tuple, Dict

# Machine Learning
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    accuracy_score
)

# Dask ML
import dask.dataframe as dd
from dask.distributed import Client
from dask_ml.model_selection import train_test_split as dask_train_test_split
from dask_ml.preprocessing import StandardScaler as DaskStandardScaler

# Agregar directorios al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'airflow_bot'))
from config.airflow_config import MLConfig, DaskConfig, BusinessLogicConfig
from scripts.cmms_api_client import CMSSAPIClient


class FailurePredictionModel:
    """Modelo de predicción de fallas de equipos"""
    
    def __init__(self):
        """Inicializar modelo"""
        self.cmms_client = CMSSAPIClient()
        self.model = None
        self.scaler = None
        self.feature_names = []
        self.model_path = Path(MLConfig.FAILURE_PREDICTION_MODEL)
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
    
    def extract_features(self, equipos: pd.DataFrame, ordenes: pd.DataFrame) -> pd.DataFrame:
        """
        Extraer features para el modelo
        
        Args:
            equipos: DataFrame con equipos
            ordenes: DataFrame con órdenes de trabajo
        
        Returns:
            DataFrame con features
        """
        print("Extrayendo features...")
        
        features_list = []
        
        for _, equipo in equipos.iterrows():
            equipo_id = equipo['idequipo']
            
            # Filtrar órdenes del equipo
            ordenes_equipo = ordenes[ordenes['idequipo'] == equipo_id].copy()
            
            # Filtrar solo correctivas
            ordenes_correctivas = ordenes_equipo[
                ordenes_equipo['idtipomantenimientoot'] == BusinessLogicConfig.TIPOS_MANTENIMIENTO['CORRECTIVO']
            ]
            
            # Calcular features
            features = {
                'equipo_id': equipo_id,
                'tipo_equipo': equipo.get('idtipoequipo', 0),
                'edad_equipo': datetime.now().year - equipo.get('anio', datetime.now().year),
                
                # Features de historial de fallas
                'num_fallas_total': len(ordenes_correctivas),
                'num_fallas_ultimo_mes': len(ordenes_correctivas[
                    ordenes_correctivas['fechareportefalla'] >= datetime.now() - timedelta(days=30)
                ]) if not ordenes_correctivas.empty else 0,
                'num_fallas_ultimos_3_meses': len(ordenes_correctivas[
                    ordenes_correctivas['fechareportefalla'] >= datetime.now() - timedelta(days=90)
                ]) if not ordenes_correctivas.empty else 0,
                'num_fallas_ultimo_anio': len(ordenes_correctivas[
                    ordenes_correctivas['fechareportefalla'] >= datetime.now() - timedelta(days=365)
                ]) if not ordenes_correctivas.empty else 0,
            }
            
            # MTBF (Mean Time Between Failures)
            if len(ordenes_correctivas) >= 2:
                ordenes_correctivas_sorted = ordenes_correctivas.sort_values('fechareportefalla')
                intervalos = ordenes_correctivas_sorted['fechareportefalla'].diff().dropna()
                features['mtbf_dias'] = intervalos.mean().total_seconds() / (24 * 3600) if len(intervalos) > 0 else 0
                features['mtbf_std'] = intervalos.std().total_seconds() / (24 * 3600) if len(intervalos) > 0 else 0
            else:
                features['mtbf_dias'] = 0
                features['mtbf_std'] = 0
            
            # MTTR (Mean Time To Repair)
            ordenes_con_fechas = ordenes_correctivas.dropna(subset=['fechareportefalla', 'fechacompletado'])
            if len(ordenes_con_fechas) > 0:
                tiempos_reparacion = (
                    ordenes_con_fechas['fechacompletado'] - 
                    ordenes_con_fechas['fechareportefalla']
                )
                features['mttr_horas'] = tiempos_reparacion.mean().total_seconds() / 3600
                features['mttr_std'] = tiempos_reparacion.std().total_seconds() / 3600
            else:
                features['mttr_horas'] = 0
                features['mttr_std'] = 0
            
            # Días desde última falla
            if not ordenes_correctivas.empty:
                ultima_falla = ordenes_correctivas['fechareportefalla'].max()
                features['dias_desde_ultima_falla'] = (datetime.now() - ultima_falla).days
            else:
                features['dias_desde_ultima_falla'] = 999
            
            # Features de mantenimiento preventivo
            ordenes_preventivas = ordenes_equipo[
                ordenes_equipo['idtipomantenimientoot'] == BusinessLogicConfig.TIPOS_MANTENIMIENTO['PREVENTIVO']
            ]
            features['num_mantenimientos_preventivos'] = len(ordenes_preventivas)
            
            # Días desde último mantenimiento preventivo
            if not ordenes_preventivas.empty:
                ultimo_preventivo = ordenes_preventivas['fechacompletado'].max()
                if pd.notna(ultimo_preventivo):
                    features['dias_desde_ultimo_preventivo'] = (datetime.now() - ultimo_preventivo).days
                else:
                    features['dias_desde_ultimo_preventivo'] = 999
            else:
                features['dias_desde_ultimo_preventivo'] = 999
            
            # Ratio de mantenimiento preventivo vs correctivo
            total_mantenimientos = len(ordenes_equipo)
            if total_mantenimientos > 0:
                features['ratio_preventivo_correctivo'] = len(ordenes_preventivas) / total_mantenimientos
            else:
                features['ratio_preventivo_correctivo'] = 0
            
            # Target: ¿Tendrá falla en los próximos 30 días?
            # Para entrenamiento, miramos si hubo falla en los 30 días siguientes
            # (esto requiere datos históricos)
            features['target'] = 0  # Placeholder, se calculará después
            
            features_list.append(features)
        
        df_features = pd.DataFrame(features_list)
        
        print(f"✅ Features extraídos para {len(df_features)} equipos")
        return df_features
    
    def create_target_variable(
        self,
        df_features: pd.DataFrame,
        ordenes: pd.DataFrame,
        prediction_window_days: int = 30
    ) -> pd.DataFrame:
        """
        Crear variable target basada en si hubo falla en ventana de predicción
        
        Args:
            df_features: DataFrame con features
            ordenes: DataFrame con órdenes de trabajo
            prediction_window_days: Ventana de predicción en días
        
        Returns:
            DataFrame con target calculado
        """
        print(f"Creando variable target (ventana de {prediction_window_days} días)...")
        
        # Para cada equipo, verificar si tuvo falla en los próximos N días
        # Nota: En producción, esto se hace con datos históricos
        # Para simplificar, usamos una heurística basada en MTBF
        
        for idx, row in df_features.iterrows():
            equipo_id = row['equipo_id']
            mtbf = row['mtbf_dias']
            dias_desde_falla = row['dias_desde_ultima_falla']
            
            # Heurística: si días desde última falla > 80% del MTBF, alta probabilidad
            if mtbf > 0 and dias_desde_falla > (mtbf * 0.8):
                df_features.at[idx, 'target'] = 1
            elif row['num_fallas_ultimo_mes'] >= 2:
                df_features.at[idx, 'target'] = 1
            else:
                df_features.at[idx, 'target'] = 0
        
        # Balancear clases si es necesario
        class_counts = df_features['target'].value_counts()
        print(f"   Clase 0 (no falla): {class_counts.get(0, 0)}")
        print(f"   Clase 1 (falla): {class_counts.get(1, 0)}")
        
        return df_features
    
    def prepare_data(self) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Preparar datos para entrenamiento
        
        Returns:
            Tupla (X, y) con features y target
        """
        print("Preparando datos...")
        
        # Obtener datos desde la API
        equipos = self.cmms_client.get_equipos()
        ordenes = self.cmms_client.get_ordenes_trabajo()
        
        # Convertir a DataFrames
        df_equipos = pd.DataFrame(equipos)
        df_ordenes = pd.DataFrame(ordenes)
        
        # Convertir fechas
        df_ordenes['fechareportefalla'] = pd.to_datetime(
            df_ordenes['fechareportefalla'],
            errors='coerce'
        )
        df_ordenes['fechacompletado'] = pd.to_datetime(
            df_ordenes['fechacompletado'],
            errors='coerce'
        )
        
        # Extraer features
        df_features = self.extract_features(df_equipos, df_ordenes)
        
        # Crear target
        df_features = self.create_target_variable(df_features, df_ordenes)
        
        # Separar features y target
        feature_columns = [
            'tipo_equipo', 'edad_equipo',
            'num_fallas_total', 'num_fallas_ultimo_mes',
            'num_fallas_ultimos_3_meses', 'num_fallas_ultimo_anio',
            'mtbf_dias', 'mtbf_std',
            'mttr_horas', 'mttr_std',
            'dias_desde_ultima_falla',
            'num_mantenimientos_preventivos',
            'dias_desde_ultimo_preventivo',
            'ratio_preventivo_correctivo'
        ]
        
        self.feature_names = feature_columns
        
        X = df_features[feature_columns]
        y = df_features['target']
        
        # Manejar valores NaN
        X = X.fillna(0)
        
        print(f"✅ Datos preparados: {len(X)} muestras, {len(feature_columns)} features")
        return X, y
    
    def train(self, X: pd.DataFrame, y: pd.Series) -> Dict:
        """
        Entrenar modelo
        
        Args:
            X: Features
            y: Target
        
        Returns:
            Diccionario con métricas de evaluación
        """
        print("Entrenando modelo...")
        
        # Verificar cantidad de datos
        if len(X) < MLConfig.MIN_TRAINING_SAMPLES:
            print(f"⚠️ Datos insuficientes: {len(X)} < {MLConfig.MIN_TRAINING_SAMPLES}")
            print("   Se requieren más datos históricos para entrenar el modelo")
            return {}
        
        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=MLConfig.TEST_SIZE,
            random_state=MLConfig.RANDOM_STATE,
            stratify=y if len(y.unique()) > 1 else None
        )
        
        print(f"   Train: {len(X_train)} muestras")
        print(f"   Test: {len(X_test)} muestras")
        
        # Escalar features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Entrenar modelo
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=MLConfig.RANDOM_STATE,
            n_jobs=-1
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluar
        y_pred = self.model.predict(X_test_scaled)
        y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]
        
        # Métricas
        accuracy = accuracy_score(y_test, y_pred)
        
        metrics = {
            'accuracy': accuracy,
            'classification_report': classification_report(y_test, y_pred),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
            'feature_importance': dict(zip(
                self.feature_names,
                self.model.feature_importances_
            ))
        }
        
        # AUC-ROC si hay ambas clases
        if len(y_test.unique()) > 1:
            metrics['roc_auc'] = roc_auc_score(y_test, y_pred_proba)
        
        print(f"✅ Modelo entrenado")
        print(f"   Accuracy: {accuracy:.4f}")
        if 'roc_auc' in metrics:
            print(f"   ROC-AUC: {metrics['roc_auc']:.4f}")
        
        # Mostrar features más importantes
        print("\n   Top 5 features más importantes:")
        sorted_features = sorted(
            metrics['feature_importance'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        for feature, importance in sorted_features[:5]:
            print(f"      {feature}: {importance:.4f}")
        
        return metrics
    
    def save_model(self):
        """Guardar modelo entrenado"""
        if self.model is None:
            print("⚠️ No hay modelo entrenado para guardar")
            return
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'trained_at': datetime.now().isoformat()
        }
        
        joblib.dump(model_data, self.model_path)
        print(f"✅ Modelo guardado en: {self.model_path}")
    
    def load_model(self):
        """Cargar modelo entrenado"""
        if not self.model_path.exists():
            print(f"⚠️ No se encontró modelo en: {self.model_path}")
            return False
        
        model_data = joblib.load(self.model_path)
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        
        print(f"✅ Modelo cargado desde: {self.model_path}")
        print(f"   Entrenado el: {model_data.get('trained_at', 'N/A')}")
        return True
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predecir probabilidad de falla
        
        Args:
            X: Features
        
        Returns:
            Array con probabilidades
        """
        if self.model is None:
            raise ValueError("Modelo no entrenado. Llama a train() o load_model() primero.")
        
        # Asegurar que tenga las mismas features
        X = X[self.feature_names]
        X = X.fillna(0)
        
        # Escalar
        X_scaled = self.scaler.transform(X)
        
        # Predecir probabilidad
        probas = self.model.predict_proba(X_scaled)[:, 1]
        
        return probas


def main():
    """Función principal para entrenar el modelo"""
    print("=" * 60)
    print("ENTRENAMIENTO DE MODELO DE PREDICCIÓN DE FALLAS")
    print("=" * 60)
    
    # Crear modelo
    model = FailurePredictionModel()
    
    # Preparar datos
    X, y = model.prepare_data()
    
    if len(X) < MLConfig.MIN_TRAINING_SAMPLES:
        print("\n❌ No hay suficientes datos para entrenar el modelo")
        print(f"   Se requieren al menos {MLConfig.MIN_TRAINING_SAMPLES} muestras")
        return
    
    # Entrenar
    metrics = model.train(X, y)
    
    if metrics:
        # Guardar modelo
        model.save_model()
        
        print("\n" + "=" * 60)
        print("ENTRENAMIENTO COMPLETADO")
        print("=" * 60)
    else:
        print("\n❌ No se pudo entrenar el modelo")


if __name__ == '__main__':
    main()

