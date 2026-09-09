import React from 'react';
import { FileText, CheckCircle2, XCircle, Loader2, X } from 'lucide-react';
import { cn } from '../../utils/formatters';

export type UploadStatus = 'Ready' | 'Uploading' | 'Processing' | 'Completed' | 'Failed';

export interface UploadFile {
  id: string;
  file: File;
  progress: number;
  status: UploadStatus;
}

interface UploadFileRowProps {
  file: UploadFile;
  onRemove: (id: string) => void;
}

export const UploadFileRow: React.FC<UploadFileRowProps> = ({ file, onRemove }) => {
  const getStatusDisplay = () => {
    switch (file.status) {
      case 'Completed': return <CheckCircle2 size={20} className="text-success" />;
      case 'Failed': return <XCircle size={20} className="text-alert" />;
      case 'Uploading':
      case 'Processing':
        return <Loader2 size={20} className="text-accent animate-spin" />;
      default: return <FileText size={20} className="text-secondary" />;
    }
  };

  return (
    <div className="flex items-center gap-4 p-4 rounded-xl border border-border bg-surface shadow-sm">
      <div className="shrink-0">{getStatusDisplay()}</div>
      
      <div className="flex-1 min-w-0">
        <div className="flex justify-between items-center mb-2">
          <p className="text-sm font-semibold text-primary truncate pr-4">{file.file.name}</p>
          <span className="text-xs text-secondary shrink-0 font-medium">
            {(file.file.size / 1024 / 1024).toFixed(2)} MB
          </span>
        </div>
        
        <div className="h-2 bg-surface-raised border border-border rounded-full overflow-hidden">
          <div 
            className={cn(
              "h-full rounded-full transition-all duration-300",
              file.status === 'Failed' ? "bg-alert" : file.status === 'Completed' ? "bg-success" : "bg-accent"
            )}
            style={{ width: `${file.progress}%` }}
          />
        </div>
        
        <div className="flex justify-between items-center mt-2 text-xs font-semibold">
          <span className={cn(
            file.status === 'Failed' ? "text-alert" : file.status === 'Completed' ? "text-success" : "text-secondary"
          )}>
            {file.status}
          </span>
          {file.status !== 'Completed' && file.status !== 'Failed' && (
            <span className="text-accent">{Math.round(file.progress)}%</span>
          )}
        </div>
      </div>

      <button 
        onClick={() => onRemove(file.id)}
        disabled={file.status === 'Uploading' || file.status === 'Processing'}
        className="shrink-0 p-2 text-secondary hover:text-alert hover:bg-alert/10 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <X size={18} />
      </button>
    </div>
  );
};