import React from 'react';
import { Layers } from 'lucide-react';

export const ProblemSection: React.FC = () => {
  return (
    <section className="py-24 px-6 max-w-7xl mx-auto">
      <div className="grid md:grid-cols-2 gap-16 items-center">
        <div>
          <div className="w-12 h-12 bg-alert/10 text-alert rounded-xl flex items-center justify-center mb-6">
            <Layers size={24} />
          </div>
          <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
            Hundreds of papers later, still wondering what's left to study?
          </h2>
          <p className="text-lg text-secondary leading-relaxed mb-6">
            Reading literature is easy. Synthesizing it is hard. Most AI tools just summarize individual papers, leaving you to manually piece together where the methodologies clash, which datasets are overused, and what limitations keep getting repeated.
          </p>
          <p className="text-lg text-secondary leading-relaxed">
            Nexus analyzes the structural relationships <span className="font-semibold text-primary">between</span> papers, automatically highlighting the white space in your research field.
          </p>
        </div>
        <div className="relative aspect-square md:aspect-auto md:h-[500px] bg-surface-raised rounded-3xl border border-border shadow-md overflow-hidden flex items-center justify-center">
          <div className="absolute inset-0 bg-gradient-to-br from-accent/5 to-transparent"></div>
          {/* Abstract visual representation of papers connecting */}
          <div className="relative z-10 text-center text-secondary p-8 border border-dashed border-border rounded-xl bg-surface">
            [ Interactive Graph Visualization Placeholder ]
          </div>
        </div>
      </div>
    </section>
  );
};