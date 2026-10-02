import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { UploadDropzone } from '../components/papers/UploadDropzone';
import { UploadFileRow } from '../components/papers/UploadFileRow';
import type { UploadFile } from '../components/papers/UploadFileRow';
import { Button } from '../components/common/Button';
import { useToast } from '../context/ToastContext';
import { api } from '../services/api';

export const UploadPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const { addToast } = useToast();
  const queryClient = useQueryClient();
  const [files, setFiles] = useState<UploadFile[]>([]);
  const [isProcessingAll, setIsProcessingAll] = useState(false);

  const handleFilesSelected = (newFiles: File[]) => {
    const fileObjects = newFiles.map(file => ({
      id: Math.random().toString(36).substring(7),
      file,
      progress: 0,
      status: 'Ready' as const,
    }));
    setFiles(prev => [...prev, ...fileObjects]);
  };

  const removeFile = (id: string) => {
    setFiles(prev => prev.filter(f => f.id !== id));
  };

  const pollJobUntilDone = async (jobId: string, fileId: string): Promise<boolean> => {
    const maxAttempts = 60; // 90 seconds max
    for (let i = 0; i < maxAttempts; i++) {
      await new Promise(r => setTimeout(r, 1500));
      try {
        const job = await api.getJob(jobId);
        const progress = Math.min(95, Math.max(20, Math.round((job.progress || 0.2) * 100)));
        setFiles(prev => prev.map(f => f.id === fileId ? { ...f, progress, status: 'Processing' } : f));

        if (job.status === 'SUCCEEDED') {
          setFiles(prev => prev.map(f => f.id === fileId ? { ...f, progress: 100, status: 'Completed' } : f));
          return true;
        } else if (job.status === 'FAILED' || job.status === 'CANCELLED') {
          setFiles(prev => prev.map(f => f.id === fileId ? { ...f, status: 'Failed' } : f));
          return false;
        }
      } catch (e) {
        console.error('Job polling error:', e);
      }
    }
    setFiles(prev => prev.map(f => f.id === fileId ? { ...f, status: 'Failed' } : f));
    return false;
  };

  const handleUploadAndProcess = async () => {
    if (!projectId) return;
    setIsProcessingAll(true);

    const pendingFiles = files.filter(f => f.status === 'Ready' || f.status === 'Failed');
    let anySuccess = false;

    for (const f of pendingFiles) {
      try {
        setFiles(prev => prev.map(item => item.id === f.id ? { ...item, status: 'Uploading', progress: 10 } : item));
        
        const uploadRes = await api.uploadPaper(projectId, f.file);
        setFiles(prev => prev.map(item => item.id === f.id ? { ...item, status: 'Processing', progress: 30 } : item));

        const success = await pollJobUntilDone(uploadRes.job_id, f.id);
        if (success) anySuccess = true;
      } catch (err: any) {
        console.error(`Failed to upload ${f.file.name}:`, err);
        setFiles(prev => prev.map(item => item.id === f.id ? { ...item, status: 'Failed' } : item));
        addToast(err?.response?.data?.error?.message || `Failed to process ${f.file.name}`, 'error');
      }
    }

    setIsProcessingAll(false);

    if (anySuccess) {
      await queryClient.invalidateQueries({ queryKey: ['papers', projectId] });
      await queryClient.invalidateQueries({ queryKey: ['project', projectId] });
      await queryClient.invalidateQueries({ queryKey: ['projects'] });
      await queryClient.invalidateQueries({ queryKey: ['gaps', projectId] });
      await queryClient.invalidateQueries({ queryKey: ['contradictions', projectId] });
      await queryClient.invalidateQueries({ queryKey: ['landscape', projectId] });
      addToast('Papers uploaded and processed into vector index successfully.', 'success');
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in duration-300">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-primary mb-2">Upload Literature</h2>
          <p className="text-secondary">Add PDF research papers to your project workspace for AI synthesis.</p>
        </div>
        <Button variant="secondary" onClick={() => navigate(`/projects/${projectId}/papers`)}>
          Back to Papers
        </Button>
      </div>

      <UploadDropzone onFilesSelected={handleFilesSelected} />

      {files.length > 0 && (
        <div className="space-y-6">
          <div className="flex justify-between items-center border-b border-border pb-4">
            <h3 className="font-bold text-primary">Selected Files ({files.length})</h3>
            <Button 
              onClick={handleUploadAndProcess}
              disabled={isProcessingAll || files.every(f => f.status === 'Completed')}
            >
              {isProcessingAll ? 'Processing Literature...' : 'Process All Papers'}
            </Button>
          </div>
          
          <div className="grid gap-4">
            {files.map(file => (
              <UploadFileRow key={file.id} file={file} onRemove={removeFile} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};