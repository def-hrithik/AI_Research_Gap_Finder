export type GapType = 'Underexplored Area' | 'Repeated Limitation' | 'Methodological Gap' | 'Dataset Gap' | 'Contradiction-Driven Gap' | 'Future-Work Gap';

export interface Evidence {
  paperId: string;
  section: string;
  page: number;
  text: string;
  relationshipToGap: string;
  relevanceScore: number;
}

export interface ConfidenceBreakdown {
  evidenceFrequency: number;
  futureWorkSupport: number;
  methodologicalWeakness: number;
  topicCoverage: number;
}

export interface ResearchGap {
  id: string;
  projectId: string;
  type: GapType;
  confidence: number;
  topic: string;
  description: string;
  evidence: Evidence[];
  supportingPaperIds: string[];
  suggestedQuestion: string;
  suggestedMethodology: string;
  confidenceBreakdown: ConfidenceBreakdown;
}