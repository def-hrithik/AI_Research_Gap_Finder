import React from 'react';
import { Link } from 'react-router-dom';
import { Target, FileText, ChevronRight } from 'lucide-react';
import type { ResearchGap } from '../../types/gap';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';

interface GapCardProps {
  gap: ResearchGap;
}

export const GapCard: React.FC<GapCardProps> = ({ gap }) => {
  return (
    <div className="relative">
      {/* Primary Content Block */}
      <div className="pr-0 lg:pr-80">
        <Card raised interactive className="p-6 md:p-8 flex flex-col h-full relative z-10 group border-border hover:border-accent/50">
          <div className="flex items-center gap-2 text-xs font-bold text-secondary mb-4 uppercase tracking-wider">
            <Target size={16} className="text-accent" />
            {gap.topic}
          </div>
          
          <h3 className="text-xl md:text-2xl font-bold mb-4 text-primary leading-tight group-hover:text-accent transition-colors">
            {gap.suggestedQuestion}
          </h3>
          
          <p className="text-secondary leading-relaxed mb-6">
            {gap.description}
          </p>

          <div className="flex items-center gap-4 text-sm text-secondary mt-auto pt-6 border-t border-border">
            <div className="flex items-center gap-1.5 font-medium">
              <FileText size={16} className="text-primary" /> {gap.supportingPaperIds.length} Supporting Papers
            </div>
            <Link to={`/gaps/${gap.id}`} className="ml-auto inline-flex items-center text-accent font-semibold opacity-0 group-hover:opacity-100 transition-opacity">
              View Evidence <ChevronRight size={16} />
            </Link>
          </div>
        </Card>
      </div>

      {/* Signature Motif: The Marginal Annotation */}
      <div className="mt-4 lg:mt-0 lg:absolute right-0 top-8 lg:w-80 z-0">
        <div className="relative p-6 border-l-2 border-accent bg-surface-raised rounded-r-2xl lg:shadow-md lg:border lg:border-border lg:border-l-accent border-l-4">
          <div className="hidden lg:block absolute -left-[19px] top-6 bg-surface border border-border rounded-full p-1 shadow-sm">
            <div className="w-2 h-2 rounded-full bg-accent animate-pulse" />
          </div>
          
          <div className="flex justify-between items-start mb-4">
            <Badge variant="outline" className="border-accent/20 text-accent bg-accent/5">{gap.type}</Badge>
            <div className="flex flex-col items-end">
              <span className="text-accent font-black text-2xl tracking-tighter leading-none">{gap.confidence}%</span>
              <span className="text-[10px] text-secondary uppercase font-bold mt-1">Confidence</span>
            </div>
          </div>
          
          <div className="space-y-3">
            <p className="text-xs font-bold text-secondary uppercase tracking-wider">Top Evidence</p>
            <p className="text-sm font-medium text-primary italic leading-relaxed line-clamp-3">
              "{gap.evidence[0]?.text}"
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};