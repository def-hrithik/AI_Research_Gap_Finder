import React, { useCallback, useState } from 'react';
import { UploadCloud, FileType } from 'lucide-react';
import { cn } from '../../utils/formatters';

interface UploadDropzoneProps {
  onFilesSelected: (files: File[]) => void;
}

export const UploadDropzone: React.FC<UploadDropzoneProps> = ({ onFilesSelected }) => {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onFilesSelected(Array.from(e.dataTransfer.files));
    }
  }, [onFilesSelected]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onFilesSelected(Array.from(e.target.files));
    }
  }, [onFilesSelected]);

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={cn(
        "relative flex flex-col items-center justify-center p-12 text-center rounded-2xl border-2 border-dashed transition-all duration-200 bg-surface",
        isDragging ? "border-accent bg-accent/5" : "border-border hover:border-accent/50 hover:bg-surface-raised"
      )}
    >
      <input
        type="file"
        multiple
        accept="application/pdf"
        onChange={handleFileInput}
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        title="Upload PDFs"
      />
      <div className="w-16 h-16 bg-accent/10 text-accent rounded-2xl flex items-center justify-center mb-6 shadow-sm">
        <UploadCloud size={32} />
      </div>
      <h3 className="text-xl font-bold text-primary mb-2">Upload Research Papers</h3>
      <p className="text-secondary mb-6 max-w-sm leading-relaxed">
        Drag and drop your PDF files here, or click to browse. We will automatically extract methodologies, datasets, and limitations.
      </p>
      <div className="flex items-center gap-2 text-xs font-semibold text-secondary uppercase tracking-wider bg-background px-3 py-1.5 rounded-lg border border-border">
        <FileType size={14} /> PDF files only (Max 50MB each)
      </div>
    </div>
  );
};