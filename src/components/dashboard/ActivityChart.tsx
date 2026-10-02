import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card } from '../common/Card';
import type { Project } from '../../types/project';

interface ActivityChartProps {
  projects?: Project[];
}

export const ActivityChart: React.FC<ActivityChartProps> = ({ projects = [] }) => {
  const chartData = projects.map(p => ({
    name: p.name.length > 15 ? p.name.slice(0, 15) + '...' : p.name,
    papers: p.paperCount,
    gaps: p.gapCount,
  }));

  return (
    <Card className="p-6 flex flex-col h-full">
      <div className="mb-6">
        <h3 className="text-lg font-bold text-primary">Workspace Metrics</h3>
        <p className="text-sm text-secondary">Papers analyzed and candidate gaps found across active projects</p>
      </div>
      <div className="flex-1 min-h-[250px] flex items-center justify-center">
        {chartData.length === 0 ? (
          <p className="text-sm text-secondary">No active projects to display metrics for.</p>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgb(var(--border))" />
              <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: 'rgb(var(--text-secondary))', fontSize: 12 }} dy={10} />
              <YAxis axisLine={false} tickLine={false} tick={{ fill: 'rgb(var(--text-secondary))', fontSize: 12 }} />
              <Tooltip 
                contentStyle={{ backgroundColor: 'rgb(var(--surface))', borderRadius: '12px', border: '1px solid rgb(var(--border))', boxShadow: 'var(--tw-shadow-md)' }}
                itemStyle={{ color: 'rgb(var(--text-primary))' }}
              />
              <Bar dataKey="papers" name="Papers" fill="rgb(var(--accent))" radius={[4, 4, 0, 0]} />
              <Bar dataKey="gaps" name="Gaps" fill="rgb(var(--alert))" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
    </Card>
  );
};