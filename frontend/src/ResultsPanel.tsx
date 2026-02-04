import type { Issue } from './api';

type Status = 'idle' | 'loading' | 'success' | 'error';

interface ResultsPanelProps {
  status: Status;
  issues: Issue[];
  errorMessage: string | null;
  pep8Date: string | null;
  onRetry: () => void;
  onSelectIssue: (line: number) => void;
}

const PEP8_URL = 'https://peps.python.org/pep-0008/';

export default function ResultsPanel({
  status,
  issues,
  errorMessage,
  pep8Date,
  onRetry,
  onSelectIssue,
}: ResultsPanelProps) {
  return (
    <aside className="results-pane" aria-live="polite">
      {status === 'idle' && (
        <div className="results-state results-empty">
          <p>Paste code and click Check to validate.</p>
        </div>
      )}

      {status === 'loading' && (
        <div className="results-state results-loading">
          <div className="spinner" aria-hidden />
          <p>Checking PEP 8…</p>
        </div>
      )}

      {status === 'error' && (
        <div className="results-state results-error">
          <p className="error-message">{errorMessage ?? 'Something went wrong.'}</p>
          <button type="button" className="retry-btn" onClick={onRetry}>
            Retry
          </button>
        </div>
      )}

      {status === 'success' && issues.length === 0 && (
        <div className="results-state results-success-none">
          <p className="no-issues">No PEP 8 issues found.</p>
          {pep8Date && (
            <p className="pep8-date">
              Validated against <a href={PEP8_URL} target="_blank" rel="noopener noreferrer">PEP 8</a> (last updated: {pep8Date})
            </p>
          )}
        </div>
      )}

      {status === 'success' && issues.length > 0 && (
        <div className="results-list">
          <p className="results-heading">
            {issues.length} issue{issues.length !== 1 ? 's' : ''} found
            {pep8Date && (
              <span className="pep8-date-inline"> (PEP 8: {pep8Date})</span>
            )}
          </p>
          <ul className="issue-list">
            {issues.map((issue, i) => (
              <li
                key={`${issue.line}-${issue.column ?? 0}-${i}`}
                className="issue-item"
              >
                <button
                  type="button"
                  className="issue-trigger"
                  onClick={() => onSelectIssue(issue.line)}
                >
                  <span className="issue-loc">
                    Line {issue.line}
                    {issue.column != null ? `:${issue.column + 1}` : ''}
                  </span>
                  <span className="issue-code">{issue.code}</span>
                  <span className="issue-msg">{issue.message}</span>
                </button>
                <div className="issue-detail">
                  <p className="issue-type">
                    {issue.pep8_section_url ? (
                      <a href={issue.pep8_section_url} target="_blank" rel="noopener noreferrer">{issue.code} – {issue.pep8_section}</a>
                    ) : (
                      <>{issue.code} – {issue.pep8_section}</>
                    )}
                  </p>
                  <blockquote className="pep8-quote">{issue.pep8_quote}</blockquote>
                  <p className="suggestion"><strong>How to fix:</strong> {issue.suggestion}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </aside>
  );
}
