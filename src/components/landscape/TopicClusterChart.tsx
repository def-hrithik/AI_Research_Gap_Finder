import React from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { Card } from '../common/Card';

const data = [
  { x: 10, y: 30, z: 200, name: 'Transformers', color: 'rgb(var(--accent))' },
  { x: 30, y: 200, z: 100, name: 'CNNs', color: 'rgb(var(--success))' },
  { x: 45, y: 100, z: 400, name: 'EHR Data', color: 'rgb(var(--alert))' },
  { x: 70, y: 150, z: 250, name: 'Medical Imaging', color: '#3B82F6' },
  { x: 80, y: 50, z: 150, name: 'Demographic Bias', color: '#8B5CF6' },
];

export const TopicClusterChart: React.FC = () => (
  <Card className="p-6 h-[400px] flex flex-col">
    <h3 className="font-bold text-primary mb-1">Topic Clusters</h3>
    <p className="text-sm text-secondary mb-4">Proximity implies co-occurrence in literature</p>
    <div className="flex-1">
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: -20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgb(var(--border))" />
          <XAxis type="number" dataKey="x" name="st" hide />
          <YAxis type="number" dataKey="y" name="weight" hide />
          <Tooltip 
            cursor={{ strokeDasharray: '3 3' }}
            contentStyle={{ backgroundColor: 'rgb(var(--surface))', borderRadius: '12px', border: '1px solid rgb(var(--border))' }}
            formatter={(_value: any, _name: any, props: any) => [props.payload.name, 'Topic']}
          />
          <Scatter name="Topics" data={data} fill="#8884d8">
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  </Card>
);