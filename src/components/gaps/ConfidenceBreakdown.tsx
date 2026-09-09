import React from 'react';
import type { ConfidenceBreakdown as CBType } from '../../types/gap';
export const ConfidenceBreakdown: React.FC<{ breakdown: CBType }> = ({ breakdown }) => {
  const metrics = [
    { label: 'Evidence Frequency', value: breakdown.evidenceFrequency },
    { label: 'Future-work Support', value: breakdown.futureWorkSupport },
    { label: 'Methodological Weakness', value: breakdown.methodologicalWeakness },
    { label: 'Topic Coverage', value: breakdown.topicCoverage },
  ];

  return (
    <div className="space-y-4">
      {metrics.map((metric, idx) => (
        <div key={idx}>
          <div className="flex justify-between items-center mb-1 text-sm">
            <span className="font-semibold text-primary">{metric.label}</span>
            <span className="font-bold text-accent">{metric.value}%</span>
          </div>
          <div className="h-2 w-full bg-surface-raised rounded-full overflow-hidden border border-border">
            <div 
              className="h-full bg-accent rounded-full transition-all duration-1000"
              style={{ width: `${metric.value}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
};