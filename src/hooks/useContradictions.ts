import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import type { Contradiction } from '../types/contradiction';

export function useContradictions(projectId?: string) {
  return useQuery<Contradiction[]>({
    queryKey: ['contradictions', projectId],
    queryFn: () => api.getContradictions(projectId as string),
    enabled: !!projectId,
  });
}
