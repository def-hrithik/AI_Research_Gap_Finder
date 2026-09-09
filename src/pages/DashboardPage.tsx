import React from 'react';
import { useProjects } from '../hooks/useProjects';
import { StatCards } from '../components/dashboard/StatCards';
import { ActivityChart } from '../components/dashboard/ActivityChart';
import { TopicDistributionChart } from '../components/dashboard/TopicDistributionChart';
import { RecentProjects } from '../components/dashboard/RecentProjects';
import { ActivityFeed } from '../components/dashboard/ActivityFeed';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';

export const DashboardPage: React.FC = () => {
  const { data: projects, isLoading, isError, refetch } = useProjects();

  if (isLoading) return <LoadingState message="Loading your workspace..." className="mt-20" />;
  if (isError) return <ErrorState onRetry={refetch} className="mt-20" />;

  const projectsCount = projects?.length || 0;
  const papersCount = projects?.reduce((acc, p) => acc + p.paperCount, 0) || 0;
  const topicsCount = projects?.reduce((acc, p) => acc + p.topicCount, 0) || 0;
  const gapsCount = projects?.reduce((acc, p) => acc + p.gapCount, 0) || 0;

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold text-primary mb-2">Welcome back</h1>
        <p className="text-secondary text-lg">Here is an overview of your research intelligence workspace.</p>
      </div>

      <StatCards 
        projectsCount={projectsCount} 
        papersCount={papersCount} 
        topicsCount={topicsCount} 
        gapsCount={gapsCount} 
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ActivityChart />
        </div>
        <div>
          <TopicDistributionChart />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <RecentProjects projects={projects || []} />
        </div>
        <div>
          <ActivityFeed />
        </div>
      </div>
    </div>
  );
};