import { mockApi } from './mockApi';
import { realApi } from './realApi';

// Centralized API layer toggled via env var
const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false';

export const api = USE_MOCK ? mockApi : realApi;