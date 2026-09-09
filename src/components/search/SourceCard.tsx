import React from 'react';
import { FileText } from 'lucide-react';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';

interface Source {
  id: string;
  paperTitle: string;
  section: string;
  page: number;
  text: string;
  relevance: number;
}

export const SourceCard: React.FC<{ source: Source }> = ({ source }) => (
  <Card className="p-5 flex flex-col h-full border-border hover:border-accent/30 transition-colors">
    <div className="flex justify-between items-start mb-3">
      <Badge variant="accent" className="bg-accent/10 text-accent">Relevance {source.relevance}%</Badge>
      <span className="text-xs font-semibold text-secondary uppercase">Page {source.page}</span>
    </div>
    <p className="text-sm font-medium text-primary mb-4 italic line-clamp-4 flex-1">
      "{source.text}"
    </p>
    <div className="border-t border-border pt-3 mt-auto">
      <div className="text-xs font-bold text-primary flex items-center gap-1.5 mb-1 truncate">
        <FileText size={14} className="text-secondary shrink-0" />
        <span className="truncate">{source.paperTitle}</span>
      </div>
      <div className="text-xs text-secondary pl-5">Section: {source.section}</div>
    </div>
  </Card>
);