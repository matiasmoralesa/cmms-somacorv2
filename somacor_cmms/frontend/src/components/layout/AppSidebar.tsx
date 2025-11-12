import React from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Wrench, 
  ClipboardList, 
  Calendar, 
  Package, 
  Users, 
  Settings,
  Menu,
  X,
  Activity,
  Clock,
  AlertTriangle,
  UserCheck,
  MapPin,
  Tag,
  ListTodo,
  CheckSquare
} from 'lucide-react'
import { 
  Sidebar, 
  SidebarHeader, 
  SidebarContent, 
  SidebarFooter, 
  SidebarGroup, 
  SidebarGroupLabel, 
  SidebarMenuButton,
  useSidebar
} from '@/components/ui/sidebar'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

const navigationItems = [
  {
    title: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    title: "Equipos",
    href: "/equipos",
    icon: Wrench,
  },
  {
    title: "Órdenes de Trabajo",
    href: "/ordenes-trabajo",
    icon: ClipboardList,
  },
  {
    title: "Mantenimiento Preventivo",
    href: "/mantenimiento-preventivo",
    icon: Calendar,
  },
  {
    title: "Inventario",
    href: "/inventario",
    icon: Package,
  },
  {
    title: "Técnicos",
    href: "/tecnicos",
    icon: Users,
  },
  {
    title: "Estado de Máquina",
    href: "/estado-maquina",
    icon: Activity,
  },
  {
    title: "Calendario",
    href: "/calendario",
    icon: Clock,
  },
  {
    title: "Mantenimiento No Planificado",
    href: "/mantenimiento-no-planificado",
    icon: AlertTriangle,
  },
  {
    title: "Checklist",
    href: "/checklist",
    icon: CheckSquare,
  },
]

const configItems = [
  {
    title: "Configuración",
    href: "/configuracion",
    icon: Settings,
  },
]

const adminItems = [
  {
    title: "Perfiles",
    href: "/admin/perfiles",
    icon: UserCheck,
  },
  {
    title: "Programas",
    href: "/admin/programas",
    icon: Calendar,
  },
]

const mantenedoresItems = [
  {
    title: "Faenas",
    href: "/mantenedores/faenas",
    icon: MapPin,
  },
  {
    title: "Tipos de Equipo",
    href: "/mantenedores/tipos-equipo",
    icon: Tag,
  },
  {
    title: "Tipos de Tarea",
    href: "/mantenedores/tipos-tarea",
    icon: ListTodo,
  },
]

export function AppSidebar() {
  const location = useLocation()
  const navigate = useNavigate()
  const { isOpen, setIsOpen } = useSidebar()

  const handleNavigation = (href: string) => {
    navigate(href)
  }

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}
      
      <Sidebar className="lg:translate-x-0">
        <SidebarHeader>
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
              <Wrench className="h-5 w-5 text-primary-foreground" />
            </div>
            <div className="flex flex-col">
              <span className="text-lg font-semibold text-sidebar-foreground">
                Somacor CMMS
              </span>
            </div>
          </div>
          
          {/* Mobile close button */}
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden"
            onClick={() => setIsOpen(false)}
          >
            <X className="h-5 w-5" />
          </Button>
        </SidebarHeader>

        <SidebarContent>
          <SidebarGroup>
            <SidebarGroupLabel>Gestión</SidebarGroupLabel>
            {navigationItems.map((item) => {
              const isActive = location.pathname === item.href
              return (
                <SidebarMenuButton
                  key={item.href}
                  isActive={isActive}
                  onClick={() => handleNavigation(item.href)}
                  className="w-full"
                >
                  <item.icon className="h-5 w-5" />
                  <span>{item.title}</span>
                </SidebarMenuButton>
              )
            })}
          </SidebarGroup>

          <SidebarGroup>
            <SidebarGroupLabel>Administración</SidebarGroupLabel>
            {adminItems.map((item) => {
              const isActive = location.pathname === item.href
              return (
                <SidebarMenuButton
                  key={item.href}
                  isActive={isActive}
                  onClick={() => handleNavigation(item.href)}
                  className="w-full"
                >
                  <item.icon className="h-5 w-5" />
                  <span>{item.title}</span>
                </SidebarMenuButton>
              )
            })}
          </SidebarGroup>

          <SidebarGroup>
            <SidebarGroupLabel>Mantenedores</SidebarGroupLabel>
            {mantenedoresItems.map((item) => {
              const isActive = location.pathname === item.href
              return (
                <SidebarMenuButton
                  key={item.href}
                  isActive={isActive}
                  onClick={() => handleNavigation(item.href)}
                  className="w-full"
                >
                  <item.icon className="h-5 w-5" />
                  <span>{item.title}</span>
                </SidebarMenuButton>
              )
            })}
          </SidebarGroup>

          <SidebarGroup>
            <SidebarGroupLabel>Configuración</SidebarGroupLabel>
            {configItems.map((item) => {
              const isActive = location.pathname === item.href
              return (
                <SidebarMenuButton
                  key={item.href}
                  isActive={isActive}
                  onClick={() => handleNavigation(item.href)}
                  className="w-full"
                >
                  <item.icon className="h-5 w-5" />
                  <span>{item.title}</span>
                </SidebarMenuButton>
              )
            })}
          </SidebarGroup>
        </SidebarContent>

        <SidebarFooter>
          <div className="flex items-center gap-3 px-3 py-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-sidebar-primary text-white text-sm font-medium">
              AU
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-medium text-sidebar-foreground">
                Admin User
              </span>
              <span className="text-xs text-sidebar-foreground/70">
                Administrador
              </span>
            </div>
          </div>
        </SidebarFooter>
      </Sidebar>
    </>
  )
}
