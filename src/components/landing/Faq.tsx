import React, { useState } from 'react';
import { ChevronDown } from 'lucide-react';
import { cn } from '../../utils/formatters';

const faqs = [
  { q: "What is a research gap finder?", a: "Unlike standard chatbots that summarize text, Nexus specifically looks for structural patterns in literature: repeated limitations, methodological weaknesses, and explicit calls for future work." },
  { q: "How does it calculate confidence scores?", a: "Scores are derived from a weighted matrix considering evidence frequency, how explicitly authors state a limitation, and the recency of the papers involved." },
  { q: "Can I trust the generated gaps?", a: "Nexus provides candidate gaps, not proven facts. Every claim includes direct traceable evidence (paper, section, page, quote) so you can verify the context yourself." },
  { q: "Does it work with any discipline?", a: "Yes, provided the uploaded PDFs are standard academic papers with clear methodology, findings, and limitation sections. It works exceptionally well in STEM and social sciences." }
];

export const Faq: React.FC = () => {
  const [open, setOpen] = useState<number | null>(0);

  return (
    <section className="py-24 px-6 max-w-3xl mx-auto">
      <h2 className="text-3xl font-bold tracking-tight mb-10 text-center">Frequently asked questions</h2>
      <div className="space-y-4">
        {faqs.map((faq, i) => (
          <div key={i} className="border border-border bg-surface rounded-2xl overflow-hidden transition-all duration-200">
            <button 
              onClick={() => setOpen(open === i ? null : i)}
              className="w-full flex items-center justify-between p-6 text-left focus:outline-none"
            >
              <span className="font-bold">{faq.q}</span>
              <ChevronDown className={cn("text-secondary transition-transform", open === i && "rotate-180")} size={20} />
            </button>
            <div className={cn("px-6 pb-6 text-secondary overflow-hidden text-sm leading-relaxed", open === i ? "block" : "hidden")}>
              {faq.a}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};