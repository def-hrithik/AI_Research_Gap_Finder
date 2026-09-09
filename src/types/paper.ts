export interface PaperAnalysis {
  problem: string;
  methodology: string;
  models: string[];
  dataset: string[];
  findings: string;
  limitations: string[];
  futureWork: string[];
}

export interface Paper {
  id: string;
  projectId: string;
  title: string;
  authors: string[];
  year: number;
  venue: string;
  doi: string;
  abstract: string;
  analysisStatus: 'pending' | 'processing' | 'completed';
  analysis?: PaperAnalysis;
}