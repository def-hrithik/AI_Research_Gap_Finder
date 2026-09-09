import React from 'react';
import { Link } from 'react-router-dom';
import { Target } from 'lucide-react';
import { Button } from '../common/Button';
import { ThemeToggle } from '../layout/ThemeToggle';

export const NavBar: React.FC = () => {
  return (
    <nav className="fixed top-0 w-full h-20 bg-background/80 backdrop-blur-lg border-b border-border z-50 transition-all">
      <div className="max-w-7xl mx-auto px-6 h-full flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 group">
          <div className="w-8 h-8 rounded-xl bg-accent flex items-center justify-center transition-transform group-hover:scale-105">
            <Target size={18} className="text-white" />
          </div>
          <span className="font-bold text-xl tracking-tight text-primary">Nexus</span>
        </Link>
        
        <div className="hidden md:flex items-center gap-8 text-sm font-medium text-secondary">
          <a href="#product" className="hover:text-primary transition-colors">Product</a>
          <a href="#how-it-works" className="hover:text-primary transition-colors">How it Works</a>
        </div>

        <div className="flex items-center gap-4">
          <ThemeToggle />
          <Link to="/dashboard" className="hidden sm:block">
            <Button variant="ghost">Log In</Button>
          </Link>
          <Link to="/dashboard">
            <Button className="rounded-full shadow-md">Get Started</Button>
          </Link>
        </div>
      </div>
    </nav>
  );
};