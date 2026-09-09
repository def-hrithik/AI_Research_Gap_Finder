import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { usePapers } from '../hooks/usePapers';
import { PaperMultiSelect } from '../components/comparison/PaperMultiSelect';
import { ComparisonTable } from '../components/comparison/ComparisonTable';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { EmptyState } from '../components/common/EmptyState';
import { Layers } from 'lucide-react';

export const ComparePage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const { data: papers, isLoading, isError, refetch } = usePapers(projectId);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  if (isLoading) return <LoadingState message="Loading literature matrix..." />;
  if (isError) return <ErrorState onRetry={refetch} />;

  if (!papers || papers.length === 0) {
    return <EmptyState title="No papers to compare" description="Upload papers first." />;
  }

  // Pre-select first two papers by default if none are selected
  if (selectedIds.length === 0 && papers.length >= 2) {
    setSelectedIds([papers[0].id, papers[1].id]);
  }

  const handleToggle = (id: string) => {
    setSelectedIds(prev => 
      prev.includes(id) ? prev.filter(pId => pId !== id) : [...prev, id]
    );
  };

  const selectedPapers = papers.filter(p => selectedIds.includes(p.id));

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-300">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-primary mb-2">Paper Comparison</h2>
        <p className="text-secondary">Identify methodological differences and conflicting findings side-by-side.</p>
      </div>

      <PaperMultiSelect 
        papers={papers} 
        selectedIds={selectedIds} 
        onToggle={handleToggle} 
      />

      {selectedPapers.length > 0 ? (
        <ComparisonTable papers={selectedPapers} />
      ) : (
        <EmptyState 
          icon={<Layers size={24} />}
          title="Select papers to compare"
          description="Choose at least one paper from the list above to view its structured analysis."
        />
      )}
    </div>
  );
};