"""
Sistema de notificaciones de Telegram para Airflow DAGs
"""

import asyncio
from typing import List, Dict, Optional
from telegram import Bot
from loguru import logger
import sys
from pathlib import Path

# Agregar directorios al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'airflow_bot'))
from config.airflow_config import TelegramConfig, LoggingConfig

# Configurar logging
logger.add(
    LoggingConfig.LOG_FILE,
    format=LoggingConfig.FORMAT,
    level=LoggingConfig.LEVEL,
    rotation=LoggingConfig.ROTATION,
    retention=LoggingConfig.RETENTION
)


class TelegramNotifier:
    """Clase para enviar notificaciones vía Telegram desde Airflow"""
    
    def __init__(self, token: str = None):
        """
        Inicializar notificador de Telegram
        
        Args:
            token: Token del bot de Telegram
        """
        self.token = token or TelegramConfig.BOT_TOKEN
        self.bot = Bot(token=self.token)
        logger.info("TelegramNotifier inicializado")
    
    async def _send_message_async(
        self,
        chat_id: int,
        message: str,
        parse_mode: str = 'Markdown'
    ):
        """
        Enviar mensaje de forma asíncrona
        
        Args:
            chat_id: ID del chat de Telegram
            message: Mensaje a enviar
            parse_mode: Modo de parseo (Markdown o HTML)
        """
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=parse_mode
            )
            logger.info(f"Mensaje enviado a chat_id: {chat_id}")
        except Exception as e:
            logger.error(f"Error al enviar mensaje: {str(e)}")
            raise
    
    def send_message(
        self,
        chat_id: int,
        message: str,
        parse_mode: str = 'Markdown'
    ):
        """
        Enviar mensaje (wrapper síncrono para usar en Airflow)
        
        Args:
            chat_id: ID del chat de Telegram
            message: Mensaje a enviar
            parse_mode: Modo de parseo (Markdown o HTML)
        """
        asyncio.run(self._send_message_async(chat_id, message, parse_mode))
    
    def notify_prediction_alert(
        self,
        chat_id: int,
        equipo: Dict,
        probabilidad: float,
        mtbf: float
    ):
        """
        Notificar alerta de predicción de falla
        
        Args:
            chat_id: ID del chat
            equipo: Datos del equipo
            probabilidad: Probabilidad de falla
            mtbf: MTBF del equipo
        """
        message = f"""
🚨 **ALERTA PREDICTIVA**

⚙️ **Equipo:** {equipo.get('nombreequipo', 'N/A')}
🔢 **Código:** {equipo.get('codigointerno', 'N/A')}
📍 **Faena:** {equipo.get('faena_nombre', 'N/A')}

⚠️ **Probabilidad de Falla:** {probabilidad*100:.1f}%
📊 **MTBF Actual:** {mtbf:.1f} días

🔧 **Recomendación:** Programar mantenimiento preventivo urgente

📅 **Fecha:** {asyncio.get_event_loop().time()}
"""
        
        self.send_message(chat_id, message)
        logger.info(f"Alerta predictiva enviada para equipo {equipo.get('idequipo')}")
    
    def notify_preventive_maintenance_created(
        self,
        chat_id: int,
        orden: Dict,
        equipo: Dict,
        tecnico: Dict
    ):
        """
        Notificar creación de orden de mantenimiento preventivo
        
        Args:
            chat_id: ID del chat
            orden: Datos de la orden de trabajo
            equipo: Datos del equipo
            tecnico: Datos del técnico asignado
        """
        message = f"""
📋 **NUEVA ORDEN DE MANTENIMIENTO PREVENTIVO**

🔧 **Orden:** {orden.get('codigoot', 'N/A')}
⚙️ **Equipo:** {equipo.get('nombreequipo', 'N/A')}
👤 **Técnico Asignado:** {tecnico.get('nombreusuario', 'N/A')}

📅 **Fecha Programada:** {orden.get('fechaprogramada', 'N/A')}
⏱️ **Duración Estimada:** {orden.get('duracionestimada', 'N/A')} horas

📍 **Faena:** {equipo.get('faena_nombre', 'N/A')}

✅ La orden ha sido creada automáticamente por el sistema.
"""
        
        self.send_message(chat_id, message)
        logger.info(f"Notificación de mantenimiento preventivo enviada: {orden.get('codigoot')}")
    
    def notify_checklist_critical_items(
        self,
        chat_id: int,
        checklist: Dict,
        items_fallidos: List[Dict],
        equipo: Dict
    ):
        """
        Notificar items críticos fallidos en checklist
        
        Args:
            chat_id: ID del chat
            checklist: Datos del checklist
            items_fallidos: Lista de items fallidos
            equipo: Datos del equipo
        """
        items_text = "\n".join([
            f"   ❌ {item.get('nombre', 'N/A')}"
            for item in items_fallidos[:5]  # Limitar a 5 items
        ])
        
        message = f"""
⚠️ **ITEMS CRÍTICOS FALLIDOS EN CHECKLIST**

📋 **Checklist:** {checklist.get('template_nombre', 'N/A')}
⚙️ **Equipo:** {equipo.get('nombreequipo', 'N/A')}
📅 **Fecha:** {checklist.get('fecha_completado', 'N/A')}

🔴 **Items Fallidos ({len(items_fallidos)}):**
{items_text}

🔧 **Acción:** Se ha generado automáticamente una orden de trabajo correctiva.
"""
        
        self.send_message(chat_id, message)
        logger.info(f"Notificación de checklist crítico enviada: {checklist.get('id')}")
    
    def notify_weekly_report(
        self,
        chat_id: int,
        stats: Dict
    ):
        """
        Notificar reporte semanal
        
        Args:
            chat_id: ID del chat
            stats: Estadísticas del reporte
        """
        message = f"""
📊 **REPORTE SEMANAL - CMMS SOMACOR**

🔧 **Órdenes de Trabajo:**
- Completadas: {stats.get('ordenes_completadas', 0)}
- Pendientes: {stats.get('ordenes_pendientes', 0)}
- En Progreso: {stats.get('ordenes_en_progreso', 0)}

⚙️ **Equipos:**
- Disponibilidad: {stats.get('disponibilidad', 0):.1f}%
- MTBF Promedio: {stats.get('mtbf_promedio', 0):.1f} días
- MTTR Promedio: {stats.get('mttr_promedio', 0):.1f} horas

📈 **KPIs:**
- Cumplimiento: {stats.get('cumplimiento', 0):.1f}%
- Eficiencia: {stats.get('eficiencia', 0):.1f}%

⚠️ **Alertas Activas:** {stats.get('alertas_activas', 0)}

📅 Semana del {stats.get('fecha_inicio', 'N/A')} al {stats.get('fecha_fin', 'N/A')}
"""
        
        self.send_message(chat_id, message)
        logger.info("Reporte semanal enviado")
    
    def notify_technician_assignment(
        self,
        chat_id: int,
        orden: Dict,
        tecnico: Dict,
        equipo: Dict
    ):
        """
        Notificar asignación de orden a técnico
        
        Args:
            chat_id: ID del chat
            orden: Datos de la orden
            tecnico: Datos del técnico
            equipo: Datos del equipo
        """
        prioridad_emoji = {
            'Urgente': '🔴',
            'Alta': '🟠',
            'Media': '🟡',
            'Baja': '🟢'
        }.get(orden.get('prioridad', ''), '⚪')
        
        message = f"""
📋 **NUEVA ORDEN ASIGNADA**

👤 **Técnico:** {tecnico.get('nombreusuario', 'N/A')}

🔧 **Orden:** {orden.get('codigoot', 'N/A')}
⚙️ **Equipo:** {equipo.get('nombreequipo', 'N/A')}
📍 **Faena:** {equipo.get('faena_nombre', 'N/A')}

{prioridad_emoji} **Prioridad:** {orden.get('prioridad', 'N/A')}
🔨 **Tipo:** {orden.get('tipo_mantenimiento_nombre', 'N/A')}

📝 **Descripción:**
{orden.get('descripcionproblemareportado', 'N/A')}

⏱️ **Duración Estimada:** {orden.get('duracionestimada', 'N/A')} horas
"""
        
        self.send_message(chat_id, message)
        logger.info(f"Notificación de asignación enviada a técnico {tecnico.get('idusuario')}")
    
    def notify_dag_failure(
        self,
        chat_id: int,
        dag_id: str,
        task_id: str,
        error_message: str
    ):
        """
        Notificar falla en ejecución de DAG
        
        Args:
            chat_id: ID del chat
            dag_id: ID del DAG
            task_id: ID de la tarea
            error_message: Mensaje de error
        """
        message = f"""
❌ **ERROR EN DAG DE AIRFLOW**

🔧 **DAG:** {dag_id}
📋 **Tarea:** {task_id}

⚠️ **Error:**
```
{error_message[:500]}
```

🔍 Revisa los logs de Airflow para más detalles.
"""
        
        self.send_message(chat_id, message, parse_mode='Markdown')
        logger.error(f"Notificación de falla de DAG enviada: {dag_id}/{task_id}")
    
    def notify_batch(
        self,
        chat_ids: List[int],
        message: str,
        parse_mode: str = 'Markdown'
    ):
        """
        Enviar notificación a múltiples usuarios
        
        Args:
            chat_ids: Lista de IDs de chat
            message: Mensaje a enviar
            parse_mode: Modo de parseo
        """
        for chat_id in chat_ids:
            try:
                self.send_message(chat_id, message, parse_mode)
            except Exception as e:
                logger.error(f"Error al enviar mensaje a {chat_id}: {str(e)}")


# Instancia singleton del notificador
telegram_notifier = TelegramNotifier()


if __name__ == '__main__':
    # Prueba del notificador
    notifier = TelegramNotifier()
    
    # Ejemplo de notificación de prueba
    test_message = """
🤖 **Prueba de Notificación**

Este es un mensaje de prueba del sistema de notificaciones de Telegram para CMMS Somacor v2.

✅ Si recibes este mensaje, el sistema está funcionando correctamente.
"""
    
    # Reemplazar con un chat_id real para probar
    # notifier.send_message(123456789, test_message)
    
    print("Notificador de Telegram listo para usar")

