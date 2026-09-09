import type { Paper } from '../types/paper';

export const mockPapers: Paper[] = [
  {
    id: 'paper-001',
    projectId: 'proj-001',
    title: 'Transformer Models for Early Diabetes Detection',
    authors: ['Smith, J.', 'Doe, A.'],
    year: 2024,
    venue: 'IEEE Medical Imaging',
    doi: '10.1109/TMI.2024.1234567',
    abstract: 'This paper reviews the application of transformer architectures to early diabetes detection...',
    analysisStatus: 'completed',
    analysis: {
      problem: 'Late detection of type 2 diabetes due to reliance on blood-test lagging indicators.',
      methodology: 'Retrospective cohort study using Vision Transformers on retinal scans.',
      models: ['ViT-Base', 'ResNet-50'],
      dataset: ['MIMIC-IV', 'EyePACS'],
      findings: 'ViT outperformed CNNs by 8% in early microaneurysm detection.',
      limitations: ['Small demographic variance in training set', 'High computational overhead'],
      futureWork: ['Validate on longitudinal data', 'Reduce model size for edge deployment']
    }
  },
  {
    id: 'paper-002',
    projectId: 'proj-001',
    title: 'Evaluating CNN robustness on non-Western clinical datasets',
    authors: ['Chen, L.', 'Kumar, R.'],
    year: 2025,
    venue: 'Nature Health AI',
    doi: '10.1038/s41746-025-1234-x',
    abstract: 'We evaluate traditional CNN approaches across diverse geographic datasets...',
    analysisStatus: 'completed',
    analysis: {
      problem: 'Model performance degradation on demographics not represented in training.',
      methodology: 'Cross-validation of pre-trained models on 4 distinct geographic clinical datasets.',
      models: ['EfficientNet', 'ResNet-50'],
      dataset: ['AsianHealth DB', 'AfriMed DB'],
      findings: 'Performance dropped by 14-22% across non-Western cohorts.',
      limitations: ['Did not test transformer architectures'],
      futureWork: ['Evaluate newer attention-based models on these datasets']
    }
  }
];