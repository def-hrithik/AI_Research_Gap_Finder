import React from 'react';
import { TopicClusterChart } from '../components/landscape/TopicClusterChart';
import { MethodUsageChart } from '../components/landscape/MethodUsageChart';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';

export const LandscapePage: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-300">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-primary mb-2">Research Landscape</h2>
        <p className="text-secondary">A visual map of the field, highlighting common methodologies and structural patterns.</p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <TopicClusterChart />
        
        <div className="space-y-6">
          <MethodUsageChart />
          
          <Card className="p-6">
            <h3 className="font-bold text-primary mb-1">Repeated Limitations</h3>
            <p className="text-sm text-secondary mb-4">Ranked by frequency across literature</p>
            <div className="space-y-3">
              {[
                { label: "Lack of cross-demographic validation", count: 8 },
                { label: "Small sample sizes in dataset", count: 5 },
                { label: "High computational training overhead", count: 4 },
                { label: "Retrospective rather than prospective", count: 3 }
              ].map((lim, i) => (
                <div key={i} className="flex justify-between items-center p-3 rounded-xl bg-surface-raised border border-border">
                  <span className="text-sm font-medium text-primary">{lim.label}</span>
                  <Badge variant="default">{lim.count} Papers</Badge>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};