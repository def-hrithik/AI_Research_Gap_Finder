import React from 'react';
import { Link } from 'react-router-dom';
import { FileText, Target, Map, ArrowRight } from 'lucide-react';
import type { Project } from '../../types/project';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
import { Button } from '../common/Button';
import { formatDate } from '../../utils/formatters';

interface ProjectCardProps {
  project: Project;
}

export const ProjectCard: React.FC<ProjectCardProps> = ({ project }) => {
  const getStatusColor = (status: Project['status']) => {
    switch(status) {
      case 'Analyzed': return 'success';
      case 'Processing': return 'accent';
      case 'Error': return 'alert';
      default: return 'default';
    }
  };

  return (
    <Card raised interactive className="flex flex-col h-full group">
      <div className="p-6 flex-1 flex flex-col">
        <div className="flex justify-between items-start mb-4">
          <Badge variant={getStatusColor(project.status)}>{project.status}</Badge>
          <span className="text-xs text-secondary">Updated {formatDate(project.lastUpdated)}</span>
        </div>
        
        <h3 className="text-xl font-bold text-primary mb-2 group-hover:text-accent transition-colors">
          {project.name}
        </h3>
        <p className="text-sm text-secondary line-clamp-2 mb-6 flex-1">
          {project.description}
        </p>

        <div className="flex items-center gap-6 pt-4 border-t border-border">
          <div className="flex flex-col">
            <span className="text-xl font-bold text-primary flex items-center gap-2">
              <FileText size={16} className="text-secondary" /> {project.paperCount}
            </span>
            <span className="text-xs font-medium text-secondary uppercase tracking-wider">Papers</span>
          </div>
          <div className="flex flex-col">
            <span className="text-xl font-bold text-primary flex items-center gap-2">
              <Map size={16} className="text-secondary" /> {project.topicCount}
            </span>
            <span className="text-xs font-medium text-secondary uppercase tracking-wider">Topics</span>
          </div>
          <div className="flex flex-col">
            <span className="text-xl font-bold text-primary flex items-center gap-2">
              <Target size={16} className="text-secondary" /> {project.gapCount}
            </span>
            <span className="text-xs font-medium text-secondary uppercase tracking-wider">Gaps</span>
          </div>
        </div>
      </div>
      <div className="p-4 bg-surface-raised border-t border-border mt-auto">
        <Link to={`/projects/${project.id}/papers`} className="block">
          <Button fullWidth variant="secondary" className="group-hover:bg-accent group-hover:text-white group-hover:border-accent transition-all gap-2">
            Open Workspace <ArrowRight size={16} />
          </Button>
        </Link>
      </div>
    </Card>
  );
};