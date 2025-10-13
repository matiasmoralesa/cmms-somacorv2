import React from 'react'
import { Outlet } from 'react-router-dom'
import { Menu } from 'lucide-react'
import { SidebarProvider, useSidebar } from '@/components/ui/sidebar'
import { AppSidebar } from './AppSidebar'
import { Button } from '@/components/ui/button'
import RealtimeNotifications from '@/components/RealtimeNotifications'

function LayoutContent() {
  const { isOpen, setIsOpen } = useSidebar()

  return (
    <div className="flex h-screen bg-background">
      <AppSidebar />
      
      <div className="flex-1 flex flex-col overflow-hidden lg:ml-64">
        {/* Mobile header */}
        <header className="flex items-center justify-between border-b bg-background px-4 py-3 lg:hidden">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsOpen(true)}
            >
              <Menu className="h-5 w-5" />
            </Button>
            <h1 className="text-lg font-semibold">Somacor CMMS</h1>
          </div>
          <RealtimeNotifications />
        </header>

        {/* Desktop header */}
        <header className="hidden lg:flex items-center justify-between border-b bg-background px-6 py-4">
          <h1 className="text-xl font-semibold">Somacor CMMS</h1>
          <RealtimeNotifications />
        </header>

        {/* Main content */}
        <main className="flex-1 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export function AppLayout() {
  return (
    <SidebarProvider>
      <LayoutContent />
    </SidebarProvider>
  )
}