import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import type { ResearchGap } from '../types/gap';

export function useGaps(projectId?: string) {
  return useQuery<ResearchGap[]>({
    queryKey: ['gaps', projectId],
    queryFn: () => api.getGaps(projectId as string),
    enabled: !!projectId,
  });
}

export function useGap(gapId?: string) {
  return useQuery<ResearchGap | undefined>({
    queryKey: ['gap', gapId],
    queryFn: () => api.getGap(gapId as string),
    enabled: !!gapId,
  });
}
