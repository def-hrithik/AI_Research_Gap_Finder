import React, { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Search, Bell, User, LogOut } from 'lucide-react';
import { ThemeToggle } from './ThemeToggle';
import { Button } from '../common/Button';
import { useAuth } from '../../context/AuthContext';

export const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const initials = user
    ? user.name
        .split(' ')
        .map((part) => part[0])
        .join('')
        .slice(0, 2)
        .toUpperCase()
    : null;

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

        {user ? (
          <div className="relative" ref={menuRef}>
            <button
              onClick={() => setMenuOpen((o) => !o)}
              className="rounded-full w-9 h-9 flex items-center justify-center bg-accent/10 text-accent hover:bg-accent/20 transition-colors text-xs font-bold"
              aria-label="Account menu"
            >
              {initials}
            </button>
            {menuOpen && (
              <div className="absolute right-0 mt-2 w-56 bg-surface border border-border rounded-xl shadow-md py-1 z-20">
                <div className="px-3 py-2 border-b border-border">
                  <p className="text-sm font-medium text-primary truncate">{user.name}</p>
                  <p className="text-xs text-secondary truncate">{user.email}</p>
                </div>
                <button
                  onClick={() => {
                    setMenuOpen(false);
                    logout();
                  }}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm text-secondary hover:text-primary hover:bg-surface-raised transition-colors"
                >
                  <LogOut size={14} /> Log out
                </button>
              </div>
            )}
          </div>
        ) : (
          <Link to="/login">
            <Button variant="ghost" className="rounded-full w-9 h-9 p-0 bg-accent/10 text-accent hover:bg-accent/20">
              <User size={18} />
            </Button>
          </Link>
        )}
      </div>
    </header>
  );
};