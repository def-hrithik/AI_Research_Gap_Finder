import React from 'react';
import { Card } from '../common/Card';

const quotes = [
  { name: "Dr. Sarah Jenkins", role: "Postdoctoral Researcher", quote: "It completely changed how I write literature reviews. What used to take a month of building spreadsheets now takes an afternoon." },
  { name: "Marcus Chen", role: "PhD Candidate in CS", quote: "The contradiction detection is brilliant. It found a subtle dataset bias across three papers that I had entirely missed while reading them manually." },
  { name: "Elena Rostova", role: "Graduate Research Assistant", quote: "Finally, an AI tool that actually provides exact page numbers and quotes instead of just making up a generic summary." }
];

export const Testimonials: React.FC = () => {
  return (
    <section className="py-24 px-6 bg-surface-raised border-y border-border overflow-hidden">
      <div className="max-w-7xl mx-auto">
        <h2 className="text-3xl font-bold tracking-tight mb-12 text-center">Trusted by researchers</h2>
        <div className="grid md:grid-cols-3 gap-8">
          {quotes.map((q, i) => (
            <Card key={i} raised className="p-8">
              <p className="text-primary italic mb-6">"{q.quote}"</p>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-accent/20 flex items-center justify-center text-accent font-bold">
                  {q.name.charAt(0)}
                </div>
                <div>
                  <div className="font-bold text-sm">{q.name}</div>
                  <div className="text-xs text-secondary">{q.role}</div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};