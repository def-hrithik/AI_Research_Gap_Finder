import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useGaps } from '../hooks/useGaps';
import { api } from '../services/api';
import { GapFilters } from '../components/gaps/GapFilters';
import { GapCard } from '../components/gaps/GapCard';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { EmptyState } from '../components/common/EmptyState';
import { Button } from '../components/common/Button';
import { Target, Sparkles, Loader2 } from 'lucide-react';

export const GapsPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const { data: gaps, isLoading, isError, refetch } = useGaps(projectId);
  const [isSynthesizing, setIsSynthesizing] = useState(false);

  const handleSynthesize = async () => {
    if (!projectId) return;
    try {
      setIsSynthesizing(true);
      await api.startAnalysis(projectId);
      await refetch();
    } catch (err) {
      console.error('Synthesis failed:', err);
    } finally {
      setIsSynthesizing(false);
    }
  };

  if (isLoading) return <LoadingState message="Synthesizing literature gaps..." />;
  if (isError) return <ErrorState onRetry={refetch} />;

  return (
    <div className="max-w-6xl mx-auto animate-in fade-in duration-300 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-primary mb-2">Candidate Research Gaps</h2>
          <p className="text-secondary max-w-3xl">AI-generated prioritization signals based on literature evidence. These are potential areas requiring human review, not proven facts.</p>
        </div>
        <Button 
          variant="secondary" 
          onClick={handleSynthesize} 
          disabled={isSynthesizing} 
          className="gap-2 shrink-0"
        >
          {isSynthesizing ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
          {isSynthesizing ? 'Synthesizing...' : 'Synthesize Gaps with AI'}
        </Button>
      </div>

      <GapFilters />

      {!gaps || gaps.length === 0 ? (
        <div className="space-y-4">
          <EmptyState 
            icon={<Target size={24} />}
            title="No research gaps found yet"
            description="Upload papers and run synthesis to identify candidate research gaps across the literature."
          />
          <div className="flex justify-center">
            <Button onClick={handleSynthesize} disabled={isSynthesizing} className="gap-2">
              {isSynthesizing ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
              {isSynthesizing ? 'Synthesizing Gaps...' : 'Run Gap Discovery with AI'}
            </Button>
          </div>
        </div>
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