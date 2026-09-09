import React from 'react';

const suggestions = [
  "What methods produce conflicting results?",
  "Which datasets are underused?",
  "What limitations are repeated across the literature?",
  "What future work is most frequently suggested?"
];

export const SuggestedQuestions: React.FC<{ onSelect: (q: string) => void }> = ({ onSelect }) => (
  <div className="mt-8">
    <p className="text-sm font-semibold text-secondary uppercase tracking-wider mb-4 text-center">Suggested Queries</p>
    <div className="flex flex-wrap justify-center gap-3">
      {suggestions.map((q, i) => (
        <button
          key={i}
          onClick={() => onSelect(q)}
          className="px-4 py-2 rounded-xl border border-border bg-surface text-sm text-secondary hover:text-primary hover:border-accent/50 hover:shadow-sm transition-all"
        >
          {q}
        </button>
      ))}
    </div>
  </div>
);