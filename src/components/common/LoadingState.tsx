import React from 'react';
import { Loader2 } from 'lucide-react';
import { cn } from '../../utils/formatters';

interface LoadingStateProps {
  message?: string;
  className?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({ message = 'Loading...', className }) => (
  <div className={cn("flex flex-col items-center justify-center p-12 text-secondary space-y-4", className)}>
    <Loader2 className="w-8 h-8 animate-spin text-accent" />
    <p className="text-sm font-medium">{message}</p>
  </div>
);