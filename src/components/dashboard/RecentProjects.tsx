import React from 'react';
import { Link } from 'react-router-dom';
import type { Project } from '../../types/project';
import { ProjectCard } from '../projects/ProjectCard';
import { Button } from '../common/Button';

interface RecentProjectsProps {
  projects: Project[];
}

export const RecentProjects: React.FC<RecentProjectsProps> = ({ projects }) => {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold text-primary">Recent Projects</h3>
        <Link to="/projects">
          <Button variant="ghost" size="sm">View All</Button>
        </Link>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {projects.slice(0, 2).map(project => (
          <ProjectCard key={project.id} project={project} />
        ))}
      </div>
    </div>
  );
};