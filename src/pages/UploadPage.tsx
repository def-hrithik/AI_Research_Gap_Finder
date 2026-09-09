import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { UploadDropzone } from '../components/papers/UploadDropzone';
import { UploadFileRow } from '../components/papers/UploadFileRow';
import type { UploadFile } from '../components/papers/UploadFileRow';
import { Button } from '../components/common/Button';
import { useToast } from '../context/ToastContext';

export const UploadPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const { addToast } = useToast();
  const [files, setFiles] = useState<UploadFile[]>([]);
  const [isProcessingAll, setIsProcessingAll] = useState(false);

  const handleFilesSelected = (newFiles: File[]) => {
    const fileObjects = newFiles.map(file => ({
      id: Math.random().toString(36).substring(7),
      file,
      progress: 0,
      status: 'Ready' as const
    }));
    setFiles(prev => [...prev, ...fileObjects]);
  };

  const removeFile = (id: string) => {
    setFiles(prev => prev.filter(f => f.id !== id));
  };

  const handleUploadAndProcess = () => {
    setIsProcessingAll(true);
    
    // Simulate upload and processing for each file
    files.forEach((file, index) => {
      if (file.status === 'Completed' || file.status === 'Failed') return;

      setTimeout(() => {
        setFiles(prev => prev.map(f => f.id === file.id ? { ...f, status: 'Uploading', progress: 10 } : f));
        
        let progress = 10;
        const uploadInterval = setInterval(() => {
          progress += Math.random() * 20;
          if (progress >= 100) {
            clearInterval(uploadInterval);
            setFiles(prev => prev.map(f => f.id === file.id ? { ...f, status: 'Processing', progress: 100 } : f));
            
            // Simulate AI processing phase
            setTimeout(() => {
              const success = Math.random() > 0.1; // 90% success rate
              setFiles(prev => prev.map(f => f.id === file.id ? { 
                ...f, 
                status: success ? 'Completed' : 'Failed' 
              } : f));

              // Check if all are done
              setFiles(currentFiles => {
                const allDone = currentFiles.every(cf => cf.status === 'Completed' || cf.status === 'Failed');
                if (allDone) {
                  setIsProcessingAll(false);
                  addToast('Processing complete. Papers have been added to your workspace.', 'success');
                }
                return currentFiles;
              });

            }, 2000 + Math.random() * 2000);
          } else {
            setFiles(prev => prev.map(f => f.id === file.id ? { ...f, progress } : f));
          }
        }, 300);
      }, index * 500); // Stagger start times
    });
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
              {isProcessingAll ? 'Processing...' : 'Process All Papers'}
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