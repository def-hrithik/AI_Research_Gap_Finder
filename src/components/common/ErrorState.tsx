import React from 'react';
import { AlertTriangle } from 'lucide-react';
import { Button } from './Button';
import { cn } from '../../utils/formatters';

interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
  className?: string;
}

export const ErrorState: React.FC<ErrorStateProps> = ({ message = 'Something went wrong.', onRetry, className }) => (
  <div className={cn("flex flex-col items-center justify-center p-12 text-center", className)}>
    <AlertTriangle className="w-10 h-10 text-alert mb-4 opacity-80" />
    <h3 className="text-lg font-bold text-primary mb-2">Error Loading Data</h3>
    <p className="text-secondary text-sm mb-6">{message}</p>
    {onRetry && (
      <Button variant="secondary" onClick={onRetry}>Try Again</Button>
    )}
  </div>
);