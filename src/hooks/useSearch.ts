import { useState } from 'react';
import { api } from '../services/api';

export function useSearch(projectId?: string) {
  const [isSearching, setIsSearching] = useState(false);
  const [results, setResults] = useState<{ answer: string; sources: any[]; insufficientEvidence: boolean } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const search = async (query: string) => {
    if (!query.trim() || !projectId) return;
    setIsSearching(true);
    setError(null);
    try {
      const res = await api.search(projectId, query);
      setResults(res);
    } catch (err: any) {
      console.error('Search failed:', err);
      setError(err?.response?.data?.error?.message || err?.message || 'Failed to execute semantic search.');
      setResults(null);
    } finally {
      setIsSearching(false);
    }
  };

  return { search, isSearching, results, error };
}