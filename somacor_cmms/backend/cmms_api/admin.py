# cmms_api/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    Roles, Usuarios, TiposEquipo, Faenas, EstadosEquipo,
    Equipos, ChecklistTemplate, ChecklistCategory, ChecklistItem,
    ChecklistInstance, ChecklistAnswer
)

# --- Personalización del Panel de Administración ---

class UsuariosInline(admin.StackedInline):
    model = Usuarios
    can_delete = False
    verbose_name_plural = 'Perfil de Usuario CMMS'
    fields = ('idrol', 'departamento') # Removed 'idespecialidad', 'telefono', 'cargo' as they are not in the current Usuarios model

class UserAdmin(BaseUserAdmin):
    inlines = (UsuariosInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_rol')

    @admin.display(description='Rol')
    def get_rol(self, obj):
        try:
            return obj.usuarios.idrol.nombrerol
        except Usuarios.DoesNotExist:
            return 'No asignado'

admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# --- Paneles de Administración Personalizados ---

@admin.register(Equipos)
class EquiposAdmin(admin.ModelAdmin):
    list_display = ('nombreequipo', 'codigointerno', 'idtipoequipo', 'idfaenaactual', 'idestadoactual', 'activo')
    list_filter = ('idtipoequipo', 'idfaenaactual', 'idestadoactual', 'activo')
    search_fields = ('nombreequipo', 'codigointerno', 'marca', 'modelo')

# --- Registros Simples para los Demás Modelos ---
admin.site.register(Roles)
admin.site.register(Faenas)
admin.site.register(TiposEquipo)
admin.site.register(EstadosEquipo)

# Registering new Checklist models
@admin.register(ChecklistTemplate)
class ChecklistTemplateAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo_equipo', 'activo')
    list_filter = ('tipo_equipo', 'activo')
    search_fields = ('nombre',)

@admin.register(ChecklistCategory)
class ChecklistCategoryAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'template', 'orden')
    list_filter = ('template',)
    search_fields = ('nombre',)

@admin.register(ChecklistItem)
class ChecklistItemAdmin(admin.ModelAdmin):
    list_display = ('texto', 'category', 'es_critico', 'orden')
    list_filter = ('category', 'es_critico')
    search_fields = ('texto',)

@admin.register(ChecklistInstance)
class ChecklistInstanceAdmin(admin.ModelAdmin):
    list_display = ('template', 'equipo', 'operador', 'fecha_inspeccion', 'horometro_inspeccion')
    list_filter = ('template', 'equipo', 'operador', 'fecha_inspeccion')
    search_fields = ('equipo__nombreequipo', 'operador__username')

@admin.register(ChecklistAnswer)
class ChecklistAnswerAdmin(admin.ModelAdmin):
    list_display = ('instance', 'item', 'estado')
    list_filter = ('instance__template', 'item__category', 'estado')
    search_fields = ('instance__equipo__nombreequipo', 'item__texto')


