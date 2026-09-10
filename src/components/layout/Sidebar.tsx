import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, FolderKanban, FileText, Search, 
  Map, Layers, Target, FileBarChart, ChevronLeft, ChevronRight, Beaker
} from 'lucide-react';
import { cn } from '../../utils/formatters';

interface SidebarProps {
  collapsed: boolean;
  setCollapsed: (collapsed: boolean) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ collapsed, setCollapsed }) => {
  const location = useLocation();
  
  // Extract projectId from URL if present (e.g., /projects/proj-1/...)
  const match = location.pathname.match(/\/projects\/([^/]+)/);
  const projectId = match ? match[1] : null;

  const globalLinks = [
    { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/projects', icon: FolderKanban, label: 'Projects' },
  ];

  const projectLinks = projectId ? [
    { to: `/projects/${projectId}/papers`, icon: FileText, label: 'Papers' },
    { to: `/projects/${projectId}/search`, icon: Search, label: 'Semantic Search' },
    { to: `/projects/${projectId}/landscape`, icon: Map, label: 'Landscape' },
    { to: `/projects/${projectId}/compare`, icon: Layers, label: 'Compare' },
    { to: `/projects/${projectId}/contradictions`, icon: Beaker, label: 'Contradictions' },
    { to: `/projects/${projectId}/gaps`, icon: Target, label: 'Research Gaps' },
    { to: `/projects/${projectId}/reports`, icon: FileBarChart, label: 'Reports' },
  ] : [];

  const NavItem = ({ to, icon: Icon, label }: { to: string, icon: any, label: string }) => (
    <NavLink
      to={to}
      className={({ isActive }) => cn(
        "flex items-center gap-3 px-3 py-2.5 rounded-xl font-medium transition-all duration-200 group",
        isActive 
          ? "bg-accent/10 text-accent" 
          : "text-secondary hover:bg-surface-raised hover:text-primary"
      )}
      title={collapsed ? label : undefined}
    >
      {({ isActive }) => (
        <>
          <Icon size={20} className={cn("shrink-0 transition-colors", isActive ? "text-accent" : "text-secondary group-hover:text-primary")} />
          {!collapsed && <span className="truncate">{label}</span>}
        </>
      )}
    </NavLink>
  );

  return (
    <aside className={cn(
      "bg-surface border-r border-border flex flex-col transition-all duration-300 relative z-20",
      collapsed ? "w-20" : "w-64"
    )}>
      {/* Logo Area */}
      <div className="h-16 flex items-center px-4 border-b border-border overflow-hidden shrink-0">
        <div className="w-8 h-8 rounded-xl bg-accent flex items-center justify-center shrink-0">
          <Target size={18} className="text-white" />
        </div>
        {!collapsed && <span className="ml-3 font-bold text-lg text-primary tracking-tight truncate">Nexus Gap Finder</span>}
      </div>

      {/* Navigation */}
      <div className="flex-1 overflow-y-auto py-6 px-3 flex flex-col gap-8">
        <div className="flex flex-col gap-1">
          {!collapsed && <span className="px-3 text-xs font-semibold text-secondary uppercase tracking-wider mb-2">Platform</span>}
          {globalLinks.map(link => <NavItem key={link.to} {...link} />)}
        </div>

        {projectId && (
          <div className="flex flex-col gap-1">
            {!collapsed && <span className="px-3 text-xs font-semibold text-secondary uppercase tracking-wider mb-2">Active Project</span>}
            {projectLinks.map(link => <NavItem key={link.to} {...link} />)}
          </div>
        )}
      </div>

      {/* Collapse Toggle */}
      <button 
        onClick={() => setCollapsed(!collapsed)}
        className="absolute -right-3 top-20 bg-surface border border-border rounded-full p-1 text-secondary hover:text-primary hover:bg-surface-raised shadow-sm transition-transform"
      >
        {collapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
      </button>
    </aside>
  );
};