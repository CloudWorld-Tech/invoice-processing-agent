import { MessageSquare } from "lucide-react";

interface Props {
  value: string;
  onChange: (value: string) => void;
  visible: boolean;
  onToggle: () => void;
  disabled: boolean;
}

export function PromptToggle({ value, onChange, visible, onToggle, disabled }: Props) {
  return (
    <>
      <button
        className="prompt-toggle"
        onClick={onToggle}
        aria-expanded={visible}
        aria-controls="custom-prompt"
      >
        <MessageSquare size={14} />
        {visible ? "Hide" : "Add"} custom prompt
      </button>

      {visible && (
        <div className="input-group">
          <label htmlFor="custom-prompt">Custom instructions (optional)</label>
          <textarea
            id="custom-prompt"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder="e.g. Focus on travel expenses..."
            rows={2}
            disabled={disabled}
            aria-label="Custom instructions for invoice processing"
          />
        </div>
      )}
    </>
  );
}
