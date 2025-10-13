"""
API v1 URL configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from cmms_api import views
from cmms_api.views_maintenance import MantenimientoWorkflowViewSet
from cmms_api.views_checklist import ChecklistWorkflowViewSet
from cmms_api.views_dashboard import (
    dashboard_stats, dashboard_recent_work_orders, 
    dashboard_monthly_data, dashboard_maintenance_types
)
from cmms_api.views_equipos import (
    equipos_list, equipos_categories, equipos_states, equipos_stats
)
from cmms_api.views_ordenes import (
    ordenes_list, ordenes_stats, ordenes_filters, ordenes_by_equipment
)
from cmms_api.views_bot import (
    bot_search_equipment, bot_create_work_order, bot_get_work_order_status,
    bot_get_equipment_info, bot_get_dashboard_summary, bot_webhook_receiver
)

router = DefaultRouter()

# Registros de la API básica
router.register(r'users', views.UserViewSet)
router.register(r'roles', views.RolViewSet)
router.register(r'faenas', views.FaenaViewSet)
router.register(r'tipos-equipo', views.TipoEquipoViewSet)
router.register(r'estados-equipo', views.EstadoEquipoViewSet)
router.register(r'equipos', views.EquipoViewSet)

# Checklist API routes
router.register(r'checklist-templates', views.ChecklistTemplateViewSet)
router.register(r'checklist-categories', views.ChecklistCategoryViewSet)
router.register(r'checklist-items', views.ChecklistItemViewSet)
router.register(r'checklist-instances', views.ChecklistInstanceViewSet)
router.register(r'checklist-answers', views.ChecklistAnswerViewSet)

# Agenda de Mantenimiento Preventivo API routes
router.register(r'tipos-tarea', views.TipoTareaViewSet)
router.register(r'tareas-estandar', views.TareaEstandarViewSet)
router.register(r'planes-mantenimiento', views.PlanMantenimientoViewSet)
router.register(r'detalles-plan-mantenimiento', views.DetallesPlanMantenimientoViewSet)
router.register(r'tipos-mantenimiento-ot', views.TiposMantenimientoOTViewSet)
router.register(r'estados-orden-trabajo', views.EstadosOrdenTrabajoViewSet)

# Registro de Mantenimientos API routes
router.register(r'ordenes-trabajo', views.OrdenTrabajoViewSet)
router.register(r'actividades-ot', views.ActividadOrdenTrabajoViewSet)
router.register(r'evidencias-ot', views.EvidenciaOTViewSet)
router.register(r'agendas', views.AgendaViewSet)

# Workflows especializados
router.register(r'mantenimiento-workflow', MantenimientoWorkflowViewSet, basename='mantenimiento-workflow')
router.register(r'checklist-workflow', ChecklistWorkflowViewSet, basename='checklist-workflow')

# URLs de la API v1
urlpatterns = [
    path('', include(router.urls)),
    
    # Rutas de autenticación
    path('auth/login/', views.CustomAuthToken.as_view(), name='auth_token'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    
    # Dashboard endpoints
    path('dashboard/stats/', dashboard_stats, name='dashboard_stats'),
    path('dashboard/recent-work-orders/', dashboard_recent_work_orders, name='dashboard_recent_work_orders'),
    path('dashboard/monthly-data/', dashboard_monthly_data, name='dashboard_monthly_data'),
    path('dashboard/maintenance-types/', dashboard_maintenance_types, name='dashboard_maintenance_types'),
    
    # Equipos endpoints
    path('equipos/list/', equipos_list, name='equipos_list'),
    path('equipos/categories/', equipos_categories, name='equipos_categories'),
    path('equipos/states/', equipos_states, name='equipos_states'),
    path('equipos/stats/', equipos_stats, name='equipos_stats'),
    
    # Órdenes de trabajo endpoints
    path('ordenes/list/', ordenes_list, name='ordenes_list'),
    path('ordenes/stats/', ordenes_stats, name='ordenes_stats'),
    path('ordenes/filters/', ordenes_filters, name='ordenes_filters'),
    path('ordenes/equipment/<int:equipment_id>/', ordenes_by_equipment, name='ordenes_by_equipment'),
    
    # Bot integration endpoints
    path('bot/equipment/search/', bot_search_equipment, name='bot_search_equipment'),
    path('bot/work-orders/create/', bot_create_work_order, name='bot_create_work_order'),
    path('bot/work-orders/<int:work_order_id>/status/', bot_get_work_order_status, name='bot_get_work_order_status'),
    path('bot/equipment/<int:equipment_id>/info/', bot_get_equipment_info, name='bot_get_equipment_info'),
    path('bot/dashboard/summary/', bot_get_dashboard_summary, name='bot_get_dashboard_summary'),
    path('bot/webhook/', bot_webhook_receiver, name='bot_webhook_receiver'),
]
