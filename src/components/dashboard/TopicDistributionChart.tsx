import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { Card } from '../common/Card';

const data = [
  { name: 'Machine Learning', value: 35 },
  { name: 'Healthcare', value: 25 },
  { name: 'NLP', value: 20 },
  { name: 'Climate', value: 20 },
];

const COLORS = ['rgb(var(--accent))', 'rgb(var(--success))', 'rgb(var(--alert))', '#3B82F6'];

export const TopicDistributionChart: React.FC = () => {
  return (
    <Card className="p-6 flex flex-col h-full">
      <div className="mb-6">
        <h3 className="text-lg font-bold text-primary">Topic Distribution</h3>
        <p className="text-sm text-secondary">Breakdown of analyzed literature</p>
      </div>
      <div className="flex-1 min-h-[250px] relative">
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
      </div>
    </Card>
  );
};