import axios from 'axios';
import type { Project } from '../types/project';
import type { Paper, PaperAnalysis } from '../types/paper';
import type { ResearchGap } from '../types/gap';
import type { Contradiction } from '../types/contradiction';

const apiClient = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
});

// Helper to map backend ProjectResponse to frontend Project
function mapBackendProject(p: any): Project {
  let mappedStatus: Project['status'] = 'Processing';
  const s = (p.status || '').toUpperCase();
  if (s === 'ANALYZED') mappedStatus = 'Analyzed';
  else if (s === 'ERROR' || s === 'FAILED') mappedStatus = 'Error';
  else if (s === 'EMPTY') mappedStatus = 'Processing';
  else mappedStatus = 'Processing';

  return {
    id: p.project_id,
    name: p.name,
    description: p.description || '',
    paperCount: p.paper_count || 0,
    gapCount: p.gap_count || 0,
    topicCount: p.topic_count || 0,
    lastUpdated: p.updated_at || p.created_at || new Date().toISOString(),
    status: mappedStatus,
  };
}

// Helper to map backend PaperResponse to frontend Paper
function mapBackendPaper(p: any, analysis?: any): Paper {
  let analysisStatus: Paper['analysisStatus'] = 'pending';
  const s = (p.status || '').toUpperCase();
  const aStatus = (p.analysis_status || '').toUpperCase();

  if (aStatus === 'COMPLETED' || s === 'ANALYZED' || !!analysis) {
    analysisStatus = 'completed';
  } else if (['PARSING', 'CHUNKING', 'EMBEDDING', 'ANALYZING'].includes(s)) {
    analysisStatus = 'processing';
  }

  let mappedAnalysis: PaperAnalysis | undefined = undefined;
  if (analysis) {
    mappedAnalysis = {
      problem: analysis.problem || '',
      methodology: analysis.methodology || '',
      models: analysis.models || [],
      dataset: analysis.dataset || [],
      findings: analysis.findings || '',
      limitations: analysis.limitations || [],
      futureWork: analysis.futureWork || [],
    };
  }

  return {
    id: p.paper_id,
    projectId: p.project_id,
    title: p.title || 'Untitled Document',
    authors: Array.isArray(p.authors) ? p.authors : [],
    year: p.year || new Date().getFullYear(),
    venue: p.venue || 'Preprint / Publication',
    doi: p.doi || '',
    abstract: p.abstract || '',
    analysisStatus,
    analysis: mappedAnalysis,
  };
}

export const realApi = {
  // Projects
  getProjects: async (): Promise<Project[]> => {
    const { data } = await apiClient.get('/projects');
    const items = data.items || [];
    return items.map(mapBackendProject);
  },

  getProject: async (id: string): Promise<Project> => {
    const { data } = await apiClient.get(`/projects/${id}`);
    return mapBackendProject(data);
  },

  createProject: async (payload: { name: string; description?: string }): Promise<Project> => {
    const { data } = await apiClient.post('/projects', payload);
    return mapBackendProject(data);
  },

  deleteProject: async (id: string): Promise<void> => {
    await apiClient.delete(`/projects/${id}`);
  },

  // Papers
  getPapers: async (projectId: string): Promise<Paper[]> => {
    const { data } = await apiClient.get(`/projects/${projectId}/papers`);
    const items = data.items || [];
    return items.map((p: any) => mapBackendPaper(p));
  },

  getPaper: async (paperId: string): Promise<Paper> => {
    const { data } = await apiClient.get(`/papers/${paperId}`);
    return mapBackendPaper(data.paper, data.analysis);
  },

  uploadPaper: async (projectId: string, file: File): Promise<{ paper: Paper; job_id: string; poll_url: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    const { data } = await apiClient.post(`/projects/${projectId}/papers/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return {
      paper: mapBackendPaper(data.paper),
      job_id: data.job_id,
      poll_url: data.poll_url,
    };
  },

  deletePaper: async (paperId: string): Promise<void> => {
    await apiClient.delete(`/papers/${paperId}`);
  },

  // Jobs
  getJob: async (jobId: string): Promise<any> => {
    const { data } = await apiClient.get(`/jobs/${jobId}`);
    return data;
  },

  // Search & RAG
  search: async (projectId: string, query: string): Promise<{ answer: string; sources: any[]; insufficientEvidence: boolean }> => {
    const { data } = await apiClient.post('/search', {
      project_id: projectId,
      query,
      generate_answer: true,
      top_k: 10,
    });
    return {
      answer: data.answer,
      sources: (data.sources || []).map((s: any) => ({
        id: String(s.source_id || s.chunk_id),
        paperTitle: s.paper_title,
        section: s.section_heading || s.section || 'General',
        page: s.page || 1,
        text: s.text,
        relevance: Math.round((s.score || 0.8) * 100),
      })),
      insufficientEvidence: !!data.insufficient_evidence,
    };
  },

  // Research Gaps
  getGaps: async (projectId: string): Promise<ResearchGap[]> => {
    const { data } = await apiClient.get(`/projects/${projectId}/gaps`);
    return Array.isArray(data) ? data : [];
  },

  getGap: async (gapId: string): Promise<ResearchGap> => {
    const { data } = await apiClient.get(`/gaps/${gapId}`);
    return data;
  },

  // Contradictions
  getContradictions: async (projectId: string): Promise<Contradiction[]> => {
    const { data } = await apiClient.get(`/projects/${projectId}/contradictions`);
    return Array.isArray(data) ? data : [];
  },

  // Landscape
  getLandscape: async (projectId: string): Promise<any> => {
    const { data } = await apiClient.get(`/projects/${projectId}/landscape`);
    return data;
  },

  // Reports
  getReports: async (projectId: string, format?: string): Promise<any> => {
    const { data } = await apiClient.get(`/projects/${projectId}/reports${format ? `?format=${format}` : ''}`);
    return data;
  },

  generateReport: async (projectId: string): Promise<any> => {
    const { data } = await apiClient.post(`/projects/${projectId}/reports/generate`);
    return data;
  },

  startAnalysis: async (projectId: string): Promise<any> => {
    const { data } = await apiClient.post(`/projects/${projectId}/analyze`);
    return data;
  },
};
