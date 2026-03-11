interface Props {
  value: string;
  onChange: (value: string) => void;
  disabled: boolean;
}

export function FolderInput({ value, onChange, disabled }: Props) {
  return (
    <div className="input-group">
      <label htmlFor="folder-path">Server-side folder path</label>
      <input
        id="folder-path"
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="sample_invoices"
        disabled={disabled}
        aria-label="Server-side folder path for invoice images"
      />
    </div>
  );
}
