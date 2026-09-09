
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from './context/ThemeContext';
import { ToastProvider } from './context/ToastContext';

// Layout & Core Pages
import { AppShell } from './components/layout/AppShell';
import { LandingPage } from './pages/LandingPage';
import { DashboardPage } from './pages/DashboardPage';
import { ProjectsPage } from './pages/ProjectsPage';
import { ProjectWorkspacePage } from './pages/ProjectWorkspacePage';
import { NotFoundPage } from './pages/NotFoundPage';

// Project Feature Pages
import { UploadPage } from './pages/UploadPage';
import { PapersPage } from './pages/PapersPage';
import { PaperDetailsPage } from './pages/PaperDetailsPage';
import { SearchPage } from './pages/SearchPage';
import { LandscapePage } from './pages/LandscapePage';
import { ComparePage } from './pages/ComparePage';
import { ContradictionsPage } from './pages/ContradictionsPage';
import { GapsPage } from './pages/GapsPage';
import { GapDetailsPage } from './pages/GapDetailsPage';
import { ReportsPage } from './pages/ReportsPage';

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 1000 * 60 * 5, retry: 1 } },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <ToastProvider>
          <BrowserRouter>
            <Routes>
              {/* Public Marketing Route */}
              <Route path="/" element={<LandingPage />} />

              {/* Authenticated App Routes wrapped in the Sidebar Shell */}
              <Route element={<AppShell />}>
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/projects" element={<ProjectsPage />} />
                
                {/* Global detail views independent of active project tab */}
                <Route path="/papers/:paperId" element={<PaperDetailsPage />} />
                <Route path="/gaps/:gapId" element={<GapDetailsPage />} />

                {/* Nested Project Workspace Routes */}
                <Route path="/projects/:projectId" element={<ProjectWorkspacePage />}>
                  <Route index element={<Navigate to="papers" replace />} />
                  <Route path="upload" element={<UploadPage />} />
                  <Route path="papers" element={<PapersPage />} />
                  <Route path="search" element={<SearchPage />} />
                  <Route path="landscape" element={<LandscapePage />} />
                  <Route path="compare" element={<ComparePage />} />
                  <Route path="contradictions" element={<ContradictionsPage />} />
                  <Route path="gaps" element={<GapsPage />} />
                  <Route path="reports" element={<ReportsPage />} />
                </Route>

                <Route path="*" element={<NotFoundPage />} />
              </Route>
            </Routes>
          </BrowserRouter>
        </ToastProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}