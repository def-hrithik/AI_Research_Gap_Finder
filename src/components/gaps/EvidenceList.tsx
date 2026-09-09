import React from 'react';
import { FileText, Link as LinkIcon } from 'lucide-react';
import type { Evidence } from '../../types/gap';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';

export const EvidenceList: React.FC<{ evidence: Evidence[] }> = ({ evidence }) => {
  return (
    <div className="space-y-4">
      {evidence.map((ev, idx) => (
        <Card key={idx} className="p-5 border-border bg-background">
          <div className="flex justify-between items-start mb-3">
            <div className="flex items-center gap-2">
              <Badge variant="accent" className="bg-accent/10">Relevance: {ev.relevanceScore}%</Badge>
              <span className="text-xs font-bold text-secondary uppercase tracking-wider px-2 border-l border-border">Page {ev.page}</span>
            </div>
          </div>
          <p className="text-primary font-medium italic mb-4 leading-relaxed">
            "{ev.text}"
          </p>
          <div className="flex items-center justify-between pt-3 border-t border-border">
            <div className="flex items-center gap-2 text-xs font-bold text-secondary">
              <FileText size={14} className="text-primary" /> {ev.paperId}
              <span className="opacity-50">•</span>
              Section: {ev.section}
            </div>
            <button className="text-accent hover:text-accent-hover p-1 bg-accent/5 rounded-md transition-colors">
              <LinkIcon size={14} />
            </button>
          </div>
        </Card>
      ))}
    </div>
  ); 
};