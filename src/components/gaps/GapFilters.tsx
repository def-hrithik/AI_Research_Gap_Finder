import React from 'react';
import { Filter, ArrowUpDown } from 'lucide-react';
import { Button } from '../common/Button';

export const GapFilters: React.FC = () => {
  return (
    <div className="flex flex-col sm:flex-row gap-4 mb-8">
      <div className="flex-1 flex gap-2 overflow-x-auto hide-scrollbar pb-2 sm:pb-0">
        <select className="px-4 py-2.5 rounded-xl border border-border bg-surface text-primary text-sm font-medium focus:outline-none focus:ring-2 focus:ring-accent/50 min-w-[160px]">
          <option>All Gap Types</option>
          <option>Underexplored Area</option>
          <option>Repeated Limitation</option>
          <option>Contradiction-Driven</option>
        </select>
        <select className="px-4 py-2.5 rounded-xl border border-border bg-surface text-primary text-sm font-medium focus:outline-none focus:ring-2 focus:ring-accent/50 min-w-[160px]">
          <option>All Topics</option>
          <option>Model Generalization</option>
          <option>Data Demographics</option>
        </select>
      </div>
      <div className="flex items-center gap-2 shrink-0">
        <Button variant="secondary" className="gap-2">
          <ArrowUpDown size={16} /> Sort: Confidence
        </Button>
        <Button variant="secondary" className="gap-2 px-3">
          <Filter size={16} />
        </Button>
      </div>
    </div>
  );
};