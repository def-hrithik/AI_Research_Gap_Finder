import React from 'react';
import { Search, SlidersHorizontal } from 'lucide-react';
import { Button } from '../common/Button';

export const ProjectFilters: React.FC = () => {
  return (
    <div className="flex flex-col sm:flex-row gap-4">
      <div className="relative flex-1">
        <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary" />
        <input 
          type="text"
          placeholder="Search projects by name or keyword..."
          className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-border bg-surface focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent text-primary transition-all"
        />
      </div>
      <div className="flex items-center gap-3">
        <select className="px-4 py-2.5 rounded-xl border border-border bg-surface text-primary font-medium focus:outline-none focus:ring-2 focus:ring-accent/50 cursor-pointer appearance-none pr-10">
          <option>Sort by: Newest</option>
          <option>Sort by: Name (A-Z)</option>
          <option>Sort by: Most Papers</option>
        </select>
        <Button variant="secondary" className="gap-2 px-3">
          <SlidersHorizontal size={18} />
          <span className="hidden sm:inline">Filter</span>
        </Button>
      </div>
    </div>
  );
};