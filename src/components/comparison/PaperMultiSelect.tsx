import React from 'react';
import { CheckSquare, Square } from 'lucide-react';
import { Card } from '../common/Card';
import type { Paper } from '../../types/paper';
import { cn } from '../../utils/formatters';

interface PaperMultiSelectProps {
  papers: Paper[];
  selectedIds: string[];
  onToggle: (id: string) => void;
}

export const PaperMultiSelect: React.FC<PaperMultiSelectProps> = ({ papers, selectedIds, onToggle }) => {
  return (
    <div className="mb-8">
      <h3 className="text-sm font-bold text-secondary uppercase tracking-wider mb-4">
        Select Papers to Compare (Max 4)
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {papers.map((paper) => {
          const isSelected = selectedIds.includes(paper.id);
          const isDisabled = !isSelected && selectedIds.length >= 4;

          return (
            <Card
              key={paper.id}
              interactive={!isDisabled}
              onClick={() => {
                if (!isDisabled || isSelected) onToggle(paper.id);
              }}
              className={cn(
                "p-3 flex items-start gap-3 cursor-pointer transition-all",
                isSelected ? "border-accent bg-accent/5 ring-1 ring-accent" : "",
                isDisabled ? "opacity-50 cursor-not-allowed" : ""
              )}
            >
              <div className="mt-0.5 text-accent shrink-0">
                {isSelected ? <CheckSquare size={18} /> : <Square size={18} className="text-secondary" />}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-bold text-primary truncate">{paper.title}</p>
                <p className="text-xs text-secondary truncate">{paper.authors.join(', ')} • {paper.year}</p>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
};