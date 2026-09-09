export interface Contradiction {
  id: string;
  projectId: string;
  topic: string;
  paperAId: string;
  paperAClaim: string;
  paperBId: string;
  paperBClaim: string;
  experimentalContext: string;
  dataset: string;
  method: string;
  confidenceScore: number;
}