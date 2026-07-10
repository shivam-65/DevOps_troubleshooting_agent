import { NavLink } from 'react-router-dom';
import { LayoutDashboard, AlertTriangle, Zap, FileText, Settings, ChevronLeft, ChevronRight, Shield } from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/incidents', icon: AlertTriangle, label: 'Incidents' },
  { to: '/actions', icon: Zap, label: 'Actions' },
  { to: '/reports', icon: FileText, label: 'Reports' },
  { to: '/settings', icon: Settings, label: 'Settings' },
];

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  return (
    <aside className={cn(
      'fixed left-0 top-0 h-screen bg-sidebar border-r border-border flex flex-col z-40 transition-all duration-200',
      collapsed ? 'w-16' : 'w-56'
    )}>
      <div className={cn('flex items-center h-14 border-b border-border px-4', collapsed ? 'justify-center' : 'gap-2')}>
        <Shield className="h-6 w-6 text-primary flex-shrink-0" />
        {!collapsed && <span className="font-semibold text-foreground text-sm tracking-tight">Incident Commander</span>}
      </div>

      <nav className="flex-1 py-3 space-y-0.5 px-2">
        {navItems.map((item) => (
          <NavLink key={item.to} to={item.to} end={item.to === '/'}
            className={({ isActive }) => cn(
              'flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors',
              isActive
                ? 'bg-primary/10 text-primary'
                : 'text-sidebar-foreground hover:text-foreground hover:bg-muted/50',
              collapsed && 'justify-center px-0'
            )}>
            <item.icon className="h-4.5 w-4.5 flex-shrink-0" />
            {!collapsed && <span>{item.label}</span>}
          </NavLink>
        ))}
      </nav>

      <button onClick={onToggle} className="flex items-center justify-center h-10 border-t border-border text-muted-foreground hover:text-foreground transition-colors">
        {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
      </button>
    </aside>
  );
}
