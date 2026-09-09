import React from 'react';
import { useParams } from 'react-router-dom';
import { AlertCircle } from 'lucide-react';
import { useContradictions } from '../hooks/useContradictions';
import { ContradictionCard } from '../components/contradictions/ContradictionCard';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { EmptyState } from '../components/common/EmptyState';
import { Card } from '../components/common/Card';

export const ContradictionsPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const { data: contradictions, isLoading, isError, refetch } = useContradictions(projectId);

  if (isLoading) return <LoadingState message="Detecting literary contradictions..." />;
  if (isError) return <ErrorState onRetry={refetch} />;

  return (
    <div className="max-w-5xl mx-auto space-y-6 animate-in fade-in duration-300">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-primary mb-2">Contradiction Analysis</h2>
        <p className="text-secondary">Explore areas where the literature produces conflicting claims or experimental results.</p>
      </div>

      <Card className="p-4 mb-8 bg-alert/5 border-alert/20 flex items-start gap-3">
        <AlertCircle size={20} className="text-alert shrink-0 mt-0.5" />
        <p className="text-sm text-primary leading-relaxed">
          <strong className="font-bold">Important:</strong> These are <span className="italic">Candidate Contradictions</span> surfaced by AI pattern matching. They are not proven facts. Always review the full experimental context to determine if the claims are genuinely opposed or simply examining different variables.
        </p>
      </Card>

      {!contradictions || contradictions.length === 0 ? (
        <EmptyState 
          icon={<AlertCircle size={24} />}
          title="No contradictions detected"
          description="The AI did not find any high-confidence conflicting claims in the current project literature."
        />
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