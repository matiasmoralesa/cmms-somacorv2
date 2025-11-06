import React from 'react'
import { cn } from '@/lib/utils'

interface PageLayoutProps {
  children: React.ReactNode
  className?: string
}

export function PageLayout({ children, className }: PageLayoutProps) {
  return (
    <div className={cn("p-6 space-y-6", className)}>
      {children}
    </div>
  )
}

interface PageHeaderProps {
  title: string
  subtitle?: string
  description?: string
  action?: React.ReactNode
  children?: React.ReactNode
  className?: string
}

export function PageHeader({ title, subtitle, description, action, children, className }: PageHeaderProps) {
  return (
    <div className={cn("flex items-center justify-between", className)}>
      <div className="space-y-1">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">
          {title}
        </h1>
        {(subtitle || description) && (
          <p className="text-muted-foreground">
            {subtitle || description}
          </p>
        )}
      </div>
      {(action || children) && (
        <div className="flex items-center gap-2">
          {action || children}
        </div>
      )}
    </div>
  )
}

interface StatsGridProps {
  children: React.ReactNode
  className?: string
}

export function StatsGrid({ children, className }: StatsGridProps) {
  return (
    <div className={cn("grid gap-4 md:grid-cols-2 lg:grid-cols-4", className)}>
      {children}
    </div>
  )
}

interface ContentGridProps {
  children: React.ReactNode
  className?: string
}

export function ContentGrid({ children, className }: ContentGridProps) {
  return (
    <div className={cn("grid gap-6 lg:grid-cols-2", className)}>
      {children}
    </div>
  )
}
