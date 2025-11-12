import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  Search, 
  Package, 
  AlertTriangle, 
  DollarSign,
  Eye,
  Edit,
  Trash2,
  MapPin,
  Clock
} from 'lucide-react';
import { PageLayout, PageHeader, StatsGrid } from '@/components/layout/PageLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import CreateInventarioForm from '@/components/forms/CreateInventarioForm';
import { inventarioService } from '@/services/inventarioService';

interface InventoryItem {
  id: string;
  code: string;
  name: string;
  category: string;
  quantity: number;
  minStock: number;
  status: 'normal' | 'low' | 'high' | 'out';
  location: string;
  unitCost: number;
}

const InventarioView: React.FC = () => {
  const [inventoryItems, setInventoryItems] = useState<InventoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedItem, setSelectedItem] = useState<InventoryItem | null>(null);
  const [showEditForm, setShowEditForm] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  // Calcular estadísticas dinámicamente
  const stats = {
    totalItems: inventoryItems.length,
    lowStock: inventoryItems.filter(item => item.status === 'low').length,
    outOfStock: inventoryItems.filter(item => item.status === 'out').length,
    totalValue: inventoryItems.reduce((sum, item) => sum + (item.quantity * item.unitCost), 0)
  };

  // Items con stock bajo para alertas
  const lowStockItems = inventoryItems.filter(item => item.status === 'low' || item.status === 'out');

  useEffect(() => {
    fetchInventory();
  }, []);

  const fetchInventory = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Cargar datos reales del backend
      try {
        const response = await inventarioService.getAll();
        const items = response.results || response.data || response || [];
        
        // Validar que sea un array
        if (!Array.isArray(items)) {
          console.warn('Respuesta no es un array:', items);
          setInventoryItems([]);
          return;
        }
        
        const itemsTransformados: InventoryItem[] = items.map((item: any) => {
          // Usar los nombres correctos de campos del backend
          const cantidad = parseFloat(item.cantidad || 0);
          const stockMinimo = parseFloat(item.stockminimo || 10);
          const stockMaximo = item.stockmaximo ? parseFloat(item.stockmaximo) : null;
          
          // Determinar estado del stock basado en estado_stock del backend
          let status: 'normal' | 'low' | 'high' | 'out' = 'normal';
          if (item.estado_stock === 'sin_stock') {
            status = 'out';
          } else if (item.estado_stock === 'stock_bajo') {
            status = 'low';
          } else if (item.estado_stock === 'stock_alto') {
            status = 'high';
          } else {
            status = 'normal';
          }
          
          return {
            id: item.idinventario?.toString() || item.id?.toString(),
            code: item.codigointerno || 'SIN-COD',
            name: item.nombreitem || 'Sin nombre',
            category: item.categoria_nombre || 'General',
            quantity: cantidad,
            minStock: stockMinimo,
            status: status,
            location: item.ubicacion || 'Sin ubicación',
            unitCost: parseFloat(item.costounitario || 0)
          };
        });
        
        setInventoryItems(itemsTransformados);
        console.log('✅ Inventario cargado:', itemsTransformados.length, 'items');
      } catch (apiErr: any) {
        console.error('❌ Error al cargar inventario:', apiErr);
        setError(`Error al cargar el inventario: ${apiErr.message || 'Error desconocido'}`);
        setInventoryItems([]);
      }
    } catch (err: any) {
      console.error("❌ Error general:", err);
      setError(`Error: ${err.message || 'Error desconocido'}`);
      setInventoryItems([]);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'normal': return <Badge variant="stock-normal">Stock Normal</Badge>;
      case 'low': return <Badge variant="stock-low">Stock Bajo</Badge>;
      case 'high': return <Badge variant="stock-high">Stock Alto</Badge>;
      case 'out': return <Badge variant="stock-out">Sin Stock</Badge>;
      default: return <Badge variant="secondary">{status}</Badge>;
    }
  };

  const getQuantityDisplay = (item: InventoryItem) => {
    const isLowStock = item.quantity <= item.minStock;
    return (
      <div className={`flex items-center gap-2 ${isLowStock ? 'text-destructive' : ''}`}>
        {isLowStock && <AlertTriangle className="h-4 w-4" />}
        <span>{item.quantity} unidad{item.quantity !== 1 ? 'es' : ''}</span>
      </div>
    );
  };

  const filteredItems = inventoryItems.filter(item => {
    const matchesSearch = item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.code.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = categoryFilter === 'all' || item.category === categoryFilter;
    const matchesStatus = statusFilter === 'all' || item.status === statusFilter;
    
    return matchesSearch && matchesCategory && matchesStatus;
  });

  const handleEdit = (item: InventoryItem) => {
    setSelectedItem(item);
    setShowEditForm(true);
  };

  const handleDelete = (item: InventoryItem) => {
    setSelectedItem(item);
    setShowDeleteDialog(true);
  };

  const confirmDelete = async () => {
    if (!selectedItem) return;
    
    try {
      console.log('Eliminando item:', selectedItem.id);
      
      // TODO: Implementar eliminación en el backend
      // await inventarioService.delete(parseInt(selectedItem.id));
      
      // Simular eliminación
      await new Promise(resolve => setTimeout(resolve, 500));
      
      alert('Item de inventario eliminado exitosamente');
      setShowDeleteDialog(false);
      setSelectedItem(null);
      
      // Recargar datos
      fetchInventory();
    } catch (err) {
      console.error('Error eliminando item:', err);
      alert('Error al eliminar el item de inventario');
    }
  };

  const handleSuccess = () => {
    fetchInventory();
    setSelectedItem(null);
  };

  // Handlers para acciones
  const handleViewDetails = (item: InventoryItem) => {
    setSelectedItem(item);
    console.log('Ver detalles de:', item.name);
  };

  if (loading) {
    return (
      <PageLayout>
        <div className="flex items-center justify-center h-64">
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
        title="Inventario" 
        subtitle="Gestión de repuestos y materiales"
      >
        <Button onClick={() => setShowCreateForm(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Nuevo Item
        </Button>
      </PageHeader>

      {/* Tarjetas de resumen */}
      <StatsGrid>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Items</CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalItems}</div>
            <p className="text-xs text-muted-foreground">
              Items registrados
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Stock Bajo</CardTitle>
            <AlertTriangle className="h-4 w-4 text-destructive" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-destructive">{stats.lowStock}</div>
            <p className="text-xs text-muted-foreground">
              Requieren reorden
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Sin Stock</CardTitle>
            <AlertTriangle className="h-4 w-4 text-destructive" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-destructive">{stats.outOfStock}</div>
            <p className="text-xs text-muted-foreground">
              Items agotados
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Valor Total</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${Math.round(stats.totalValue).toLocaleString('es-CL')}
            </div>
            <p className="text-xs text-muted-foreground">
              Valor total en CLP
            </p>
          </CardContent>
        </Card>
      </StatsGrid>

      {/* Alertas de stock bajo */}
      {lowStockItems.length > 0 && (
        <Card className="border-destructive bg-destructive/5">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-destructive">
              <AlertTriangle className="h-5 w-5" />
              Alertas de Stock Bajo
            </CardTitle>
            <CardDescription>
              {lowStockItems.length} item{lowStockItems.length !== 1 ? 's' : ''} que requiere{lowStockItems.length !== 1 ? 'n' : ''} reabastecimiento
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {lowStockItems.map(item => (
                <div key={item.id} className="flex items-center justify-between p-4 bg-background rounded-lg border">
                  <div className="flex items-center gap-4">
                    <Package className="h-8 w-8 text-muted-foreground" />
                    <div>
                      <div className="font-medium">{item.name}</div>
                      <div className="text-sm text-muted-foreground">
                        {item.code} - {item.location}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <div className="flex items-center gap-2 text-destructive">
                        <AlertTriangle className="h-4 w-4" />
                        <span className="font-medium">
                          {item.quantity} unidad{item.quantity !== 1 ? 'es' : ''}
                        </span>
                      </div>
                      <div className="text-sm text-muted-foreground">
                        Mínimo: {item.minStock} unidad{item.minStock !== 1 ? 'es' : ''}
                      </div>
                    </div>
                    <Button variant="destructive" size="sm">
                      Reordenar
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Filtros y búsqueda */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Buscar items..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={categoryFilter} onValueChange={setCategoryFilter}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue placeholder="Todas las categorías" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todas las categorías</SelectItem>
                <SelectItem value="Filtros">Filtros</SelectItem>
                <SelectItem value="Rodamientos">Rodamientos</SelectItem>
                <SelectItem value="Lubricantes">Lubricantes</SelectItem>
                <SelectItem value="Herramientas">Herramientas</SelectItem>
              </SelectContent>
            </Select>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue placeholder="Todos" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos</SelectItem>
                <SelectItem value="normal">Stock Normal</SelectItem>
                <SelectItem value="low">Stock Bajo</SelectItem>
                <SelectItem value="high">Stock Alto</SelectItem>
                <SelectItem value="out">Sin Stock</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Tabla de inventario */}
      <Card>
        <CardHeader>
          <CardTitle>Inventario Completo</CardTitle>
          <CardDescription>Todos los items en stock</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Código</TableHead>
                <TableHead>Nombre</TableHead>
                <TableHead>Categoría</TableHead>
                <TableHead>Cantidad</TableHead>
                <TableHead>Stock Mínimo</TableHead>
                <TableHead>Estado</TableHead>
                <TableHead>Ubicación</TableHead>
                <TableHead>Costo Unitario</TableHead>
                <TableHead className="text-right">Acciones</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredItems.map((item) => (
                <TableRow key={item.id}>
                  <TableCell className="font-medium">
                    {item.code}
                  </TableCell>
                  <TableCell>
                    <div className="font-medium">{item.name}</div>
                  </TableCell>
                  <TableCell>{item.category}</TableCell>
                  <TableCell>
                    {getQuantityDisplay(item)}
                  </TableCell>
                  <TableCell>
                    {item.minStock} unidad{item.minStock !== 1 ? 'es' : ''}
                  </TableCell>
                  <TableCell>
                    {getStatusBadge(item.status)}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <MapPin className="h-4 w-4 text-muted-foreground" />
                      {item.location}
                    </div>
                  </TableCell>
                  <TableCell>
                    ${Math.round(item.unitCost).toLocaleString('es-CL')}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-2">
                      <Button 
                        variant="ghost" 
                        size="icon"
                        onClick={() => handleViewDetails(item)}
                        title="Ver detalles"
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button 
                        variant="ghost" 
                        size="icon"
                        onClick={() => handleEdit(item)}
                        title="Editar"
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button 
                        variant="ghost" 
                        size="icon"
                        onClick={() => handleDelete(item)}
                        title="Eliminar"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          
          {filteredItems.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              <Package className="mx-auto h-12 w-12 text-muted-foreground/50" />
              <h3 className="mt-2 text-sm font-medium">No hay items en el inventario</h3>
              <p className="mt-1 text-sm">
                {inventoryItems.length === 0 
                  ? 'Comienza agregando el primer item al inventario.'
                  : 'No hay items que coincidan con los filtros seleccionados.'}
              </p>
              {inventoryItems.length === 0 && (
                <Button 
                  onClick={() => setShowCreateForm(true)}
                  className="mt-4"
                  variant="outline"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Agregar Primer Item
                </Button>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Formulario de creación de item de inventario */}
      <CreateInventarioForm
        isOpen={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        onSuccess={() => {
          fetchInventory();
        }}
      />

      {/* Formulario de edición de item de inventario */}
      {selectedItem && (
        <CreateInventarioForm
          isOpen={showEditForm}
          onClose={() => {
            setShowEditForm(false);
            setSelectedItem(null);
          }}
          onSuccess={() => {
            fetchInventory();
            setShowEditForm(false);
            setSelectedItem(null);
          }}
          inventarioData={selectedItem}
        />
      )}

      {/* Diálogo de confirmación de eliminación */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>¿Estás seguro?</AlertDialogTitle>
            <AlertDialogDescription>
              Esta acción no se puede deshacer. Se eliminará permanentemente el item "{selectedItem?.name}".
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

export default InventarioView;

