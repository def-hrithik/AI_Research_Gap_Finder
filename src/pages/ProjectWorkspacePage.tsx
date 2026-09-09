import React from 'react';
import { useParams, NavLink, Outlet } from 'react-router-dom';
import { useProject } from '../hooks/useProjects';
import { FileText, Search, Map, Layers, Target, FileBarChart, UploadCloud, Beaker } from 'lucide-react';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { cn } from '../utils/formatters';

export const ProjectWorkspacePage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const { data: project, isLoading, isError, refetch } = useProject(projectId);

  if (isLoading) return <LoadingState message="Loading project workspace..." className="mt-20" />;
  if (isError || !project) return <ErrorState onRetry={refetch} className="mt-20" />;

  const tabs = [
    { name: 'Papers', path: `/projects/${projectId}/papers`, icon: FileText },
    { name: 'Semantic Search', path: `/projects/${projectId}/search`, icon: Search },
    { name: 'Landscape', path: `/projects/${projectId}/landscape`, icon: Map },
    { name: 'Compare', path: `/projects/${projectId}/compare`, icon: Layers },
    { name: 'Contradictions', path: `/projects/${projectId}/contradictions`, icon: Beaker },
    { name: 'Research Gaps', path: `/projects/${projectId}/gaps`, icon: Target },
    { name: 'Reports', path: `/projects/${projectId}/reports`, icon: FileBarChart },
  ];

  return (
    <div className="max-w-7xl mx-auto flex flex-col h-[calc(100vh-8rem)]">
      {/* Project Header */}
      <div className="shrink-0 mb-6 space-y-4">
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold text-primary">{project.name}</h1>
              <Badge variant={project.status === 'Analyzed' ? 'success' : 'accent'}>
                {project.status}
              </Badge>
            </div>
            <p className="text-secondary max-w-3xl leading-relaxed">{project.description}</p>
          </div>
          <div className="flex items-center gap-3 shrink-0">
            <NavLink to={`/projects/${projectId}/upload`}>
              <Button className="gap-2 shadow-sm rounded-xl">
                <UploadCloud size={18} /> Add Papers
              </Button>
            </NavLink>
          </div>
        </div>

        {/* Stats Row */}
        <div className="flex flex-wrap items-center gap-6 text-sm py-2 border-b border-border">
          <div className="flex items-center gap-2 text-secondary">
            <FileText size={16} /> <strong className="text-primary">{project.paperCount}</strong> Papers
          </div>
          <div className="flex items-center gap-2 text-secondary">
            <Map size={16} /> <strong className="text-primary">{project.topicCount}</strong> Topics
          </div>
          <div className="flex items-center gap-2 text-secondary">
            <Target size={16} /> <strong className="text-primary">{project.gapCount}</strong> Gaps
          </div>
        </div>

        {/* Workspace Tabs */}
        <div className="flex overflow-x-auto hide-scrollbar gap-2 pb-2">
          {tabs.map(tab => (
            <NavLink
              key={tab.path}
              to={tab.path}
              className={({ isActive }) => cn(
                "flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold whitespace-nowrap transition-all duration-200",
                isActive 
                  ? "bg-primary text-background shadow-md" 
                  : "bg-surface text-secondary border border-border hover:border-accent/50 hover:text-primary"
              )}
            >
              <tab.icon size={16} /> {tab.name}
            </NavLink>
          ))}
        </div>
      </div>

      {/* Nested Content Area */}
      <div className="flex-1 overflow-y-auto min-h-0 pb-12">
        <Outlet />
      </div>
    </div>
  );
};