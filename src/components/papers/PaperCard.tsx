import React from 'react';
import { Link } from 'react-router-dom';
import { FileText, Calendar, BookOpen } from 'lucide-react';
import type { Paper } from '../../types/paper';
import { Card } from '../common/Card';
import { StatusBadge } from './StatusBadge';

export const PaperCard: React.FC<{ paper: Paper }> = ({ paper }) => {
  return (
    <Link to={`/papers/${paper.id}`} className="block h-full">
      <Card interactive className="h-full flex flex-col p-6">
        <div className="flex justify-between items-start mb-4">
          <StatusBadge status={paper.analysisStatus} />
        </div>
        <h3 className="text-lg font-bold text-primary mb-3 line-clamp-2 leading-tight">
          {paper.title}
        </h3>
        <p className="text-sm text-secondary mb-6 line-clamp-3 leading-relaxed flex-1">
          {paper.abstract}
        </p>
        <div className="flex flex-wrap gap-4 pt-4 border-t border-border text-xs font-semibold text-secondary uppercase tracking-wider">
          <div className="flex items-center gap-1.5"><FileText size={14} /> {paper.authors[0]} et al.</div>
          <div className="flex items-center gap-1.5"><Calendar size={14} /> {paper.year}</div>
          <div className="flex items-center gap-1.5"><BookOpen size={14} /> {paper.venue}</div>
        </div>
      </Card>
    </Link>
  );
};