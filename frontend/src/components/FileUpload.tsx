import { Upload, X } from "lucide-react";
import { useRef } from "react";

interface Props {
  files: File[];
  onFilesChange: (files: File[]) => void;
  disabled: boolean;
  uploadProgress: number | null;
}

export function FileUpload({ files, onFilesChange, disabled, uploadProgress }: Props) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      onFilesChange([...files, ...Array.from(e.target.files)]);
    }
  };

  const removeFile = (index: number) => {
    onFilesChange(files.filter((_, i) => i !== index));
  };

  return (
    <div className="input-group">
      <label>Invoice images (PNG, JPG, TIFF, etc.)</label>
      <div
        className="drop-zone"
        role="button"
        tabIndex={0}
        aria-label="Click or drag files to upload invoice images"
        onClick={() => !disabled && fileInputRef.current?.click()}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            fileInputRef.current?.click();
          }
        }}
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          if (e.dataTransfer.files) {
            onFilesChange([...files, ...Array.from(e.dataTransfer.files)]);
          }
        }}
      >
        <Upload size={24} />
        <p>Click or drag files here</p>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept="image/*"
          onChange={handleFileChange}
          style={{ display: "none" }}
          aria-hidden="true"
        />
      </div>
      {uploadProgress !== null && (
        <div className="upload-progress" role="progressbar" aria-valuenow={uploadProgress} aria-valuemin={0} aria-valuemax={100}>
          <div className="upload-progress-bar" style={{ width: `${uploadProgress}%` }} />
          <span className="upload-progress-label">Uploading... {uploadProgress}%</span>
        </div>
      )}
      {files.length > 0 && (
        <ul className="file-list" aria-label="Selected files">
          {files.map((f, i) => (
            <li key={`${f.name}-${i}`}>
              <span>{f.name}</span>
              <button
                onClick={() => removeFile(i)}
                className="icon-btn"
                aria-label={`Remove ${f.name}`}
                disabled={disabled}
              >
                <X size={14} />
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
