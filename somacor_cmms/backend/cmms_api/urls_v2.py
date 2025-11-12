"""
URLs V2 - Rutas optimizadas para la API V2
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views_v2
from .views_checklist import ChecklistWorkflowViewSet

router = DefaultRouter()

# Registrar ViewSets principales
router.register(r'equipos', views_v2.EquiposViewSet)
router.register(r'ordenes-trabajo', views_v2.OrdenesTrabajoViewSet)
router.register(r'dashboard', views_v2.DashboardViewSet, basename='dashboard')
router.register(r'search', views_v2.SearchViewSet, basename='search')

# Registrar ViewSets para formularios
router.register(r'faenas', views_v2.FaenasViewSet)
router.register(r'usuarios', views_v2.UsuariosViewSet)
router.register(r'tipos-equipo', views_v2.TiposEquipoViewSet)
router.register(r'checklist-templates', views_v2.ChecklistTemplateViewSet)
router.register(r'checklist-categories', views_v2.ChecklistCategoryViewSet)
router.register(r'checklist-items', views_v2.ChecklistItemViewSet)
router.register(r'checklist-instance', views_v2.ChecklistInstanceViewSet)
router.register(r'inventario', views_v2.InventarioViewSet, basename='inventario')
router.register(r'categorias-inventario', views_v2.CategoriasInventarioViewSet)
router.register(r'proveedores', views_v2.ProveedoresViewSet)
router.register(r'movimientos-inventario', views_v2.MovimientosInventarioViewSet)
router.register(r'roles', views_v2.RolesViewSet)
router.register(r'tecnicos', views_v2.TecnicosViewSet)
router.register(r'especialidades', views_v2.EspecialidadesViewSet)

# Registrar ViewSets de catálogos
router.register(r'estados-equipo', views_v2.EstadosEquipoViewSet)
router.register(r'estados-orden-trabajo', views_v2.EstadosOrdenTrabajoViewSet)
router.register(r'tipos-mantenimiento-ot', views_v2.TiposMantenimientoOTViewSet)
router.register(r'tipos-tarea', views_v2.TiposTareaViewSet)
router.register(r'tareas-estandar', views_v2.TareasEstandarViewSet)

# Registrar ViewSets de planes de mantenimiento
router.register(r'planes-mantenimiento', views_v2.PlanesMantenimientoViewSet)
router.register(r'detalles-plan-mantenimiento', views_v2.DetallesPlanMantenimientoViewSet)

# Registrar ViewSets de actividades y evidencias
router.register(r'actividades-orden-trabajo', views_v2.ActividadesOrdenTrabajoViewSet)
router.register(r'evidencias-ot', views_v2.EvidenciaOTViewSet)

# Registrar ViewSets de agendas
router.register(r'agendas', views_v2.AgendasViewSet)

# Workflows especializados
router.register(r'checklist-workflow', ChecklistWorkflowViewSet, basename='checklist-workflow')

urlpatterns = [
    # APIs principales con ViewSets registrados en el router
    path('', include(router.urls)),
    
    # NOTA: Los endpoints del dashboard ahora están en DashboardViewSet
    # Accesibles vía:
    # - /api/v2/dashboard/stats/
    # - /api/v2/dashboard/monthly_data/
    # - /api/v2/dashboard/maintenance_types/
    # - /api/v2/dashboard/recent_work_orders/
]