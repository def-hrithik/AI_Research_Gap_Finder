import React from 'react';
import { Search, LayoutGrid, List } from 'lucide-react';
import { cn } from '../../utils/formatters';

interface PaperFiltersProps {
  viewMode: 'list' | 'grid';
  setViewMode: (mode: 'list' | 'grid') => void;
}

export const PaperFilters: React.FC<PaperFiltersProps> = ({ viewMode, setViewMode }) => {
  return (
    <div className="flex flex-col sm:flex-row gap-4 mb-6">
      <div className="relative flex-1">
        <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary" />
        <input 
          type="text"
          placeholder="Search by title, author, or venue..."
          className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-border bg-surface focus:outline-none focus:ring-2 focus:ring-accent/50 text-primary"
        />
      </div>
      <div className="flex items-center gap-3">
        <select className="px-4 py-2.5 rounded-xl border border-border bg-surface text-primary font-medium focus:outline-none focus:ring-2 focus:ring-accent/50 cursor-pointer appearance-none pr-10">
          <option>All Statuses</option>
          <option>Processed</option>
          <option>Processing</option>
        </select>
        <div className="flex items-center p-1 bg-surface border border-border rounded-xl">
          <button 
            onClick={() => setViewMode('list')}
            className={cn("p-1.5 rounded-lg transition-colors", viewMode === 'list' ? "bg-background shadow-sm text-primary" : "text-secondary hover:text-primary")}
          >
            <List size={18} />
          </button>
          <button 
            onClick={() => setViewMode('grid')}
            className={cn("p-1.5 rounded-lg transition-colors", viewMode === 'grid' ? "bg-background shadow-sm text-primary" : "text-secondary hover:text-primary")}
          >
            <LayoutGrid size={18} />
          </button>
        </div>
      </div>
    </div>
  );
};