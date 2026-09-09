import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, ExternalLink, ShieldCheck } from 'lucide-react';
import { usePaper } from '../hooks/usePapers';
import { Button } from '../components/common/Button';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';

export const PaperDetailsPage: React.FC = () => {
  const { paperId } = useParams<{ paperId: string }>();
  const navigate = useNavigate();
  const { data: paper, isLoading, isError, refetch } = usePaper(paperId);

  if (isLoading) return <LoadingState message="Loading paper analysis..." className="mt-20" />;
  if (isError || !paper) return <ErrorState onRetry={refetch} className="mt-20" />;

  if (!paper.analysis) {
    return (
      <div className="max-w-3xl mx-auto mt-20 text-center space-y-3">
        <Button variant="ghost" onClick={() => navigate(-1)} className="gap-2 px-0 hover:bg-transparent text-secondary hover:text-primary">
          <ArrowLeft size={18} /> Back to Project
        </Button>
        <h1 className="text-xl font-bold text-primary">{paper.title}</h1>
        <p className="text-secondary">
          {paper.analysisStatus === 'processing'
            ? 'This paper is still being analyzed. Check back shortly.'
            : 'This paper has not been analyzed yet.'}
        </p>
        <Badge variant={paper.analysisStatus === 'processing' ? 'accent' : 'default'}>
          {paper.analysisStatus}
        </Badge>
      </div>
    );
  }

  const AnalysisSection = ({ title, content, type = 'AI Analysis' }: { title: string, content: React.ReactNode, type?: 'AI Analysis' | 'Direct Evidence' }) => (
    <div className="border-b border-border py-6 last:border-0">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-primary">{title}</h3>
        <Badge variant={type === 'Direct Evidence' ? 'success' : 'accent'}>
          {type === 'Direct Evidence' ? <><ShieldCheck size={12} className="mr-1"/> Direct Evidence</> : 'AI Analysis'}
        </Badge>
      </div>
      <div className="text-secondary leading-relaxed space-y-2">
        {content}
      </div>
    </div>
  );

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <Button variant="ghost" onClick={() => navigate(-1)} className="gap-2 px-0 hover:bg-transparent text-secondary hover:text-primary">
        <ArrowLeft size={18} /> Back to Project
      </Button>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Main Content: AI Structured Analysis */}
        <div className="lg:col-span-2 space-y-6">
          <Card className="p-8">
            <h1 className="text-2xl font-extrabold text-primary mb-4 leading-tight">{paper.title}</h1>
            <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-sm text-secondary mb-8 border-b border-border pb-6">
              <span className="font-semibold text-primary">{paper.authors.join(', ')}</span>
              <span>{paper.venue}</span>
              <span>{paper.year}</span>
            </div>

            <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
              Structured Extraction
            </h2>

            <AnalysisSection 
              title="Core Problem & Objective" 
              content={<p>{paper.analysis.problem}</p>} 
            />
            
            <AnalysisSection 
              title="Methodology & Approach" 
              content={<p>{paper.analysis.methodology}</p>} 
            />

            <AnalysisSection 
              title="Models & Architecture" 
              content={
                <div className="flex flex-wrap gap-2">
                  {paper.analysis.models.map((m, i) => <Badge key={i} variant="outline">{m}</Badge>)}
                </div>
              } 
            />

            <AnalysisSection 
              title="Datasets Used" 
              type="Direct Evidence"
              content={
                <div className="flex flex-wrap gap-2">
                  {paper.analysis.dataset.map((d, i) => <Badge key={i} variant="outline">{d}</Badge>)}
                </div>
              } 
            />

            <AnalysisSection 
              title="Key Findings" 
              content={<p>{paper.analysis.findings}</p>} 
            />

            <AnalysisSection 
              title="Stated Limitations" 
              type="Direct Evidence"
              content={
                <ul className="list-disc pl-5 space-y-2">
                  {paper.analysis.limitations.map((l, i) => <li key={i}>{l}</li>)}
                </ul>
              } 
            />

            <AnalysisSection 
              title="Suggested Future Work" 
              type="Direct Evidence"
              content={
                <ul className="list-disc pl-5 space-y-2">
                  {paper.analysis.futureWork.map((fw, i) => <li key={i}>{fw}</li>)}
                </ul>
              } 
            />
          </Card>
        </div>

        {/* Side Panel: Metadata and Evidence Traceability */}
        <div className="space-y-6">
          <Card raised className="p-6">
            <h3 className="font-bold text-primary mb-4">Document Details</h3>
            <div className="space-y-4 text-sm">
              <div>
                <span className="block text-secondary font-semibold uppercase tracking-wider text-xs mb-1">Status</span>
                <Badge variant="success">Fully Processed</Badge>
              </div>
              <div>
                <span className="block text-secondary font-semibold uppercase tracking-wider text-xs mb-1">Internal ID</span>
                <span className="text-primary font-mono bg-surface-raised px-2 py-1 rounded-md border border-border">{paper.id}</span>
              </div>
              <Button variant="secondary" fullWidth className="gap-2 mt-4">
                View Source PDF <ExternalLink size={16} />
              </Button>
            </div>
          </Card>

          <Card className="p-6 bg-accent/5 border-accent/20">
            <h3 className="font-bold text-primary mb-2 flex items-center gap-2">
              <ShieldCheck size={18} className="text-accent" /> Evidence Traceability
            </h3>
            <p className="text-sm text-secondary leading-relaxed mb-4">
              Sections marked as <strong className="text-primary">Direct Evidence</strong> are extracted verbatim or near-verbatim from the source text. AI Analysis sections are synthesized interpretations.
            </p>
            <div className="text-xs p-3 bg-surface rounded-xl border border-border text-secondary italic">
              "We prioritize transparent lineage so you can confidently cite the underlying findings without hallucination risk."
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};