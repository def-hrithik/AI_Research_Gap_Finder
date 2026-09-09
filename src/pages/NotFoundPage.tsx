import React from 'react';
import { Link } from 'react-router-dom';
import { MapPinOff } from 'lucide-react';
import { Button } from '../components/common/Button';

export const NotFoundPage: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center h-full min-h-[70vh] text-center px-6 animate-in fade-in duration-300">
      <div className="w-20 h-20 bg-surface border border-border rounded-2xl flex items-center justify-center text-secondary mb-8 shadow-sm">
        <MapPinOff size={40} />
      </div>
      <h1 className="text-6xl font-black text-primary tracking-tighter mb-4">404</h1>
      <h2 className="text-2xl font-bold text-primary mb-3">This page hasn't been explored yet.</h2>
      <p className="text-secondary text-lg max-w-md mb-8 leading-relaxed">
        The literature is full of gaps. Apparently, so is this route. The page you requested does not exist in the current workspace.
      </p>
      <Link to="/dashboard">
        <Button size="lg" className="rounded-full px-8 shadow-md">
          Return to Workspace
        </Button>
      </Link>
    </div>
  );
};