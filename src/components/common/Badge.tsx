import React from 'react';
import { cn } from '../../utils/formatters';

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'accent' | 'success' | 'alert' | 'outline';
}

export const Badge: React.FC<BadgeProps> = ({ variant = 'default', className, children, ...props }) => {
  const variants = {
    default: "bg-surface-raised text-secondary border border-border",
    accent: "bg-accent/10 text-accent border border-accent/20",
    success: "bg-success/10 text-success border border-success/20",
    alert: "bg-alert/10 text-alert border border-alert/20",
    outline: "bg-transparent text-secondary border border-border"
  };

  return (
    <span
      className={cn("inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold", variants[variant], className)}
      {...props}
    >
      {children}
    </span>
  );
};