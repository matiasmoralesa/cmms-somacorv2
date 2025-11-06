# cmms_api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import urls_v2
# from .views_test import test_view, test_models
# from .views_maintenance import MantenimientoWorkflowViewSet
# from .views_checklist import ChecklistWorkflowViewSet
# from .views_dashboard import (
#     dashboard_stats, dashboard_recent_work_orders,
#     dashboard_monthly_data, dashboard_maintenance_types
# )
# from .views_equipos import (
#     equipos_list, equipos_categories, equipos_states, equipos_stats
# )
# from .views_ordenes import (
#     ordenes_list, ordenes_stats, ordenes_filters, ordenes_by_equipment
# )

router = DefaultRouter()

# Registros de la API básica
router.register(r'users', views.UserViewSet)
router.register(r'roles', views.RolViewSet)
router.register(r'faenas', views.FaenaViewSet)
router.register(r'tipos-equipo', views.TipoEquipoViewSet)
router.register(r'estados-equipo', views.EstadoEquipoViewSet)
router.register(r'equipos', views.EquipoViewSet)

# Checklist API routes - temporalmente deshabilitados
# router.register(r'checklist-templates', views.ChecklistTemplateViewSet)
# router.register(r'checklist-categories', views.ChecklistCategoryViewSet)
# router.register(r'checklist-items', views.ChecklistItemViewSet)
# router.register(r'checklist-instances', views.ChecklistInstanceViewSet)
# router.register(r'checklist-answers', views.ChecklistAnswerViewSet)

# Agenda de Mantenimiento Preventivo API routes - temporalmente deshabilitados
# router.register(r'tipos-tarea', views.TipoTareaViewSet)
# router.register(r'tareas-estandar', views.TareaEstandarViewSet)
# router.register(r'planes-mantenimiento', views.PlanMantenimientoViewSet)
# router.register(r'detalles-plan-mantenimiento', views.DetallesPlanMantenimientoViewSet)
# router.register(r'tipos-mantenimiento-ot', views.TiposMantenimientoOTViewSet)
# router.register(r'estados-orden-trabajo', views.EstadosOrdenTrabajoViewSet)

# Registro de Mantenimientos API routes - temporalmente deshabilitados
# router.register(r'ordenes-trabajo', views.OrdenTrabajoViewSet)
# router.register(r'actividades-ot', views.ActividadOrdenTrabajoViewSet)
# router.register(r'evidencias-ot', views.EvidenciaOTViewSet)
# router.register(r'agendas', views.AgendaViewSet)

# Workflows especializados - temporalmente deshabilitados
# router.register(r'mantenimiento-workflow', MantenimientoWorkflowViewSet, basename='mantenimiento-workflow')
# router.register(r'checklist-workflow', ChecklistWorkflowViewSet, basename='checklist-workflow')

# URLs de la API (legacy - mantener para compatibilidad)
urlpatterns = [
    path('', include(router.urls)),  # Habilitado para APIs básicas
    # Rutas de prueba - temporalmente deshabilitadas
    # path('test/', test_view, name='test_view'),
    # path('test-models/', test_models, name='test_models'),
    # Rutas de autenticación
    path('login/', views.CustomAuthToken.as_view(), name='auth_token'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    # Dashboard endpoints - temporalmente deshabilitados
    # path('dashboard/stats/', dashboard_stats, name='dashboard_stats'),
    # path('dashboard/recent-work-orders/', dashboard_recent_work_orders, name='dashboard_recent_work_orders'),
    # path('dashboard/monthly-data/', dashboard_monthly_data, name='dashboard_monthly_data'),
    # path('dashboard/maintenance-types/', dashboard_maintenance_types, name='dashboard_maintenance_types'),

    # Equipos endpoints - temporalmente deshabilitados
    # path('equipos/list/', equipos_list, name='equipos_list'),
    # path('equipos/categories/', equipos_categories, name='equipos_categories'),
    # path('equipos/states/', equipos_states, name='equipos_states'),
    # path('equipos/stats/', equipos_stats, name='equipos_stats'),

    # Órdenes de trabajo endpoints - temporalmente deshabilitados
    # path('ordenes/list/', ordenes_list, name='ordenes_list'),
    # path('ordenes/stats/', ordenes_stats, name='ordenes_stats'),
    # path('ordenes/filters/', ordenes_filters, name='ordenes_filters'),
    # path('ordenes/equipment/<int:equipment_id>/', ordenes_by_equipment, name='ordenes_by_equipment'),
    
    # Endpoints simples para testing (sin autenticación)
    path('dashboard/stats/', views.dashboard_stats_simple, name='dashboard_stats_simple'),
    path('dashboard/recent-work-orders/', views.dashboard_recent_simple, name='dashboard_recent_simple'),
    
    # API versioning
    # path('v1/', include('cmms_api.v1.urls')),
    path('v2/', include(urls_v2.urlpatterns)),  # API V2
]

