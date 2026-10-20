import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { AlertCircle, Sparkles, Loader2 } from 'lucide-react';
import { useContradictions } from '../hooks/useContradictions';
import { api } from '../services/api';
import { ContradictionCard } from '../components/contradictions/ContradictionCard';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { EmptyState } from '../components/common/EmptyState';
import { Button } from '../components/common/Button';
import { Card } from '../components/common/Card';

export const ContradictionsPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const { data: contradictions, isLoading, isError, refetch } = useContradictions(projectId);
  const [isSynthesizing, setIsSynthesizing] = useState(false);

  const handleSynthesize = async () => {
    if (!projectId) return;
    try {
      setIsSynthesizing(true);
      await api.startAnalysis(projectId);
      await refetch();
    } catch (err) {
      console.error('Detection failed:', err);
    } finally {
      setIsSynthesizing(false);
    }
  };

  if (isLoading) return <LoadingState message="Detecting literary contradictions..." />;
  if (isError) return <ErrorState onRetry={refetch} />;

  return (
    <div className="max-w-5xl mx-auto space-y-6 animate-in fade-in duration-300">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h2 className="text-2xl font-bold text-primary mb-2">Contradiction Analysis</h2>
          <p className="text-secondary">Explore areas where the literature produces conflicting claims or experimental results.</p>
        </div>
        <Button 
          variant="secondary" 
          onClick={handleSynthesize} 
          disabled={isSynthesizing} 
          className="gap-2 shrink-0"
        >
          {isSynthesizing ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
          {isSynthesizing ? 'Detecting...' : 'Detect Contradictions with AI'}
        </Button>
      </div>

      <Card className="p-4 mb-8 bg-alert/5 border-alert/20 flex items-start gap-3">
        <AlertCircle size={20} className="text-alert shrink-0 mt-0.5" />
        <p className="text-sm text-primary leading-relaxed">
          <strong className="font-bold">Important:</strong> These are <span className="italic">Candidate Contradictions</span> surfaced by AI pattern matching. They are not proven facts. Always review the full experimental context to determine if the claims are genuinely opposed or simply examining different variables.
        </p>
      </Card>

      {!contradictions || contradictions.length === 0 ? (
        <div className="space-y-4">
          <EmptyState 
            icon={<AlertCircle size={24} />}
            title="No contradictions detected"
            description="Click below to run AI contradiction detection across your papers to surface points of tension."
          />
          <div className="flex justify-center">
            <Button onClick={handleSynthesize} disabled={isSynthesizing} className="gap-2">
              {isSynthesizing ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
              {isSynthesizing ? 'Detecting Contradictions...' : 'Run Contradiction Detection with AI'}
            </Button>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          {contradictions.map(contra => (
            <ContradictionCard key={contra.id} contradiction={contra} />
          ))}
        </div>
      )}
    </div>
  );
};