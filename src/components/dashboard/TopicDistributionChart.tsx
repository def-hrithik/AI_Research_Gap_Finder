import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { Card } from '../common/Card';
import type { Project } from '../../types/project';

interface TopicDistributionChartProps {
  projects?: Project[];
}

const COLORS = ['rgb(var(--accent))', 'rgb(var(--success))', 'rgb(var(--alert))', '#3B82F6', '#8B5CF6'];

export const TopicDistributionChart: React.FC<TopicDistributionChartProps> = ({ projects = [] }) => {
  // Aggregate real status or projects distribution
  const data = projects.map(p => ({
    name: p.name.length > 18 ? p.name.slice(0, 18) + '...' : p.name,
    value: Math.max(1, p.paperCount),
  }));

  return (
    <Card className="p-6 flex flex-col h-full">
      <div className="mb-6">
        <h3 className="text-lg font-bold text-primary">Literature Share</h3>
        <p className="text-sm text-secondary">Paper volume breakdown by project</p>
      </div>
      <div className="flex-1 min-h-[250px] relative flex items-center justify-center">
        {data.length === 0 ? (
          <p className="text-sm text-secondary">No literature indexed yet.</p>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
                stroke="none"
              >
                {data.map((_entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ backgroundColor: 'rgb(var(--surface))', borderRadius: '12px', border: '1px solid rgb(var(--border))' }}
                itemStyle={{ color: 'rgb(var(--text-primary))' }}
              />
              <Legend verticalAlign="bottom" height={36} iconType="circle" wrapperStyle={{ fontSize: '12px', color: 'rgb(var(--text-secondary))' }}/>
            </PieChart>
          </ResponsiveContainer>
        )}
      </div>
    </Card>
  );
};