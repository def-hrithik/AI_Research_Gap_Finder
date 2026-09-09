import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { usePapers } from '../hooks/usePapers';
import { PaperFilters } from '../components/papers/PaperFilters';
import { PaperTable } from '../components/papers/PaperTable';
import { PaperCard } from '../components/papers/PaperCard';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { EmptyState } from '../components/common/EmptyState';

export const PapersPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const { data: papers, isLoading, isError, refetch } = usePapers(projectId);
  const [viewMode, setViewMode] = useState<'list' | 'grid'>('list');

  if (isLoading) return <LoadingState message="Loading papers..." />;
  if (isError) return <ErrorState onRetry={refetch} />;

  if (!papers || papers.length === 0) {
    return (
      <EmptyState 
        title="No papers found" 
        description="Upload PDF documents to begin synthesizing the research landscape."
      />
    );
  }

  return (
    <div className="animate-in fade-in duration-300">
      <PaperFilters viewMode={viewMode} setViewMode={setViewMode} />
      
      {viewMode === 'list' ? (
        <PaperTable papers={papers} />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {papers.map(paper => (
            <PaperCard key={paper.id} paper={paper} />
          ))}
        </div>
      )}
    </div>
  );
};