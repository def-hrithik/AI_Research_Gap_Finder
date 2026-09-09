import React from 'react';
import { AlertCircle, Scale } from 'lucide-react';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
import type { Contradiction } from '../../types/contradiction';
interface ContradictionCardProps {
  contradiction: Contradiction;
}

export const ContradictionCard: React.FC<ContradictionCardProps> = ({ contradiction }) => {
  return (
    <Card raised className="overflow-hidden border-border relative">
      <div className="absolute top-0 left-0 w-1 h-full bg-alert"></div>
      
      <div className="p-6">
        <div className="flex justify-between items-start mb-6">
          <div className="flex items-center gap-2">
            <Badge variant="alert" className="flex items-center gap-1 bg-alert/10 text-alert">
              <AlertCircle size={14} /> Potential Contradiction
            </Badge>
            <span className="text-sm font-bold text-secondary uppercase tracking-wider pl-2 border-l border-border">
              {contradiction.topic}
            </span>
          </div>
          
          <div className="flex flex-col items-end">
            <span className="text-xl font-extrabold text-primary">{contradiction.confidenceScore}%</span>
            <span className="text-[10px] text-secondary uppercase font-bold tracking-wider">AI Confidence</span>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-6 relative">
          {/* Visual separator for desktop */}
          <div className="hidden md:flex absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-surface border border-border items-center justify-center text-secondary z-10 shadow-sm">
            <Scale size={14} />
          </div>

          <div className="p-5 rounded-xl bg-surface-raised border border-border">
            <Badge variant="default" className="mb-3">Paper A (ID: {contradiction.paperAId})</Badge>
            <p className="text-sm text-primary font-medium italic">"{contradiction.paperAClaim}"</p>
          </div>

          <div className="p-5 rounded-xl bg-surface-raised border border-border">
            <Badge variant="default" className="mb-3">Paper B (ID: {contradiction.paperBId})</Badge>
            <p className="text-sm text-primary font-medium italic">"{contradiction.paperBClaim}"</p>
          </div>
        </div>

        <div className="mt-6 pt-4 border-t border-border">
          <p className="text-xs font-semibold text-secondary uppercase tracking-wider mb-1">Experimental Context</p>
          <p className="text-sm text-primary">{contradiction.experimentalContext}</p>
        </div>
      </div>
    </Card>
  );
};