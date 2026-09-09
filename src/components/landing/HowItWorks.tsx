import React from 'react';
import { UploadCloud, Cpu, Target } from 'lucide-react';
import { Card } from '../common/Card';

const steps = [
  {
    num: "01", icon: UploadCloud, title: "Start with your literature",
    desc: "Drag and drop your curated PDFs. We parse the text, extracting methodologies, datasets, and explicit limitations."
  },
  {
    num: "02", icon: Cpu, title: "AI cross-paper synthesis",
    desc: "Our semantic engine reads across the literature, mapping out contradictions and aggregating repeated future-work suggestions."
  },
  {
    num: "03", icon: Target, title: "Get evidence-backed gaps",
    desc: "Review high-confidence research gap cards, complete with exact citations and page numbers proving why the gap exists."
  }
];

export const HowItWorks: React.FC = () => {
  return (
    <section className="py-24 px-6 bg-surface-raised border-y border-border" id="how-it-works">
      <div className="max-w-7xl mx-auto text-center mb-16">
        <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">How it works</h2>
        <p className="text-lg text-secondary max-w-2xl mx-auto">From messy PDFs to actionable research questions in minutes.</p>
      </div>
      <div className="max-w-7xl mx-auto grid md:grid-cols-3 gap-8">
        {steps.map((step, idx) => (
          <Card key={idx} raised className="p-8 relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-8 text-8xl font-black text-background opacity-50 group-hover:scale-110 transition-transform duration-500 pointer-events-none select-none">
              {step.num}
            </div>
            <div className="relative z-10">
              <div className="w-12 h-12 bg-accent/10 text-accent rounded-xl flex items-center justify-center mb-6">
                <step.icon size={24} />
              </div>
              <h3 className="text-xl font-bold mb-3">{step.title}</h3>
              <p className="text-secondary leading-relaxed">{step.desc}</p>
            </div>
          </Card>
        ))}
      </div>
    </section>
  );
};