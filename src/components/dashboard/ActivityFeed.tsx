import React from 'react';
import { Card } from '../common/Card';
import { FileText, Target, AlertTriangle, CheckCircle2 } from 'lucide-react';

const activities = [
  { id: 1, type: 'gap', text: 'New candidate gap identified in Machine Learning project', time: '2 hours ago', icon: Target, color: 'text-accent' },
  { id: 2, type: 'paper', text: 'Processed "Transformer Models for Early..."', time: '4 hours ago', icon: FileText, color: 'text-blue-500' },
  { id: 3, type: 'contradiction', text: 'Potential contradiction found between Paper A and Paper B', time: '1 day ago', icon: AlertTriangle, color: 'text-alert' },
  { id: 4, type: 'project', text: 'Project "NLP for Low-Resource" analysis completed', time: '2 days ago', icon: CheckCircle2, color: 'text-success' },
];

export const ActivityFeed: React.FC = () => {
  return (
    <Card className="p-6">
      <h3 className="text-lg font-bold text-primary mb-6">Recent Activity</h3>
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
    </Card>
  );
};