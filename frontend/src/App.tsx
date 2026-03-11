import { Header } from "./components/Header";
import { InputPanel } from "./components/InputPanel";
import { PipelineProgress } from "./components/PipelineProgress";
import { InvoiceTable } from "./components/InvoiceTable";
import { SummaryPanel } from "./components/SummaryPanel";
import { EventLog } from "./components/EventLog";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { useInvoiceRun } from "./hooks/useInvoiceRun";
import "./App.css";

function App() {
  const {
    status,
    runId,
    steps,
    invoices,
    finalResult,
    error,
    events,
    uploadProgress,
    startRunWithFolder,
    startRunWithFiles,
    cancel,
    reset,
  } = useInvoiceRun();

  const isActive = status !== "idle";

  return (
    <ErrorBoundary>
      <div className="app">
        <Header status={status} runId={runId} />

        <main className="main-content">
          <div className="left-column">
            <InputPanel
              status={status}
              onStartFolder={startRunWithFolder}
              onStartFiles={startRunWithFiles}
              onCancel={cancel}
              onReset={reset}
              uploadProgress={uploadProgress}
            />

            {isActive && <PipelineProgress steps={steps} />}

            {isActive && <EventLog events={events} />}
          </div>

          <div className="right-column">
            {error && (
              <div className="error-banner" role="alert">
                <strong>Error:</strong> {error}
              </div>
            )}

            <InvoiceTable invoices={invoices} />

            {finalResult && <SummaryPanel result={finalResult} />}

            {!isActive && invoices.length === 0 && (
              <div className="empty-state">
                <div className="empty-icon" aria-hidden="true">📄</div>
                <h3>No invoices processed yet</h3>
                <p>
                  Upload invoice images or provide a server-side folder path to get
                  started. The AI agent will extract, normalize, categorize, and
                  summarize all invoices.
                </p>
              </div>
            )}
          </div>
        </main>
      </div>
    </ErrorBoundary>
  );
}

export default App;
