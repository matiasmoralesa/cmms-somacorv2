import React, { useState, useEffect } from 'react';
import { X, Save, User, Mail, Phone, Shield } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { usuariosServiceReal, rolesServiceReal } from '@/services/apiServiceReal';

interface User {
  id?: number;
  username: string;
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  role: string;
  isActive: boolean;
}

interface CreateUserFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  userData?: User;
}

const CreateUserForm: React.FC<CreateUserFormProps> = ({
  isOpen,
  onClose,
  onSuccess,
  userData
}) => {
  const isEditMode = Boolean(userData);
  const [formData, setFormData] = useState<User>({
    username: '',
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    role: 'Usuario',
    isActive: true
  });
  const [roles, setRoles] = useState<Array<{id: number, nombre: string}>>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (userData) {
      setFormData(userData);
    } else {
      setFormData({
        username: '',
        firstName: '',
        lastName: '',
        email: '',
        phone: '',
        role: 'Usuario',
        isActive: true
      });
    }
  }, [userData, isOpen]);

  useEffect(() => {
    if (isOpen) {
      loadRoles();
    }
  }, [isOpen]);

  const loadRoles = async () => {
    try {
      const rolesData = await rolesServiceReal.getAll();
      const rolesMapeados = (rolesData.results || []).map((rol: any) => ({
        id: rol.idrol,
        nombre: rol.nombrerol
      }));
      setRoles(rolesMapeados);
    } catch (err) {
      console.error('Error loading roles:', err);
      // Usar roles por defecto si falla la carga
      setRoles([
        { id: 1, nombre: 'Usuario' },
        { id: 2, nombre: 'Técnico' },
        { id: 3, nombre: 'Supervisor' },
        { id: 4, nombre: 'Administrador' }
      ]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Preparar datos para enviar al backend
      const userDataToSend = {
        nombres: formData.firstName,
        apellidos: formData.lastName,
        correoelectronico: formData.email,
        telefonocontacto: formData.phone || null,
        activo: formData.isActive,
        // El backend manejará el username y password
      };

      console.log('[USUARIOS] Guardando usuario:', userDataToSend);
      
      // TODO: Implementar endpoint de creación de usuarios en el backend
      // await usuariosServiceReal.create(userDataToSend);
      
      // Por ahora, simular el guardado
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      console.log('[USUARIOS] Usuario guardado exitosamente');
      
      onSuccess();
      onClose();
    } catch (err) {
      setError('Error al guardar el usuario');
      console.error('[USUARIOS] Error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <div>
            <CardTitle className="text-2xl">
              {isEditMode ? 'Editar Usuario' : 'Nuevo Usuario'}
            </CardTitle>
            <CardDescription>
              {isEditMode ? 'Modifica los datos del usuario' : 'Crea un nuevo usuario en el sistema'}
            </CardDescription>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-lg">
                <p className="text-sm text-destructive">{error}</p>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="username">Nombre de Usuario *</Label>
                <Input
                  id="username"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  placeholder="Ej: juan.perez"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Correo Electrónico *</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="Ej: juan.perez@somacor.com"
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="firstName">Nombre *</Label>
                <Input
                  id="firstName"
                  value={formData.firstName}
                  onChange={(e) => setFormData({ ...formData, firstName: e.target.value })}
                  placeholder="Ej: Juan"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="lastName">Apellido *</Label>
                <Input
                  id="lastName"
                  value={formData.lastName}
                  onChange={(e) => setFormData({ ...formData, lastName: e.target.value })}
                  placeholder="Ej: Pérez"
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="phone">Teléfono</Label>
                <Input
                  id="phone"
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  placeholder="Ej: +56 9 1234 5678"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="role">Rol *</Label>
                <Select
                  value={formData.role}
                  onValueChange={(value) => setFormData({ ...formData, role: value })}
                >
                  <SelectTrigger id="role">
                    <SelectValue placeholder="Selecciona rol" />
                  </SelectTrigger>
                  <SelectContent>
                    {roles.map((rol) => (
                      <SelectItem key={rol.id} value={rol.nombre}>
                        <div className="flex items-center gap-2">
                          <Shield className="h-4 w-4" />
                          {rol.nombre}
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="isActive"
                checked={formData.isActive}
                onChange={(e) => setFormData({ ...formData, isActive: e.target.checked })}
                className="h-4 w-4 rounded border-gray-300"
              />
              <Label htmlFor="isActive" className="text-sm font-normal cursor-pointer">
                Usuario activo
              </Label>
            </div>

            <div className="flex justify-end gap-3 pt-4 border-t">
              <Button type="button" variant="outline" onClick={onClose} disabled={loading}>
                Cancelar
              </Button>
              <Button type="submit" disabled={loading}>
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Guardando...
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4 mr-2" />
                    {isEditMode ? 'Actualizar' : 'Crear'} Usuario
                  </>
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default CreateUserForm;

