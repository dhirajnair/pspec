export interface Issue {
  code: string;
  message: string;
  line: number;
  column: number | null;
  pep8_quote: string;
  pep8_section: string;
  pep8_section_url: string | null;
  suggestion: string;
}

export interface PybpAdvisory {
  rule_id: string;
  title: string;
  category: string;
  line: number;
  function: string | null;
  class_name: string | null;
  explanation: string;
  authority: string;
  citation: string;
  suggestion: string;
  severity: string;
}

export interface ApiResponse {
  ok: boolean;
  pep8_date: string;
  pep8_url: string;
  pep8_revision: string;
  issues: Issue[];
  advisories: PybpAdvisory[];
  error: string | null;
}

const API_BASE = import.meta.env.VITE_API_URL ?? '';

export async function checkApi(code: string, pybpEnabled = true): Promise<ApiResponse> {
  const res = await fetch(`${API_BASE}/api/check`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code, pybp_enabled: pybpEnabled }),
  });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}`);
  }
  return res.json() as Promise<ApiResponse>;
}
