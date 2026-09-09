export interface Project {
  id: string;
  name: string;
  description: string;
  paperCount: number;
  gapCount: number;
  topicCount: number;
  lastUpdated: string;
  status: 'Processing' | 'Analyzed' | 'Error';
}