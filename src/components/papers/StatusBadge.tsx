import React from 'react';
import { Badge } from '../common/Badge';

interface StatusBadgeProps {
  status: 'pending' | 'processing' | 'completed' | 'failed';
}

const LABELS: Record<StatusBadgeProps['status'], string> = {
  pending: 'Pending',
  processing: 'Processing',
  completed: 'Processed',
  failed: 'Failed',
};

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const getVariant = () => {
    switch (status) {
      case 'completed': return 'success';
      case 'processing': return 'accent';
      case 'failed': return 'alert';
      default: return 'default';
    }
  };

  return <Badge variant={getVariant()}>{LABELS[status]}</Badge>;
};
