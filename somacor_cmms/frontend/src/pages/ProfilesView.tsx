import React, { useState, useEffect } from 'react';
import { 
  Users, 
  Plus, 
  Search, 
  Filter,
  User,
  Mail,
  Shield,
  CheckCircle,
  XCircle,
  Edit,
  Trash2,
  Eye,
  Calendar,
  Building
} from 'lucide-react';
import { PageLayout, PageHeader, StatsGrid, ContentGrid } from '@/components/layout/PageLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import CreateUserForm from '@/components/forms/CreateUserForm';
import { perfilesService } from '@/services/perfilesService';

// =================================================================================
// TIPOS DE DATOS
// =================================================================================

interface UserProfile {
  id: number;
  username: string;
  firstName: string;
  lastName: string;
  email: string;
  role: string;
  department: string;
  isActive: boolean;
  lastLogin: string;
  createdAt: string;
  avatar?: string;
}

interface UserStats {
  totalUsers: number;
  activeUsers: number;
  inactiveUsers: number;
  adminUsers: number;
  technicianUsers: number;
}

// =================================================================================
// COMPONENTE PRINCIPAL
// =================================================================================

const ProfilesView: React.FC = () => {
  const [users, setUsers] = useState<UserProfile[]>([]);
  const [stats, setStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedUser, setSelectedUser] = useState<UserProfile | null>(null);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showEditForm, setShowEditForm] = useState(false);

  // Datos de ejemplo para el diseño
  const mockUsers: UserProfile[] = [
    {
      id: 1,
      username: 'jperez',
      firstName: 'Juan',
      lastName: 'Pérez',
      email: 'juan.perez@somacor.com',
      role: 'Técnico',
      department: 'Mantenimiento',
      isActive: true,
      lastLogin: '2024-10-15',
      createdAt: '2024-01-15'
    },
    {
      id: 2,
      username: 'mgarcia',
      firstName: 'María',
      lastName: 'García',
      email: 'maria.garcia@somacor.com',
      role: 'Supervisor',
      department: 'Mantenimiento',
      isActive: true,
      lastLogin: '2024-10-14',
      createdAt: '2024-02-20'
    },
    {
      id: 3,
      username: 'clopez',
      firstName: 'Carlos',
      lastName: 'López',
      email: 'carlos.lopez@somacor.com',
      role: 'Técnico',
      department: 'Mantenimiento',
      isActive: true,
      lastLogin: '2024-10-13',
      createdAt: '2024-03-10'
    },
    {
      id: 4,
      username: 'amartinez',
      firstName: 'Ana',
      lastName: 'Martínez',
      email: 'ana.martinez@somacor.com',
      role: 'Administrador',
      department: 'IT',
      isActive: true,
      lastLogin: '2024-10-15',
      createdAt: '2024-01-05'
    },
    {
      id: 5,
      username: 'prodriguez',
      firstName: 'Pedro',
      lastName: 'Rodríguez',
      email: 'pedro.rodriguez@somacor.com',
      role: 'Técnico',
      department: 'Mantenimiento',
      isActive: false,
      lastLogin: '2024-09-20',
      createdAt: '2024-04-15'
    }
  ];

  const mockStats: UserStats = {
    totalUsers: 25,
    activeUsers: 22,
    inactiveUsers: 3,
    adminUsers: 3,
    technicianUsers: 18
  };

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Cargar usuarios desde el backend
      const response = await fetch('http://localhost:8000/api/v2/usuarios/');
      const data = await response.json();
      const usuarios = data.results || data || [];
      
      const usuariosTransformados = usuarios.map((usuario: any) => ({
        id: usuario.user?.id || usuario.id,
        username: usuario.user?.username || usuario.username,
        firstName: usuario.user?.first_name || '',
        lastName: usuario.user?.last_name || '',
        email: usuario.user?.email || usuario.email || '',
        role: usuario.rol_nombre || usuario.role || 'Usuario',
        department: usuario.departamento || 'Sin departamento',
        isActive: usuario.user?.is_active !== undefined ? usuario.user.is_active : true,
        lastLogin: usuario.user?.last_login?.split('T')[0] || 'Nunca',
        createdAt: usuario.user?.date_joined?.split('T')[0] || new Date().toISOString().split('T')[0]
      }));
      
      setUsers(usuariosTransformados);
      
      const activeUsers = usuariosTransformados.filter((u: any) => u.isActive).length;
      const adminUsers = usuariosTransformados.filter((u: any) => 
        u.role?.toLowerCase().includes('admin')
      ).length;
      const technicianUsers = usuariosTransformados.filter((u: any) => 
        u.role?.toLowerCase().includes('técnico') || u.role?.toLowerCase().includes('tecnico')
      ).length;
      
      setStats({
        totalUsers: usuariosTransformados.length,
        activeUsers,
        inactiveUsers: usuariosTransformados.length - activeUsers,
        adminUsers,
        technicianUsers
      });
      
      console.log('✅ Usuarios cargados:', usuariosTransformados.length);
    } catch (err) {
      console.error("❌ Error fetching users:", err);
      setError('No se pudo cargar la información de usuarios.');
      setUsers([]);
      setStats({ totalUsers: 0, activeUsers: 0, inactiveUsers: 0, adminUsers: 0, technicianUsers: 0 });
      } catch (err) {
        console.error("Error fetching users data:", err);
        setError("No se pudo cargar la información de usuarios.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Filtrar usuarios
  const filteredUsers = users.filter(user => {
    const matchesSearch = user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.firstName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.lastName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesRole = roleFilter === 'all' || user.role === roleFilter;
    const matchesStatus = statusFilter === 'all' || 
                         (statusFilter === 'active' && user.isActive) ||
                         (statusFilter === 'inactive' && !user.isActive);
    
    return matchesSearch && matchesRole && matchesStatus;
  });

  // Handlers para acciones
  const handleViewProfile = (user: UserProfile) => {
    setSelectedUser(user);
    console.log('Ver perfil de:', user.username);
  };

  const handleEdit = (user: UserProfile) => {
    setSelectedUser(user);
    setShowEditForm(true);
  };

  const handleDelete = (user: UserProfile) => {
    setSelectedUser(user);
    setShowDeleteDialog(true);
  };

  const confirmDelete = () => {
    if (selectedUser) {
      console.log('Eliminar usuario:', selectedUser.username);
      setShowDeleteDialog(false);
      setSelectedUser(null);
    }
  };

  // Obtener badge de rol
  const getRoleBadge = (role: string) => {
    switch (role) {
      case 'Administrador':
        return <Badge variant="destructive"><Shield className="h-3 w-3 mr-1" />Administrador</Badge>;
      case 'Supervisor':
        return <Badge variant="default" className="bg-purple-100 text-purple-800"><User className="h-3 w-3 mr-1" />Supervisor</Badge>;
      case 'Técnico':
        return <Badge variant="default" className="bg-blue-100 text-blue-800"><User className="h-3 w-3 mr-1" />Técnico</Badge>;
      default:
        return <Badge variant="secondary">{role}</Badge>;
    }
  };

  // Obtener badge de estado
  const getStatusBadge = (isActive: boolean) => {
    return isActive ? (
      <Badge variant="default" className="bg-green-100 text-green-800">
        <CheckCircle className="h-3 w-3 mr-1" />Activo
      </Badge>
    ) : (
      <Badge variant="destructive">
        <XCircle className="h-3 w-3 mr-1" />Inactivo
      </Badge>
    );
  };

  // Obtener iniciales del usuario
  const getUserInitials = (firstName: string, lastName: string) => {
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
  };

  if (loading) {
    return (
      <PageLayout>
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      </PageLayout>
    );
  }

  if (error) {
    return (
      <PageLayout>
        <div className="p-8 text-center text-destructive bg-destructive/10 rounded-lg">
          {error}
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <PageHeader 
        title="Gestión de Usuarios" 
        subtitle="Administración de perfiles y permisos del sistema"
      >
        <Button onClick={() => setShowCreateForm(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Nuevo Usuario
        </Button>
      </PageHeader>

      {/* Tarjetas de estadísticas */}
      <StatsGrid>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Usuarios</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.totalUsers}</div>
            <p className="text-xs text-muted-foreground">
              Usuarios registrados
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Usuarios Activos</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats?.activeUsers}</div>
            <p className="text-xs text-muted-foreground">
              {stats ? Math.round((stats.activeUsers / stats.totalUsers) * 100) : 0}% del total
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Técnicos</CardTitle>
            <User className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{stats?.technicianUsers}</div>
            <p className="text-xs text-muted-foreground">
              Personal técnico
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Administradores</CardTitle>
            <Shield className="h-4 w-4 text-destructive" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-destructive">{stats?.adminUsers}</div>
            <p className="text-xs text-muted-foreground">
              Acceso administrativo
            </p>
          </CardContent>
        </Card>
      </StatsGrid>

      {/* Lista de usuarios */}
      <ContentGrid>
        <Card>
          <CardHeader>
            <div className="flex flex-col md:flex-row gap-4 justify-between items-start md:items-center">
              <div>
                <CardTitle>Lista de Usuarios</CardTitle>
                <CardDescription>
                  Gestión de perfiles y permisos de acceso
                </CardDescription>
              </div>
              
              <div className="flex flex-col md:flex-row gap-2 w-full md:w-auto">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Buscar usuario..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 w-full md:w-64"
                  />
                </div>
                
                <Select value={roleFilter} onValueChange={setRoleFilter}>
                  <SelectTrigger className="w-full md:w-48">
                    <SelectValue placeholder="Rol" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todos los roles</SelectItem>
                    <SelectItem value="Administrador">Administrador</SelectItem>
                    <SelectItem value="Supervisor">Supervisor</SelectItem>
                    <SelectItem value="Técnico">Técnico</SelectItem>
                  </SelectContent>
                </Select>

                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger className="w-full md:w-48">
                    <SelectValue placeholder="Estado" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todos los estados</SelectItem>
                    <SelectItem value="active">Activos</SelectItem>
                    <SelectItem value="inactive">Inactivos</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {filteredUsers.map(user => (
                <div key={user.id} className="border rounded-lg p-4 hover:bg-muted/50">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4">
                      {/* Avatar */}
                      <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary font-semibold">
                        {getUserInitials(user.firstName, user.lastName)}
                      </div>
                      
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h4 className="font-medium">{user.firstName} {user.lastName}</h4>
                          <span className="text-sm text-muted-foreground">(@{user.username})</span>
                          {getRoleBadge(user.role)}
                          {getStatusBadge(user.isActive)}
                        </div>
                        
                        <div className="text-sm text-muted-foreground space-y-1">
                          <div className="flex items-center gap-2">
                            <Mail className="h-3 w-3" />
                            {user.email}
                          </div>
                          <div className="flex items-center gap-2">
                            <Building className="h-3 w-3" />
                            {user.department}
                          </div>
                          <div className="flex items-center gap-2">
                            <Calendar className="h-3 w-3" />
                            Último acceso: {user.lastLogin}
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex gap-1 ml-4">
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleViewProfile(user)}
                        title="Ver perfil"
                      >
                        <Eye className="h-3 w-3" />
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleEdit(user)}
                        title="Editar"
                      >
                        <Edit className="h-3 w-3" />
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleDelete(user)}
                        title="Eliminar"
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
              
              {filteredUsers.length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  <Users className="mx-auto h-12 w-12 text-muted-foreground/50" />
                  <h3 className="mt-2 text-sm font-medium">No se encontraron usuarios</h3>
                  <p className="mt-1 text-sm">No hay usuarios que coincidan con los filtros seleccionados.</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </ContentGrid>

      {/* Formulario de creación de usuario */}
      <CreateUserForm
        isOpen={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        onSuccess={() => {
          console.log('Usuario creado exitosamente');
        }}
      />

      {/* Formulario de edición de usuario */}
      {selectedUser && (
        <CreateUserForm
          isOpen={showEditForm}
          onClose={() => {
            setShowEditForm(false);
            setSelectedUser(null);
          }}
          onSuccess={() => {
            console.log('Usuario actualizado exitosamente');
            setShowEditForm(false);
            setSelectedUser(null);
          }}
          userData={selectedUser}
        />
      )}

      {/* Diálogo de confirmación de eliminación */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>¿Estás seguro?</AlertDialogTitle>
            <AlertDialogDescription>
              Esta acción no se puede deshacer. Se eliminará permanentemente el usuario "{selectedUser?.username}".
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction onClick={confirmDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
              Eliminar
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </PageLayout>
  );
};

export default ProfilesView;