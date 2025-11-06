# cmms_api/permissions.py

from rest_framework import permissions
from .models import Usuarios

class IsAdminRole(permissions.BasePermission):
    """
    Permiso personalizado para permitir acceso solo a usuarios con rol de Admin o Administrador.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        try:
            usuario = Usuarios.objects.get(user=request.user)
            return usuario.idrol.nombrerol in ['Admin', 'Administrador']
        except Usuarios.DoesNotExist:
            return False

class IsSupervisorRole(permissions.BasePermission):
    """
    Permiso personalizado para permitir acceso solo a usuarios con rol de Supervisor.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        try:
            usuario = Usuarios.objects.get(user=request.user)
            return usuario.idrol.nombrerol == 'Supervisor'
        except Usuarios.DoesNotExist:
            return False

class IsOperadorRole(permissions.BasePermission):
    """
    Permiso personalizado para permitir acceso solo a usuarios con rol de Operador.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        try:
            usuario = Usuarios.objects.get(user=request.user)
            return usuario.idrol.nombrerol == 'Operador'
        except Usuarios.DoesNotExist:
            return False

class IsAdminOrSupervisorRole(permissions.BasePermission):
    """
    Permiso personalizado para permitir acceso a usuarios con rol de Admin, Administrador o Supervisor.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        try:
            usuario = Usuarios.objects.get(user=request.user)
            return usuario.idrol.nombrerol in ['Admin', 'Administrador', 'Supervisor']
        except Usuarios.DoesNotExist:
            return False

class IsAnyRole(permissions.BasePermission):
    """
    Permiso personalizado para permitir acceso a cualquier usuario autenticado con rol asignado.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        try:
            usuario = Usuarios.objects.get(user=request.user)
            return usuario.idrol.nombrerol in ['Admin', 'Administrador', 'Supervisor', 'Operador', 'Técnico']
        except Usuarios.DoesNotExist:
            return False

