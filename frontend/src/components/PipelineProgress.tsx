import { Check, Circle, Loader, AlertCircle } from "lucide-react";
import { memo } from "react";
import type { ProgressStep } from "../types";

interface Props {
  steps: ProgressStep[];
}

const STATUS_ICON = {
  pending: <Circle size={16} className="step-icon pending" aria-hidden="true" />,
  running: <Loader size={16} className="step-icon running spin" aria-hidden="true" />,
  completed: <Check size={16} className="step-icon completed" aria-hidden="true" />,
  error: <AlertCircle size={16} className="step-icon error" aria-hidden="true" />,
};

export const PipelineProgress = memo(function PipelineProgress({ steps }: Props) {
  const completedCount = steps.filter((s) => s.status === "completed").length;
  const pct = (completedCount / steps.length) * 100;

  return (
    <div className="pipeline-progress" aria-label="Pipeline progress">
      <h2>
        Pipeline Progress
        <span className="step-count">
          {completedCount}/{steps.length}
        </span>
      </h2>
      <div
        className="progress-bar-container"
        role="progressbar"
        aria-valuenow={pct}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={`${completedCount} of ${steps.length} steps completed`}
      >
        <div
          className="progress-bar-fill"
          style={{ width: `${pct}%` }}
        />
      </div>
      <ul className="step-list" aria-label="Processing steps">
        {steps.map((step) => (
          <li key={step.node} className={`step-item ${step.status}`}>
            {STATUS_ICON[step.status]}
            <div className="step-info">
              <span className="step-label">{step.label}</span>
              {step.status === "completed" && step.outputs && (
                <span className="step-meta">
                  {Object.entries(step.outputs)
                    .map(([k, v]) => `${k}: ${v}`)
                    .join(", ")}
                </span>
              )}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
});
