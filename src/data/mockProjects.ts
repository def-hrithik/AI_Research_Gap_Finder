import type { Project } from '../types/project';

export const mockProjects: Project[] = [
  {
    id: 'proj-1',
    name: 'Machine Learning for Healthcare Diagnosis',
    description: 'Analyzing recent advancements and limitations in ML models applied to early-stage disease detection.',
    paperCount: 9,
    gapCount: 6,
    topicCount: 8,
    lastUpdated: new Date().toISOString(),
    status: 'Analyzed'
  },
  {
    id: 'proj-2',
    name: 'NLP for Low-Resource Languages',
    description: 'Literature review on zero-shot translation capabilities.',
    paperCount: 4,
    gapCount: 2,
    topicCount: 3,
    lastUpdated: new Date(Date.now() - 86400000).toISOString(),
    status: 'Analyzed'
  }
];