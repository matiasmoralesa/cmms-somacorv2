"""
URLs V2 - Rutas optimizadas para la API V2
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views_v2

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
router.register(r'roles', views_v2.RolesViewSet)

urlpatterns = [
    # APIs principales
    path('', include(router.urls)),
]