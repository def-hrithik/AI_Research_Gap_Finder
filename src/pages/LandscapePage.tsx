import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { TopicClusterChart } from '../components/landscape/TopicClusterChart';
import { MethodUsageChart } from '../components/landscape/MethodUsageChart';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { api } from '../services/api';

export const LandscapePage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const { data: landscape, isLoading, isError, refetch } = useQuery({
    queryKey: ['landscape', projectId],
    queryFn: () => api.getLandscape(projectId!),
    enabled: !!projectId,
  });

  if (isLoading) return <LoadingState message="Mapping literature landscape..." className="mt-20" />;
  if (isError) return <ErrorState onRetry={refetch} className="mt-20" />;

  const topicClusters = landscape?.topicClusters || [];
  const methodologies = landscape?.methodologies || [];
  const repeatedLimitations = landscape?.repeatedLimitations || [];

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-300">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-primary mb-2">Research Landscape</h2>
        <p className="text-secondary">A visual map of the field, highlighting common methodologies and structural patterns.</p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <TopicClusterChart data={topicClusters} />
        
        <div className="space-y-6">
          <MethodUsageChart data={methodologies} />
          
          <Card className="p-6">
            <h3 className="font-bold text-primary mb-1">Repeated Limitations</h3>
            <p className="text-sm text-secondary mb-4">Ranked by frequency across literature</p>
            {repeatedLimitations.length === 0 ? (
              <p className="text-sm text-secondary">No repeated limitations extracted yet.</p>
            ) : (
              <div className="space-y-3">
                {repeatedLimitations.map((lim: any, i: number) => (
                  <div key={i} className="flex justify-between items-center p-3 rounded-xl bg-surface-raised border border-border">
                    <span className="text-sm font-medium text-primary line-clamp-1">{lim.label}</span>
                    <Badge variant="default" className="shrink-0 ml-2">{lim.count} Papers</Badge>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
};