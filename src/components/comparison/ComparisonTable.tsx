import React from 'react';
import type { Paper, PaperAnalysis } from '../../types/paper';

interface ComparisonTableProps {
  papers: Paper[];
}

interface Category {
  key: keyof PaperAnalysis;
  label: string;
  isArray?: boolean;
}

export const ComparisonTable: React.FC<ComparisonTableProps> = ({ papers }) => {
  if (!papers || papers.length === 0) return null;

  const categories: Category[] = [
    { key: 'problem', label: 'Core Problem' },
    { key: 'methodology', label: 'Methodology' },
    { key: 'models', label: 'Models Used', isArray: true },
    { key: 'dataset', label: 'Datasets', isArray: true },
    { key: 'findings', label: 'Key Findings' },
    { key: 'limitations', label: 'Limitations', isArray: true },
    { key: 'futureWork', label: 'Future Work', isArray: true }
  ];

  return (
    <div className="overflow-x-auto rounded-2xl border border-border bg-surface shadow-sm">
      <table className="w-full text-left min-w-[800px]">
        <thead>
          <tr className="bg-surface-raised border-b border-border">
            <th className="p-4 w-48 shrink-0 font-bold text-secondary uppercase text-xs tracking-wider border-r border-border sticky left-0 bg-surface-raised z-10">
              Category
            </th>
            {papers.map((paper) => (
              <th key={paper.id} className="p-4 min-w-[300px] align-top">
                <div className="font-bold text-primary text-sm mb-1">{paper.title}</div>
                <div className="text-xs text-secondary font-normal">{paper.authors[0]} et al., {paper.year}</div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {categories.map((category) => (
            <tr key={category.key} className="hover:bg-surface-raised/50 transition-colors">
              <td className="p-4 font-semibold text-sm text-primary border-r border-border sticky left-0 bg-surface z-10 group-hover:bg-surface-raised/50">
                {category.label}
              </td>
              {papers.map((paper) => {
                const value = paper.analysis?.[category.key];
                
                return (
                  <td key={`${paper.id}-${category.key}`} className="p-4 text-sm text-secondary leading-relaxed align-top">
                    {category.isArray && Array.isArray(value) ? (
                      <ul className="list-disc pl-4 space-y-1">
                        {value.map((item: string, idx: number) => (
                          <li key={idx}>{item}</li>
                        ))}
                      </ul>
                    ) : (
                      <p>{value || <span className="italic opacity-50">Not specified</span>}</p>
                    )}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};