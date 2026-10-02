import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { FileDown, CheckSquare, Square, Loader2, Download } from 'lucide-react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { useToast } from '../context/ToastContext';
import { api } from '../services/api';

export const ReportsPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const { addToast } = useToast();
  const [isGenerating, setIsGenerating] = useState(false);
  const [reportMarkdown, setReportMarkdown] = useState<string | null>(null);

  const [sections, setSections] = useState({
    landscape: true, topics: true, methods: true, 
    datasets: true, limitations: true, futureWork: true,
    contradictions: true, gaps: true
  });

  const toggleSection = (key: keyof typeof sections) => {
    setSections(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const downloadFile = (content: string, filename: string) => {
    const blob = new Blob([content], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleGenerate = async () => {
    if (!projectId) return;
    setIsGenerating(true);
    try {
      const res = await api.generateReport(projectId);
      setReportMarkdown(res.markdown);
      addToast('Report generated successfully! Download started.', 'success');
      if (res.markdown) {
        downloadFile(res.markdown, `research-report-${projectId}.md`);
      }
    } catch (err: any) {
      console.error('Failed to generate report:', err);
      addToast(err?.response?.data?.error?.message || 'Failed to generate report', 'error');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownloadExisting = async () => {
    if (!projectId) return;
    try {
      const res = await api.getReports(projectId);
      if (res.markdown) {
        downloadFile(res.markdown, `research-report-${projectId}.md`);
        addToast('Report downloaded successfully.', 'success');
      } else {
        await handleGenerate();
      }
    } catch (err) {
      await handleGenerate();
    }
  };

  return (
    <div className="max-w-4xl mx-auto animate-in fade-in duration-300">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-primary mb-2">Export Research Report</h2>
        <p className="text-secondary">Generate a comprehensive, evidence-grounded markdown summary of your project literature findings.</p>
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
            The report aggregates evidence across all selected sections, complete with traceable paper citations and candidate research gaps.
          </p>
          
          <div className="flex flex-col w-full gap-3 px-4">
            <Button onClick={handleGenerate} disabled={isGenerating} size="lg" className="shadow-md">
              {isGenerating ? <><Loader2 size={18} className="animate-spin mr-2"/> Compiling Report...</> : 'Generate & Download Report'}
            </Button>
            <Button variant="secondary" onClick={handleDownloadExisting} disabled={isGenerating} className="gap-2">
              <Download size={16} /> Download Raw Markdown
            </Button>
          </div>
        </Card>
      </div>

      {reportMarkdown && (
        <Card className="mt-8 p-6">
          <h3 className="font-bold text-primary mb-4">Report Preview</h3>
          <pre className="p-4 bg-background rounded-xl border border-border text-xs text-secondary overflow-x-auto whitespace-pre-wrap font-mono max-h-96">
            {reportMarkdown}
          </pre>
        </Card>
      )}
    </div>
  );
};