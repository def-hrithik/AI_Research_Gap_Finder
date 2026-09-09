import type { Contradiction } from '../types/contradiction';

export const mockContradictions: Contradiction[] = [
  {
    id: 'contra-1',
    projectId: 'proj-1',
    topic: 'Model Generalization',
    paperAId: 'paper-001',
    paperAClaim:
      'Transformer architectures maintain 94% accuracy across diverse age groups with minimal fine-tuning.',
    paperBId: 'paper-002',
    paperBClaim:
      'All tested models, including attention-based variants, experienced a severe 18% accuracy drop when applied to non-Western demographics.',
    experimentalContext: 'Zero-shot evaluation on diverse clinical demographics.',
    dataset: 'Multi-site clinical imaging cohort',
    method: 'Transformer-based classification',
    confidenceScore: 81,
  },
];
