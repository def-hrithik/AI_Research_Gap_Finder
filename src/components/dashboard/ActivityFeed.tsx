import React from 'react';
import { Card } from '../common/Card';
import { FileText, Target, FolderKanban } from 'lucide-react';
import type { Project } from '../../types/project';
import { formatDate } from '../../utils/formatters';

interface ActivityFeedProps {
  projects?: Project[];
}

export const ActivityFeed: React.FC<ActivityFeedProps> = ({ projects = [] }) => {
  const activities = projects.flatMap(p => {
    const list = [];
    list.push({
      id: `${p.id}-upd`,
      text: `Project "${p.name}" updated`,
      time: formatDate(p.lastUpdated),
      icon: FolderKanban,
      color: 'text-accent',
    });
    if (p.paperCount > 0) {
      list.push({
        id: `${p.id}-pap`,
        text: `${p.paperCount} paper${p.paperCount > 1 ? 's' : ''} indexed in "${p.name}"`,
        time: formatDate(p.lastUpdated),
        icon: FileText,
        color: 'text-blue-500',
      });
    }
    if (p.gapCount > 0) {
      list.push({
        id: `${p.id}-gap`,
        text: `${p.gapCount} candidate gap${p.gapCount > 1 ? 's' : ''} detected in "${p.name}"`,
        time: formatDate(p.lastUpdated),
        icon: Target,
        color: 'text-alert',
      });
    }
    return list;
  }).slice(0, 5);

  return (
    <Card className="p-6">
      <h3 className="text-lg font-bold text-primary mb-6">Recent Activity</h3>
      {activities.length === 0 ? (
        <p className="text-sm text-secondary">No activity yet. Create a project to start analyzing literature.</p>
      ) : (
        <div className="space-y-6">
          {activities.map((item, idx) => (
            <div key={item.id} className="flex gap-4 relative">
              {idx !== activities.length - 1 && (
                <div className="absolute top-8 bottom-[-24px] left-5 w-px bg-border"></div>
              )}
              <div className="relative z-10 w-10 h-10 rounded-full bg-surface-raised border border-border flex items-center justify-center shrink-0">
                <item.icon size={18} className={item.color} />
              </div>
              <div className="pt-2">
                <p className="text-sm text-primary font-medium">{item.text}</p>
                <p className="text-xs text-secondary mt-1">{item.time}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
};