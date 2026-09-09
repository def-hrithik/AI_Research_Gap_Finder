import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card } from '../common/Card';

const data = [
  { name: 'ResNet', count: 12 },
  { name: 'ClinicalBERT', count: 8 },
  { name: 'DenseNet', count: 6 },
  { name: 'LSTM', count: 4 },
  { name: 'ViT', count: 3 },
];

export const MethodUsageChart: React.FC = () => (
  <Card className="p-6 h-[300px] flex flex-col">
    <h3 className="font-bold text-primary mb-1">Methodology Popularity</h3>
    <p className="text-sm text-secondary mb-4">Most frequently utilized models/methods</p>
    <div className="flex-1">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{ top: 0, right: 0, left: 10, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="rgb(var(--border))" />
          <XAxis type="number" tick={{ fill: 'rgb(var(--text-secondary))', fontSize: 12 }} axisLine={false} tickLine={false} />
          <YAxis type="category" dataKey="name" tick={{ fill: 'rgb(var(--text-primary))', fontSize: 12 }} axisLine={false} tickLine={false} />
          <Tooltip 
            cursor={{ fill: 'rgb(var(--surface-raised))' }}
            contentStyle={{ backgroundColor: 'rgb(var(--surface))', borderRadius: '12px', border: '1px solid rgb(var(--border))' }}
          />
          <Bar dataKey="count" fill="rgb(var(--accent))" radius={[0, 4, 4, 0]} barSize={20} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  </Card>
);