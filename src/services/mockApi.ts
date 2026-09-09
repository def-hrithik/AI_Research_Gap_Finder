import type { Project } from '../types/project';
import type { Paper } from '../types/paper';
import type { ResearchGap } from '../types/gap';
import type { Contradiction } from '../types/contradiction';
import { mockProjects } from '../data/mockProjects';
import { mockPapers } from '../data/mockPapers';
import { mockGaps } from '../data/mockGaps';
import { mockContradictions } from '../data/mockContradictions';

const delay = (ms: number) => new Promise(res => setTimeout(res, ms));

export const mockApi = {
  getProjects: async (): Promise<Project[]> => {
    await delay(600);
    return mockProjects;
  },
  getProject: async (id: string): Promise<Project | undefined> => {
    await delay(400);
    return mockProjects.find(p => p.id === id);
  },
  getPapers: async (projectId: string): Promise<Paper[]> => {
    await delay(800);
    return mockPapers.filter(p => p.projectId === projectId);
  },
  getPaper: async (paperId: string): Promise<Paper | undefined> => {
    await delay(400);
    return mockPapers.find(p => p.id === paperId);
  },
  getGaps: async (projectId: string): Promise<ResearchGap[]> => {
    await delay(1000);
    return mockGaps.filter(g => g.projectId === projectId);
  },
  getGap: async (gapId: string): Promise<ResearchGap | undefined> => {
    await delay(400);
    return mockGaps.find(g => g.id === gapId);
  },
  getContradictions: async (projectId: string): Promise<Contradiction[]> => {
    await delay(800);
    return mockContradictions.filter(c => c.projectId === projectId);
  }
};
