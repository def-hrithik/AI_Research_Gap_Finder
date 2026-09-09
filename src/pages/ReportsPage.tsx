import React, { useState } from 'react';
import { FileDown, CheckSquare, Square, Loader2 } from 'lucide-react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { useToast } from '../context/ToastContext';

export const ReportsPage: React.FC = () => {
  const { addToast } = useToast();
  const [isGenerating, setIsGenerating] = useState(false);
  const [sections, setSections] = useState({
    landscape: true, topics: true, methods: true, 
    datasets: true, limitations: true, futureWork: true,
    contradictions: true, gaps: true
  });

  const toggleSection = (key: keyof typeof sections) => {
    setSections(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const handleGenerate = () => {
    setIsGenerating(true);
    setTimeout(() => {
      setIsGenerating(false);
      addToast('Report generated successfully! Download started.', 'success');
    }, 2500);
  };

  return (
    <div className="max-w-4xl mx-auto animate-in fade-in duration-300">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-primary mb-2">Export Research Report</h2>
        <p className="text-secondary">Generate a comprehensive HTML or text summary of your project workspace findings.</p>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        <Card className="p-6 flex flex-col h-full">
          <h3 className="font-bold text-primary mb-6">Include Sections</h3>
          <div className="space-y-1 flex-1">
            {Object.entries(sections).map(([key, isSelected]) => (
              <button
                key={key}
                onClick={() => toggleSection(key as keyof typeof sections)}
                className="w-full flex items-center justify-between p-3 rounded-xl hover:bg-surface-raised transition-colors group"
              >
                <span className="text-sm font-medium text-primary capitalize">
                  {key.replace(/([A-Z])/g, ' $1').trim()}
                </span>
                <div className="text-accent opacity-80 group-hover:opacity-100">
                  {isSelected ? <CheckSquare size={18} /> : <Square size={18} className="text-secondary" />}
                </div>
              </button>
            ))}
          </div>
        </Card>

        <Card raised className="p-6 bg-surface-raised flex flex-col justify-center items-center text-center">
          <div className="w-16 h-16 bg-accent/10 rounded-2xl flex items-center justify-center text-accent mb-6 shadow-sm">
            <FileDown size={32} />
          </div>
          <h3 className="text-xl font-bold text-primary mb-2">Generate Output</h3>
          <p className="text-secondary text-sm mb-8 leading-relaxed px-4">
            The report will aggregate evidence across all selected sections, complete with traceable page citations.
          </p>
          
          <div className="flex flex-col w-full gap-3 px-4">
            <Button onClick={handleGenerate} disabled={isGenerating} size="lg" className="shadow-md">
              {isGenerating ? <><Loader2 size={18} className="animate-spin mr-2"/> Compiling Report...</> : 'Generate HTML Report'}
            </Button>
            <Button variant="secondary" onClick={handleGenerate} disabled={isGenerating}>
              Download Raw Text
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
};