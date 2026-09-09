import React from 'react';
import { Link } from 'react-router-dom';
import type { Paper } from '../../types/paper';
import { StatusBadge } from './StatusBadge';
import { ChevronRight } from 'lucide-react';

export const PaperTable: React.FC<{ papers: Paper[] }> = ({ papers }) => {
  return (
    <div className="overflow-x-auto rounded-2xl border border-border bg-surface shadow-sm">
      <table className="w-full text-left text-sm text-primary whitespace-nowrap">
        <thead className="bg-surface-raised border-b border-border text-xs uppercase tracking-wider font-bold text-secondary">
          <tr>
            <th className="px-6 py-4">Title & Authors</th>
            <th className="px-6 py-4">Venue</th>
            <th className="px-6 py-4">Year</th>
            <th className="px-6 py-4">Status</th>
            <th className="px-6 py-4"></th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {papers.map((paper) => (
            <tr key={paper.id} className="hover:bg-surface-raised transition-colors group cursor-pointer">
              <td className="px-6 py-4 max-w-[400px]">
                <div className="font-bold text-primary truncate mb-1">{paper.title}</div>
                <div className="text-xs text-secondary truncate">{paper.authors.join(', ')}</div>
              </td>
              <td className="px-6 py-4 text-secondary">{paper.venue}</td>
              <td className="px-6 py-4 text-secondary font-medium">{paper.year}</td>
              <td className="px-6 py-4"><StatusBadge status={paper.analysisStatus} /></td>
              <td className="px-6 py-4 text-right">
                <Link to={`/papers/${paper.id}`} className="inline-flex items-center text-accent font-semibold opacity-0 group-hover:opacity-100 transition-opacity">
                  View <ChevronRight size={16} />
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};