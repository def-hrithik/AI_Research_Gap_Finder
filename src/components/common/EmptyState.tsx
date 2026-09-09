import React from 'react';
import { FileQuestion } from 'lucide-react';
import { cn } from '../../utils/formatters';

interface EmptyStateProps {
  title: string;
  description: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ title, description, icon, action, className }) => (
  <div className={cn("flex flex-col items-center justify-center p-12 text-center rounded-2xl border border-dashed border-border bg-surface-raised/50", className)}>
    <div className="w-12 h-12 rounded-full bg-surface border border-border flex items-center justify-center text-secondary mb-4 shadow-sm">
      {icon || <FileQuestion size={24} />}
    </div>
    <h3 className="text-lg font-bold text-primary mb-2">{title}</h3>
    <p className="text-secondary text-sm max-w-sm mb-6">{description}</p>
    {action}
  </div>
);