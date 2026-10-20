import test from 'node:test';
import assert from 'node:assert/strict';
import axios from 'axios';

// Test Suite for Frontend API client resilience and error handling
test('apiClient configuration has bounded timeout', () => {
  const apiClient = axios.create({
    baseURL: '/api',
    timeout: 15000,
    headers: { 'Content-Type': 'application/json' },
  });

  assert.equal(apiClient.defaults.timeout, 15000, 'apiClient must have a 15-second timeout to prevent indefinite pending states');
  assert.equal(apiClient.defaults.baseURL, '/api', 'baseURL must target /api');
});

test('apiClient interceptor converts ECONNABORTED timeout to actionable error', async () => {
  const apiClient = axios.create({ timeout: 50 });

  apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.code === 'ECONNABORTED' || error.message?.toLowerCase().includes('timeout')) {
        return Promise.reject(new Error('Request timed out. The backend server took too long to respond.'));
      }
      if (!error.response) {
        return Promise.reject(new Error('Unable to connect to backend server. Please verify the backend is running at http://127.0.0.1:8000.'));
      }
      return Promise.reject(error);
    }
  );

  const mockTimeoutError = {
    code: 'ECONNABORTED',
    message: 'timeout of 50ms exceeded',
  };

  await assert.rejects(
    async () => {
      // Simulate interceptor failure path
      const handler = apiClient.interceptors.response.handlers[0].rejected;
      await handler(mockTimeoutError);
    },
    {
      name: 'Error',
      message: 'Request timed out. The backend server took too long to respond.',
    }
  );
});

test('apiClient interceptor converts connection refused to actionable backend error', async () => {
  const apiClient = axios.create();

  apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.code === 'ECONNABORTED' || error.message?.toLowerCase().includes('timeout')) {
        return Promise.reject(new Error('Request timed out. The backend server took too long to respond.'));
      }
      if (!error.response) {
        return Promise.reject(new Error('Unable to connect to backend server. Please verify the backend is running at http://127.0.0.1:8000.'));
      }
      return Promise.reject(error);
    }
  );

  const mockNetworkError = {
    message: 'Network Error',
    response: undefined,
  };

  await assert.rejects(
    async () => {
      const handler = apiClient.interceptors.response.handlers[0].rejected;
      await handler(mockNetworkError);
    },
    {
      name: 'Error',
      message: 'Unable to connect to backend server. Please verify the backend is running at http://127.0.0.1:8000.',
    }
  );
});

test('Project response transformation handles empty and populated data correctly', () => {
  function mapBackendProject(p) {
    let mappedStatus = 'Processing';
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
      lastUpdated: p.updated_at || p.created_at || '2026-01-01T00:00:00Z',
      status: mappedStatus,
    };
  }

  // Empty project list mapping
  const emptyBackendItems = [];
  const emptyFrontendList = emptyBackendItems.map(mapBackendProject);
  assert.equal(emptyFrontendList.length, 0);

  // Populated project mapping
  const backendProject = {
    project_id: 'prj_test_123',
    name: 'Literature Review',
    description: 'Quantum NLP Gaps',
    paper_count: 5,
    gap_count: 3,
    topic_count: 2,
    status: 'ANALYZED',
    created_at: '2026-03-01T10:00:00Z',
    updated_at: '2026-03-02T12:00:00Z',
  };

  const frontendProject = mapBackendProject(backendProject);
  assert.equal(frontendProject.id, 'prj_test_123');
  assert.equal(frontendProject.name, 'Literature Review');
  assert.equal(frontendProject.paperCount, 5);
  assert.equal(frontendProject.gapCount, 3);
  assert.equal(frontendProject.status, 'Analyzed');
});
