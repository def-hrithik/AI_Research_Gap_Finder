import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Target, ShieldAlert } from 'lucide-react';
import { useGap } from '../hooks/useGaps';
import { Button } from '../components/common/Button';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { EvidenceList } from '../components/gaps/EvidenceList';
import { ConfidenceBreakdown } from '../components/gaps/ConfidenceBreakdown';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';

export const GapDetailsPage: React.FC = () => {
  const { gapId } = useParams<{ gapId: string }>();
  const navigate = useNavigate();
  const { data: gap, isLoading, isError, refetch } = useGap(gapId);

  if (isLoading) return <LoadingState message="Loading gap analysis..." className="mt-20" />;
  if (isError || !gap) return <ErrorState onRetry={refetch} className="mt-20" />;

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-in fade-in duration-300">
      <Button variant="ghost" onClick={() => navigate(-1)} className="gap-2 px-0 hover:bg-transparent text-secondary hover:text-primary">
        <ArrowLeft size={18} /> Back to Gaps
      </Button>

      <div className="grid lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          <div>
            <div className="flex items-center gap-3 mb-4">
              <Badge variant="accent" className="bg-accent/10">AI-Generated Potential Research Gap</Badge>
              <Badge variant="outline">{gap.type}</Badge>
            </div>
            <h1 className="text-3xl font-extrabold text-primary leading-tight mb-4">{gap.suggestedQuestion}</h1>
            <p className="text-lg text-secondary leading-relaxed">{gap.description}</p>
          </div>

          <Card className="p-6 bg-surface-raised border-border">
            <h3 className="font-bold text-primary mb-2 uppercase tracking-wider text-xs">Suggested Methodology</h3>
            <p className="text-primary font-medium">{gap.suggestedMethodology}</p>
          </Card>

          <div>
            <h2 className="text-xl font-bold text-primary mb-4 flex items-center gap-2">
              Traceable Evidence
            </h2>
            <EvidenceList evidence={gap.evidence} />
          </div>
        </div>

        <div className="space-y-6">
          {/* Signature Motif Card for details */}
          <Card raised className="p-6 border-t-4 border-t-accent">
            <div className="flex justify-between items-start mb-6">
              <div className="w-10 h-10 rounded-full bg-accent/10 flex items-center justify-center text-accent">
                <Target size={20} />
              </div>
              <div className="text-right">
                <div className="text-3xl font-black text-primary leading-none">{gap.confidence}%</div>
                <div className="text-[10px] font-bold text-secondary uppercase tracking-wider mt-1">Confidence Score</div>
              </div>
            </div>
            
            <h3 className="font-bold text-primary mb-4 text-sm uppercase tracking-wider">Scoring Breakdown</h3>
            <ConfidenceBreakdown breakdown={gap.confidenceBreakdown} />
            
            <div className="mt-6 pt-4 border-t border-border flex items-start gap-2 text-xs text-secondary">
              <ShieldAlert size={14} className="text-accent shrink-0 mt-0.5" />
              <p>Confidence is an AI-generated prioritization signal based on structural literature mapping, not proof of existence.</p>
            </div>
          </Card>

          <Card className="p-6">
            <h3 className="font-bold text-primary mb-4 text-sm uppercase tracking-wider">Supporting Papers</h3>
            <div className="flex flex-wrap gap-2">
              {gap.supportingPaperIds.map((id) => (
                <Badge key={id} variant="default" className="bg-background py-1">Paper ID: {id}</Badge>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};