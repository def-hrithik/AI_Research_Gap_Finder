import type { ResearchGap } from '../types/gap';

export const mockGaps: ResearchGap[] = [
  {
    id: 'gap-001',
    projectId: 'proj-001',
    type: 'Underexplored Area',
    confidence: 87,
    topic: 'Cross-demographic generalization of Transformers',
    description: 'Existing literature focuses heavily on CNN robustness across demographics, while the geographic generalization of newly proposed Transformer models remains comparatively underexplored.',
    evidence: [
      {
        paperId: 'paper-001',
        section: 'Limitations',
        page: 8,
        text: 'Our transformer models were trained exclusively on US-centric datasets, limiting geographic applicability.',
        relationshipToGap: 'Confirms lack of diversity in transformer training.',
        relevanceScore: 92
      },
      {
        paperId: 'paper-002',
        section: 'Future Work',
        page: 11,
        text: 'Future studies must evaluate newer attention-based models on these diverse datasets.',
        relationshipToGap: 'Directly calls for this specific research direction.',
        relevanceScore: 95
      }
    ],
    supportingPaperIds: ['paper-001', 'paper-002'],
    suggestedQuestion: 'How do Vision Transformer models perform when zero-shot evaluated on non-Western clinical datasets compared to CNNs?',
    suggestedMethodology: 'Benchmarking pre-trained ViT models on AfriMed DB and AsianHealth DB.',
    confidenceBreakdown: {
      evidenceFrequency: 82,
      futureWorkSupport: 95,
      methodologicalWeakness: 70,
      topicCoverage: 88
    }
  }
];