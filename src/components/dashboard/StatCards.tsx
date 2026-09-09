import React from 'react';
import { FolderKanban, FileText, Map, Target } from 'lucide-react';
import { Card } from '../common/Card';

interface StatCardsProps {
  projectsCount: number;
  papersCount: number;
  topicsCount: number;
  gapsCount: number;
}

export const StatCards: React.FC<StatCardsProps> = ({ projectsCount, papersCount, topicsCount, gapsCount }) => {
  const stats = [
    { label: 'Active Projects', value: projectsCount, icon: FolderKanban, color: 'text-accent', bg: 'bg-accent/10' },
    { label: 'Papers Analyzed', value: papersCount, icon: FileText, color: 'text-blue-500', bg: 'bg-blue-500/10' },
    { label: 'Topics Mapped', value: topicsCount, icon: Map, color: 'text-success', bg: 'bg-success/10' },
    { label: 'Candidate Gaps', value: gapsCount, icon: Target, color: 'text-alert', bg: 'bg-alert/10' },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat, i) => (
        <Card key={i} className="p-6 flex items-center gap-5">
          <div className={`w-14 h-14 rounded-2xl flex items-center justify-center ${stat.bg} ${stat.color}`}>
            <stat.icon size={28} />
          </div>
          <div>
            <div className="text-3xl font-extrabold text-primary leading-tight">{stat.value}</div>
            <div className="text-sm font-medium text-secondary">{stat.label}</div>
          </div>
        </Card>
      ))}
    </div>
  );
};