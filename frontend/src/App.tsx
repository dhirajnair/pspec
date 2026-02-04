import { useState, useCallback } from 'react';
import CodeEditor from './CodeEditor';
import ResultsPanel from './ResultsPanel';
import { checkApi, type ApiResponse, type Issue } from './api';

const PEP8_URL = 'https://peps.python.org/pep-0008/';

export default function App() {
  const [code, setCode] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [pep8Date, setPep8Date] = useState<string | null>(null);
  const [pep8Url, setPep8Url] = useState<string | null>(null);
  const [pep8Revision, setPep8Revision] = useState<string | null>(null);
  const [issues, setIssues] = useState<Issue[]>([]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [selectedLine, setSelectedLine] = useState<number | null>(null);

  const handleClear = useCallback(() => {
    setCode('');
    setStatus('idle');
    setIssues([]);
    setErrorMessage(null);
    setSelectedLine(null);
  }, []);

  const handleCheck = useCallback(async () => {
    setStatus('loading');
    setErrorMessage(null);
    setIssues([]);
    try {
      const res: ApiResponse = await checkApi(code);
      setPep8Date(res.pep8_date ?? null);
      setPep8Url(res.pep8_url ?? null);
      setPep8Revision(res.pep8_revision ?? null);
      if (!res.ok) {
        setErrorMessage(res.error ?? 'Validation failed');
        setStatus('error');
        return;
      }
      setIssues(res.issues ?? []);
      setStatus('success');
    } catch (e) {
      setErrorMessage(e instanceof Error ? e.message : 'Network or server error');
      setStatus('error');
    }
  }, [code]);

  return (
    <div className="app">
      <header className="header">
        <h1>PEP 8 Compliance Checker</h1>
        <p className="pep8-ref">
          Validated against{' '}
          <a href={pep8Url || PEP8_URL} target="_blank" rel="noopener noreferrer">
            PEP 8
          </a>
          {pep8Date ? ` (revision date: ${pep8Date})` : ''}
          {pep8Revision ? ` · ${pep8Revision}` : ''}
        </p>
      </header>

      <div className="main">
        <section className="editor-pane">
          <CodeEditor
            value={code}
            onChange={setCode}
            placeholder="Paste or type Python code here"
            highlightedLine={selectedLine}
          />
          <div className="editor-actions">
            <button
              type="button"
              className="check-btn"
              onClick={handleCheck}
              disabled={status === 'loading'}
            >
              {status === 'loading' ? 'Checking…' : 'Check PEP 8 Compliance'}
            </button>
            <button type="button" className="clear-btn" onClick={handleClear}>
              Clear
            </button>
          </div>
        </section>

        <ResultsPanel
          status={status}
          issues={issues}
          errorMessage={errorMessage}
          pep8Date={pep8Date}
          onRetry={handleCheck}
          onSelectIssue={(line) => setSelectedLine(line)}
        />
      </div>
    </div>
  );
}
