import React from 'react';
import { Search, Bell, User } from 'lucide-react';
import { ThemeToggle } from './ThemeToggle';
import { Button } from '../common/Button';

export const Header: React.FC = () => {
  return (
    <header className="h-16 flex items-center justify-between px-6 bg-surface border-b border-border z-10 sticky top-0">
      <div className="flex-1 flex items-center gap-4">
        {/* Global Search Placeholder */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-background border border-border rounded-lg text-secondary focus-within:border-accent focus-within:ring-1 focus-within:ring-accent w-64 transition-all">
          <Search size={16} />
          <input 
            type="text" 
            placeholder="Search projects..." 
            className="bg-transparent border-none focus:outline-none text-sm w-full text-primary"
          />
        </div>
      </div>
      
      <div className="flex items-center gap-2">
        <ThemeToggle />
        <button className="p-2 rounded-xl text-secondary hover:bg-surface-raised transition-colors">
          <Bell size={20} />
        </button>
        <div className="w-px h-6 bg-border mx-2"></div>
        <Button variant="ghost" className="rounded-full w-9 h-9 p-0 bg-accent/10 text-accent hover:bg-accent/20">
          <User size={18} />
        </Button>
      </div>
    </header>
  );
};