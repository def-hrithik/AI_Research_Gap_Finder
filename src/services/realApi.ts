import axios from 'axios';
import type { Project } from '../types/project';
import type { Paper } from '../types/paper';
import type { ResearchGap } from '../types/gap';
import type { Contradiction } from '../types/contradiction';

const apiClient = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' }
});

export const realApi = {
  getProjects: async (): Promise<Project[]> => {
    const { data } = await apiClient.get('/projects');
    return data;
  },
  getProject: async (id: string): Promise<Project> => {
    const { data } = await apiClient.get(`/projects/${id}`);
    return data;
  },
  getPapers: async (projectId: string): Promise<Paper[]> => {
    const { data } = await apiClient.get(`/projects/${projectId}/papers`);
    return data;
  },
  getPaper: async (paperId: string): Promise<Paper> => {
    const { data } = await apiClient.get(`/papers/${paperId}`);
    return data;
  },
  getGaps: async (projectId: string): Promise<ResearchGap[]> => {
    const { data } = await apiClient.get(`/projects/${projectId}/gaps`);
    return data;
  },
  getGap: async (gapId: string): Promise<ResearchGap> => {
    const { data } = await apiClient.get(`/gaps/${gapId}`);
    return data;
  },
  getContradictions: async (projectId: string): Promise<Contradiction[]> => {
    const { data } = await apiClient.get(`/projects/${projectId}/contradictions`);
    return data;
  }
};
