import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card } from '../common/Card';

const data = [
  { name: 'Mon', papers: 4, gaps: 1 },
  { name: 'Tue', papers: 7, gaps: 3 },
  { name: 'Wed', papers: 5, gaps: 2 },
  { name: 'Thu', papers: 12, gaps: 5 },
  { name: 'Fri', papers: 8, gaps: 4 },
  { name: 'Sat', papers: 2, gaps: 0 },
  { name: 'Sun', papers: 3, gaps: 1 },
];

export const ActivityChart: React.FC = () => {
  return (
    <Card className="p-6 flex flex-col h-full">
      <div className="mb-6">
        <h3 className="text-lg font-bold text-primary">Activity Overview</h3>
        <p className="text-sm text-secondary">Papers processed and gaps found over the last 7 days</p>
      </div>
      <div className="flex-1 min-h-[250px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="colorPapers" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="rgb(var(--accent))" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="rgb(var(--accent))" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgb(var(--border))" />
            <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: 'rgb(var(--text-secondary))', fontSize: 12 }} dy={10} />
            <YAxis axisLine={false} tickLine={false} tick={{ fill: 'rgb(var(--text-secondary))', fontSize: 12 }} />
            <Tooltip 
              contentStyle={{ backgroundColor: 'rgb(var(--surface))', borderRadius: '12px', border: '1px solid rgb(var(--border))', boxShadow: 'var(--tw-shadow-md)' }}
              itemStyle={{ color: 'rgb(var(--text-primary))' }}
            />
            <Area type="monotone" dataKey="papers" stroke="rgb(var(--accent))" strokeWidth={3} fillOpacity={1} fill="url(#colorPapers)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
};