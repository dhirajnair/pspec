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

export interface Location {
  line: number;
  column?: number | null;
  function?: string | null;
  class_name?: string | null;
}

export interface StaticAnalysisFinding {
  domain: string;
  rule_id: string;
  title: string;
  location: Location;
  severity: string;
  explanation: string;
  suggestion: string;
}

export interface ApiResponse {
  ok: boolean;
  pep8_date: string;
  pep8_url: string;
  pep8_revision: string;
  issues: Issue[];
  advisories: PybpAdvisory[];
  findings: StaticAnalysisFinding[];
  error: string | null;
}

const API_BASE = import.meta.env.VITE_API_URL ?? '';

export interface CheckOptions {
  pybpEnabled?: boolean;
  advancedEnabled?: boolean;
}

export async function checkApi(
  code: string,
  pybpEnabled = true,
  advancedEnabled = true,
): Promise<ApiResponse> {
  const body: Record<string, unknown> = {
    code,
    pybp_enabled: pybpEnabled,
  };
  if (!advancedEnabled) {
    body.enable_types = false;
    body.enable_dataflow = false;
    body.enable_errors = false;
    body.enable_security = false;
    body.enable_metrics = false;
    body.enable_insights = false;
  }
  const res = await fetch(`${API_BASE}/api/check`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}`);
  }
  return res.json() as Promise<ApiResponse>;
}
