import React, { useState } from 'react';
import { Plus } from 'lucide-react';
import { useProjects } from '../hooks/useProjects';
import { ProjectCard } from '../components/projects/ProjectCard';
import { ProjectFilters } from '../components/projects/ProjectFilters';
import { CreateProjectModal } from '../components/projects/CreateProjectModal';
import { Button } from '../components/common/Button';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { EmptyState } from '../components/common/EmptyState';

export const ProjectsPage: React.FC = () => {
  const { data: projects, isLoading, isError, refetch } = useProjects();
  const [isCreateOpen, setIsCreateOpen] = useState(false);

  if (isLoading) return <LoadingState message="Loading projects..." className="mt-20" />;
  if (isError) return <ErrorState onRetry={refetch} className="mt-20" />;

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-primary mb-2">Projects</h1>
          <p className="text-secondary">Manage your literature reviews and gap analysis workspaces.</p>
        </div>
        <Button className="gap-2" onClick={() => setIsCreateOpen(true)}>
          <Plus size={18} /> New Project
        </Button>
      </div>

      <ProjectFilters />

      {!projects || projects.length === 0 ? (
        <EmptyState 
          title="No projects found" 
          description="Create your first project to start analyzing literature and discovering gaps."
          action={<Button onClick={() => setIsCreateOpen(true)}>Create Project</Button>}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map(project => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>
      )}

      <CreateProjectModal 
        isOpen={isCreateOpen} 
        onClose={() => setIsCreateOpen(false)} 
      />
    </div>
  );
};