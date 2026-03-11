import { FolderOpen, Upload, Play } from "lucide-react";
import { useCallback, useState } from "react";
import type { RunStatus } from "../types";
import { FolderInput } from "./FolderInput";
import { FileUpload } from "./FileUpload";
import { PromptToggle } from "./PromptToggle";

interface Props {
  status: RunStatus;
  onStartFolder: (folder: string, prompt?: string) => void;
  onStartFiles: (files: File[], prompt?: string) => void;
  onCancel: () => void;
  onReset: () => void;
  uploadProgress: number | null;
}

export function InputPanel({
  status,
  onStartFolder,
  onStartFiles,
  onCancel,
  onReset,
  uploadProgress,
}: Props) {
  const [mode, setMode] = useState<"folder" | "upload">("folder");
  const [folderPath, setFolderPath] = useState("sample_invoices");
  const [files, setFiles] = useState<File[]>([]);
  const [prompt, setPrompt] = useState("");
  const [showPrompt, setShowPrompt] = useState(false);

  const isRunning = status === "running" || status === "connecting";
  const isDone = status === "completed" || status === "error";

  const handleSubmit = useCallback(() => {
    const p = prompt.trim() || undefined;
    if (mode === "folder") {
      if (!folderPath.trim()) return;
      onStartFolder(folderPath.trim(), p);
    } else {
      if (files.length === 0) return;
      onStartFiles(files, p);
    }
  }, [mode, folderPath, files, prompt, onStartFolder, onStartFiles]);

  return (
    <div className="input-panel" role="form" aria-label="Invoice processing input">
      <h2>Input</h2>

      <div className="mode-toggle" role="tablist" aria-label="Input mode">
        <button
          className={`mode-btn ${mode === "folder" ? "active" : ""}`}
          onClick={() => setMode("folder")}
          disabled={isRunning}
          role="tab"
          aria-selected={mode === "folder"}
          aria-controls="input-folder"
        >
          <FolderOpen size={16} aria-hidden="true" />
          Folder Path
        </button>
        <button
          className={`mode-btn ${mode === "upload" ? "active" : ""}`}
          onClick={() => setMode("upload")}
          disabled={isRunning}
          role="tab"
          aria-selected={mode === "upload"}
          aria-controls="input-upload"
        >
          <Upload size={16} aria-hidden="true" />
          Upload Files
        </button>
      </div>

      {mode === "folder" ? (
        <div id="input-folder" role="tabpanel">
          <FolderInput
            value={folderPath}
            onChange={setFolderPath}
            disabled={isRunning}
          />
        </div>
      ) : (
        <div id="input-upload" role="tabpanel">
          <FileUpload
            files={files}
            onFilesChange={setFiles}
            disabled={isRunning}
            uploadProgress={uploadProgress}
          />
        </div>
      )}

      <PromptToggle
        value={prompt}
        onChange={setPrompt}
        visible={showPrompt}
        onToggle={() => setShowPrompt(!showPrompt)}
        disabled={isRunning}
      />

      <div className="action-buttons">
        {isDone ? (
          <button className="btn btn-primary" onClick={onReset}>
            New Run
          </button>
        ) : isRunning ? (
          <button className="btn btn-danger" onClick={onCancel}>
            Cancel
          </button>
        ) : (
          <button
            className="btn btn-primary"
            onClick={handleSubmit}
            disabled={mode === "folder" ? !folderPath.trim() : files.length === 0}
            aria-label="Start processing invoices"
          >
            <Play size={16} aria-hidden="true" />
            Process Invoices
          </button>
        )}
      </div>
    </div>
  );
}
