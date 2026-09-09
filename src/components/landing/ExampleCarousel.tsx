import React from 'react';
import { Card } from '../common/Card';
import { Target, FileText } from 'lucide-react';

const examples = [
  { topic: 'Climate & Permafrost', confidence: 92, papers: 14, gap: 'Long-term microbial respiration data in deep permafrost is missing.' },
  { topic: 'Cancer Biology', confidence: 88, papers: 32, gap: 'In-vivo validation of the CD44 pathway in pediatric cases remains untested.' },
  { topic: 'Neuroscience', confidence: 95, papers: 18, gap: 'Contradictory findings in dopamine baseline levels during REM sleep.' },
  { topic: 'Space Science', confidence: 81, papers: 9, gap: 'Radiation shielding degradation metrics beyond 5-year missions.' }
];

export const ExampleCarousel: React.FC = () => {
  return (
    <section className="py-16 px-6 overflow-hidden bg-surface-raised border-y border-border" id="product">
      <div className="max-w-7xl mx-auto mb-10 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold tracking-tight mb-2">See it in action</h2>
          <p className="text-secondary text-lg">Real evidence. Traceable sources. Actionable gaps.</p>
        </div>
      </div>
      
      {/* Signature Motif Implementation in Cards */}
      <div className="flex gap-6 overflow-x-auto pb-8 snap-x snap-mandatory hide-scrollbar max-w-7xl mx-auto px-6 -mx-6">
        {examples.map((ex, idx) => (
          <Card key={idx} interactive className="min-w-[320px] md:min-w-[400px] snap-center p-6 flex flex-col">
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm font-semibold text-secondary uppercase tracking-wider">{ex.topic}</span>
              <div className="bg-accent/10 text-accent font-bold px-3 py-1 rounded-lg flex items-center gap-1 text-sm border border-accent/20">
                <Target size={14} /> {ex.confidence}% Gap
              </div>
            </div>
            <p className="text-lg font-medium text-primary mb-6 flex-1">
              "{ex.gap}"
            </p>
            <div className="flex items-center gap-2 pt-4 border-t border-border">
              <div className="flex -space-x-2">
                {[1,2,3].map(i => (
                  <div key={i} className="w-8 h-8 rounded-full bg-surface border-2 border-surface-raised flex items-center justify-center text-secondary shadow-sm">
                    <FileText size={12} />
                  </div>
                ))}
              </div>
              <span className="text-xs text-secondary font-medium ml-2">Derived from {ex.papers} sources</span>
            </div>
          </Card>
        ))}
      </div>
    </section>
  );
};