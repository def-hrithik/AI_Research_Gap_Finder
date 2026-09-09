import React from 'react';
import { useParams } from 'react-router-dom';
import { useGaps } from '../hooks/useGaps';
import { GapFilters } from '../components/gaps/GapFilters';
import { GapCard } from '../components/gaps/GapCard';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { EmptyState } from '../components/common/EmptyState';
import { Target } from 'lucide-react';

export const GapsPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const { data: gaps, isLoading, isError, refetch } = useGaps(projectId);

  if (isLoading) return <LoadingState message="Synthesizing literature gaps..." />;
  if (isError) return <ErrorState onRetry={refetch} />;

  return (
    <div className="max-w-6xl mx-auto animate-in fade-in duration-300 space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-primary mb-2">Candidate Research Gaps</h2>
        <p className="text-secondary max-w-3xl">AI-generated prioritization signals based on literature evidence. These are potential areas requiring human review, not proven facts.</p>
      </div>

      <GapFilters />

      {!gaps || gaps.length === 0 ? (
        <EmptyState 
          icon={<Target size={24} />}
          title="No research gaps found yet"
          description="Upload more papers to give the AI enough context to find missing links."
        />
      ) : (
        <div className="space-y-12">
          {gaps.map((gap) => (
            <GapCard key={gap.id} gap={gap} />
          ))}
        </div>
      )}
    </div>
  );
};