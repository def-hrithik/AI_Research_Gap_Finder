import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';

export function usePapers(projectId?: string) {
  return useQuery({
    queryKey: ['papers', projectId],
    queryFn: () => api.getPapers(projectId!),
    enabled: !!projectId
  });
}

export function usePaper(paperId?: string) {
  return useQuery({
    queryKey: ['paper', paperId],
    queryFn: () => api.getPaper(paperId!),
    enabled: !!paperId
  });
}