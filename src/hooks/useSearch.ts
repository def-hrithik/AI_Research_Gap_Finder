import { useState } from 'react';

// Mocking the search behavior since we don't have a real RAG backend yet
export function useSearch(_projectId?: string) {
  const [isSearching, setIsSearching] = useState(false);
  const [results, setResults] = useState<any>(null);

  const search = (_query: string) => {
    setIsSearching(true);
    // Simulate network delay and AI processing
    setTimeout(() => {
      setResults({
        answer: "Based on the literature, transformer architectures (like ClinicalBERT) consistently outperform traditional CNNs on sequential electronic health records. However, a major recurring limitation is the lack of cross-demographic validation, as most models are trained exclusively on Western datasets such as MIMIC-III.",
        sources: [
          {
            id: 'src-1',
            paperTitle: "Transformer Models for Early Diabetes Detection: A Review",
            section: "Findings",
            page: 4,
            text: "Transformers outperform CNNs on sequential patient data by 12% across all tested benchmarks.",
            relevance: 96
          },
          {
            id: 'src-2',
            paperTitle: "Evaluating CNN robustness on non-Western clinical datasets",
            section: "Introduction",
            page: 1,
            text: "Accuracy drops significantly when evaluating Western-trained models on SE Asian datasets.",
            relevance: 82
          }
        ]
      });
      setIsSearching(false);
    }, 1500);
  };

  return { search, isSearching, results };
}