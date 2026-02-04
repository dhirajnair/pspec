import type { Issue, PybpAdvisory, StaticAnalysisFinding } from './api';

type Status = 'idle' | 'loading' | 'success' | 'error';

const CORRECTNESS_DOMAINS = ['types', 'dataflow', 'errors', 'security'];
const METRICS_DOMAINS = ['metrics', 'insights'];

function findingsByDomain(findings: StaticAnalysisFinding[]) {
  const correctness = findings.filter((f) => CORRECTNESS_DOMAINS.includes(f.domain));
  const metrics = findings.filter((f) => METRICS_DOMAINS.includes(f.domain));
  return { correctness, metrics };
}

interface ResultsPanelProps {
  status: Status;
  issues: Issue[];
  advisories: PybpAdvisory[];
  findings: StaticAnalysisFinding[];
  pybpEnabled: boolean;
  advancedEnabled: boolean;
  errorMessage: string | null;
  pep8Date: string | null;
  onRetry: () => void;
  onSelectIssue: (line: number) => void;
}

const PEP8_URL = 'https://peps.python.org/pep-0008/';

export default function ResultsPanel({
  status,
  issues,
  advisories,
  findings,
  pybpEnabled,
  advancedEnabled,
  errorMessage,
  pep8Date,
  onRetry,
  onSelectIssue,
}: ResultsPanelProps) {
  const { correctness, metrics } = findingsByDomain(findings);
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

      {status === 'success' && (
        <>
          <section className="results-section results-pep8" aria-label="PEP 8 Compliance">
            <h3 className="results-section-title results-pep8-title">✔ PEP 8 Compliance</h3>
            {issues.length === 0 ? (
              <p className="no-issues">No PEP 8 issues found.</p>
            ) : (
              <div className="results-list">
                <p className="results-heading">
                  {issues.length} issue{issues.length !== 1 ? 's' : ''} found
                  {pep8Date && <span className="pep8-date-inline"> (PEP 8: {pep8Date})</span>}
                </p>
                <ul className="issue-list">
                  {issues.map((issue, i) => (
                    <li key={`${issue.line}-${issue.column ?? 0}-${i}`} className="issue-item">
                      <button type="button" className="issue-trigger" onClick={() => onSelectIssue(issue.line)}>
                        <span className="issue-loc">Line {issue.line}{issue.column != null ? `:${issue.column + 1}` : ''}</span>
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
            {pep8Date && issues.length === 0 && (
              <p className="pep8-date">Validated against <a href={PEP8_URL} target="_blank" rel="noopener noreferrer">PEP 8</a> (last updated: {pep8Date})</p>
            )}
          </section>

          {pybpEnabled && (
            <section className="results-section results-pybp" aria-label="Best Practice Advisories">
              <h3 className="results-section-title results-pybp-title">⚠ Best Practice Advisories (PYBP)</h3>
              {advisories.length === 0 ? (
                <p className="no-advisories">No advisories for this code.</p>
              ) : (
                <ul className="advisory-list">
                  {advisories.map((a, i) => (
                    <li key={`${a.rule_id}-${a.line}-${i}`} className="advisory-item">
                      <button type="button" className="advisory-trigger" onClick={() => onSelectIssue(a.line)}>
                        <span className="advisory-severity">{a.severity}</span>
                        <span className="advisory-loc">Line {a.line}</span>
                        <span className="advisory-title">{a.title}</span>
                        <span className="advisory-category">{a.category}</span>
                      </button>
                      <div className="advisory-detail">
                        <p className="advisory-explanation">{a.explanation}</p>
                        <p className="advisory-authority"><strong>Authority:</strong> {a.authority} — {a.citation}</p>
                        <p className="advisory-suggestion"><strong>Suggestion:</strong> {a.suggestion}</p>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </section>
          )}

          {advancedEnabled && (
            <>
              <section className="results-section results-correctness" aria-label="Correctness & Safety">
                <h3 className="results-section-title results-correctness-title">🛡 Correctness & Safety</h3>
                {correctness.length === 0 ? (
                  <p className="no-findings">No type, data-flow, error, or security findings.</p>
                ) : (
                  <ul className="findings-list">
                    {correctness.map((f, i) => (
                      <li key={`${f.rule_id}-${f.location.line}-${i}`} className="finding-item finding-correctness">
                        <button type="button" className="finding-trigger" onClick={() => onSelectIssue(f.location.line)}>
                          <span className="finding-domain">{f.domain}</span>
                          <span className="finding-severity">{f.severity}</span>
                          <span className="finding-loc">Line {f.location.line}</span>
                          <span className="finding-title">{f.title}</span>
                        </button>
                        <div className="finding-detail">
                          <p className="finding-explanation">{f.explanation}</p>
                          <p className="finding-suggestion"><strong>Suggestion:</strong> {f.suggestion}</p>
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </section>

              <section className="results-section results-metrics" aria-label="Metrics & Insights">
                <h3 className="results-section-title results-metrics-title">📊 Metrics & Insights</h3>
                {metrics.length === 0 ? (
                  <p className="no-findings">No metrics or insight synthesis for this code.</p>
                ) : (
                  <ul className="findings-list">
                    {metrics.map((f, i) => (
                      <li key={`${f.rule_id}-${f.location.line}-${i}`} className="finding-item finding-metrics">
                        <button type="button" className="finding-trigger" onClick={() => onSelectIssue(f.location.line)}>
                          <span className="finding-domain">{f.domain}</span>
                          <span className="finding-severity">{f.severity}</span>
                          <span className="finding-loc">Line {f.location.line}</span>
                          <span className="finding-title">{f.title}</span>
                        </button>
                        <div className="finding-detail">
                          <p className="finding-explanation">{f.explanation}</p>
                          <p className="finding-suggestion"><strong>Suggestion:</strong> {f.suggestion}</p>
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </section>
            </>
          )}
        </>
      )}
    </aside>
  );
}
