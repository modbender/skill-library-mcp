import { useState, useRef } from 'react';
import { Upload, X, FileText, Check } from 'lucide-react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import type { BrainStatus } from '../../api/types';

interface UploadFile {
  id: string;
  file: File;
  status: 'pending' | 'uploading' | 'done' | 'error';
  error?: string;
}

interface FileIngestionProps {
  brains: BrainStatus[];
  defaultBrainId?: string;
  variant?: 'default' | 'sidebar';
}

export function FileIngestion({ brains, defaultBrainId, variant = 'default' }: FileIngestionProps) {
  const [selectedBrainId, setSelectedBrainId] = useState(defaultBrainId || 'nexus');
  const [dragActive, setDragActive] = useState(false);
  const [files, setFiles] = useState<UploadFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      addFiles(e.dataTransfer.files);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files.length > 0) {
      addFiles(e.target.files);
    }
  };

  const addFiles = (fileList: FileList) => {
    const newFiles: UploadFile[] = Array.from(fileList).map(file => ({
      id: Math.random().toString(36).substring(2, 9),
      file,
      status: 'pending',
    }));
    setFiles(prev => [...prev, ...newFiles]);
  };

  const removeFile = (id: string) => {
    setFiles(prev => prev.filter(f => f.id !== id));
  };

  const uploadFiles = async () => {
    if (files.length === 0) return;
    
    setIsUploading(true);
    
    for (const uploadFile of files) {
      if (uploadFile.status === 'done') continue;
      
      setFiles(prev => prev.map(f => 
        f.id === uploadFile.id ? { ...f, status: 'uploading' } : f
      ));

      const formData = new FormData();
      formData.append('file', uploadFile.file);

      try {
        const response = await fetch(`/api/upload?brainId=${encodeURIComponent(selectedBrainId)}`, {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          setFiles(prev => prev.map(f => 
            f.id === uploadFile.id ? { ...f, status: 'done' } : f
          ));
        } else {
          const error = await response.text();
          setFiles(prev => prev.map(f => 
            f.id === uploadFile.id ? { ...f, status: 'error', error } : f
          ));
        }
      } catch (err) {
        setFiles(prev => prev.map(f => 
          f.id === uploadFile.id ? { ...f, status: 'error', error: 'Network error' } : f
        ));
      }
    }

    setIsUploading(false);
  };

  const clearCompleted = () => {
    setFiles(prev => prev.filter(f => f.status !== 'done'));
  };

  const selectedBrainName = brains.find(b => b.id === selectedBrainId)?.name || selectedBrainId;

  const isSidebar = variant === 'sidebar';

  return (
    <Card className={isSidebar ? 'p-4' : ''}>
      <div className={isSidebar ? 'flex items-center justify-between mb-3' : ''}>
        <h2 className={isSidebar ? 'text-sm font-semibold flex items-center gap-2' : 'text-lg font-semibold mb-4 flex items-center gap-2'}>
          <Upload className={isSidebar ? 'w-4 h-4 text-blue-400' : 'w-5 h-5 text-blue-400'} />
          File Ingestion
        </h2>
      </div>

      {/* Brain Selector */}
      <div className="mb-4">
        <label className="text-sm font-medium mb-2 block">Target Brain</label>
        <select
          value={selectedBrainId}
          onChange={(e) => setSelectedBrainId(e.target.value)}
          className="w-full px-3 py-2 rounded-lg border border-border bg-secondary"
          disabled={isUploading}
        >
          <option value="nexus">Nexus (Default)</option>
          {brains.filter(b => b.id !== 'nexus').map(brain => (
            <option key={brain.id} value={brain.id}>
              {brain.name}
            </option>
          ))}
        </select>
        <p className="text-xs text-muted-foreground mt-1">
          Files go to: <code className="bg-secondary/50 px-1 rounded">data/{selectedBrainId}/intake/</code>
        </p>
      </div>
      
      {/* Drop Zone */}
      <form
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className="relative"
      >
        <input
          ref={inputRef}
          type="file"
          id="file-upload"
          multiple
          onChange={handleChange}
          className="hidden"
          disabled={isUploading}
        />
        
        <label
          htmlFor="file-upload"
          className={`
            flex flex-col items-center justify-center
            border border-dashed rounded-xl
            cursor-pointer transition-all duration-200
            ${variant === 'sidebar' ? 'p-4' : 'p-6'}
            ${dragActive
              ? 'border-blue-500 bg-blue-500/10'
              : 'border-border hover:border-blue-500/50 hover:bg-blue-500/5'
            }
            ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}
          `}
        >
          <Upload className={variant === 'sidebar' ? 'w-7 h-7 text-muted-foreground mb-2' : 'w-10 h-10 text-muted-foreground mb-2'} />
          <p className={variant === 'sidebar' ? 'text-xs font-medium mb-1 text-center' : 'text-sm font-medium mb-1'}>
            Drop or click to upload
          </p>
          <p className={variant === 'sidebar' ? 'text-[11px] text-muted-foreground text-center' : 'text-xs text-muted-foreground'}>
            PDF, TXT, MD, JSON, ZIP
          </p>
        </label>
      </form>

      {/* File List */}
      {files.length > 0 && (
        <div className="mt-4 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">
              {files.length} file{files.length !== 1 ? 's' : ''}
            </span>
            {files.some(f => f.status === 'done') && (
              <button
                onClick={clearCompleted}
                className="text-xs text-muted-foreground hover:text-foreground"
              >
                Clear completed
              </button>
            )}
          </div>
          
          <div className="max-h-40 overflow-y-auto space-y-1">
            {files.map(uploadFile => (
              <div
                key={uploadFile.id}
                className={`flex items-center gap-2 p-2 rounded-lg text-sm ${
                  uploadFile.status === 'done' ? 'bg-green-500/10' :
                  uploadFile.status === 'error' ? 'bg-red-500/10' :
                  uploadFile.status === 'uploading' ? 'bg-blue-500/10' :
                  'bg-secondary/50'
                }`}
              >
                <FileText className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                <span className="flex-1 truncate">{uploadFile.file.name}</span>
                
                {uploadFile.status === 'done' && (
                  <Check className="w-4 h-4 text-green-500 flex-shrink-0" />
                )}
                {uploadFile.status === 'uploading' && (
                  <span className="text-xs text-blue-400">Uploading...</span>
                )}
                {uploadFile.status === 'error' && (
                  <span className="text-xs text-red-400" title={uploadFile.error}>
                    Error
                  </span>
                )}
                
                <button
                  onClick={() => removeFile(uploadFile.id)}
                  disabled={uploadFile.status === 'uploading'}
                  className="p-1 hover:bg-secondary rounded"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>

          <Button
            variant="primary"
            size="sm"
            onClick={uploadFiles}
            disabled={isUploading || files.length === 0 || files.every(f => f.status === 'done')}
            className="w-full"
          >
            {isUploading ? 'Uploading...' : `Upload to ${selectedBrainName}`}
          </Button>
        </div>
      )}
    </Card>
  );
}
