import React from 'react';
import { Sparkles } from 'lucide-react';
import { Card } from '../common/Card';

export const AiAnswerBlock: React.FC<{ answer: string }> = ({ answer }) => (
  <Card raised className="p-8 border-accent/20 bg-gradient-to-br from-surface to-accent/5">
    <div className="flex items-center gap-2 mb-4 text-accent font-bold">
      <Sparkles size={20} /> AI Synthesized Answer
    </div>
    <p className="text-lg leading-relaxed text-primary">{answer}</p>
  </Card>
);