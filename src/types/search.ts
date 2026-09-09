export interface SearchSource {
  paperId: string;
  section: string;
  page: number;
  snippet: string;
  relevanceScore: number;
}

export interface SearchResult {
  aiAnswer: string;
  sources: SearchSource[];
  suggestedQuestions: string[];
}