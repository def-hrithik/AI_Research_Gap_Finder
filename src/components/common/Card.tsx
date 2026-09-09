import React from 'react';
import { cn } from '../../utils/formatters';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  raised?: boolean;
  interactive?: boolean;
}

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, raised = false, interactive = false, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "bg-surface rounded-2xl border border-border overflow-hidden transition-all duration-300",
          raised && "shadow-md bg-surface-raised",
          interactive && "hover:-translate-y-1 hover:shadow-md cursor-pointer hover:border-accent/50",
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);
Card.displayName = 'Card';