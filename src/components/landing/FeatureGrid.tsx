import React from 'react';
import { ShieldCheck, Network, Scale, FileSearch, Clock, Zap } from 'lucide-react';

const features = [
  { icon: ShieldCheck, title: "Evidence-backed, not guesswork", desc: "Every generated gap is tied to direct quotes from your uploaded PDFs. No hallucinations." },
  { icon: Network, title: "Cross-paper synthesis", desc: "We don't summarize single papers. We compare methods and findings across your entire project library." },
  { icon: Scale, title: "Confidence Scoring", desc: "Our engine weighs the frequency of limitations against recent findings to give each gap a confidence score." },
  { icon: Zap, title: "Contradiction Detection", desc: "Automatically flag when Paper A's findings directly conflict with Paper B's experimental results." },
  { icon: FileSearch, title: "Traceable Citations", desc: "Click any claim to instantly see the source paper, section, and exact page number." },
  { icon: Clock, title: "Recency-aware", desc: "The algorithm weights newer papers higher when determining if a gap has already been filled." }
];

export const FeatureGrid: React.FC = () => {
  return (
    <section className="py-24 px-6 max-w-7xl mx-auto">
      <div className="text-center mb-16">
        <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">What makes it stand out</h2>
        <p className="text-lg text-secondary">Built for academic rigor, designed like a modern tool.</p>
      </div>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-8 md:gap-12">
        {features.map((f, i) => (
          <div key={i} className="flex gap-4">
            <div className="mt-1 shrink-0 w-10 h-10 rounded-xl bg-surface border border-border flex items-center justify-center text-accent shadow-sm">
              <f.icon size={20} />
            </div>
            <div>
              <h3 className="font-bold text-lg mb-2">{f.title}</h3>
              <p className="text-secondary text-sm leading-relaxed">{f.desc}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};