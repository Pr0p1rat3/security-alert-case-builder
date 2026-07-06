import type {
  AlertRecord,
  AuditLogRecord,
  CaseRecord,
  EvidenceRecord,
  IOC,
  MitreMapping,
  NoteRecord,
  ReportRecord,
  TaskRecord,
  TimelineEvent,
  User
} from "../types/models";

const API_BASE = import.meta.env.VITE_API_BASE ?? "/api";

let token = localStorage.getItem("sacb_token") ?? "";

export function setToken(next: string) {
  token = next;
  localStorage.setItem("sacb_token", next);
}

export function clearToken() {
  token = "";
  localStorage.removeItem("sacb_token");
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      ...(init.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init.headers
    }
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail ?? "Request failed");
  }
  return response.json() as Promise<T>;
}

async function requestBlob(path: string): Promise<Blob> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {}
  });
  if (!response.ok) {
    throw new Error(response.statusText);
  }
  return response.blob();
}

export const api = {
  login: (email: string, password: string) =>
    request<{ access_token: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password })
    }),
  me: () => request<User>("/auth/me"),
  dashboard: () => request<Record<string, unknown>>("/dashboard/summary"),
  cases: () => request<CaseRecord[]>("/cases"),
  createCase: (payload: Partial<CaseRecord>) =>
    request<CaseRecord>("/cases", { method: "POST", body: JSON.stringify(payload) }),
  caseDetail: (id: number) => request<CaseRecord>(`/cases/${id}`),
  updateCase: (id: number, payload: Partial<CaseRecord>) =>
    request<CaseRecord>(`/cases/${id}`, { method: "PATCH", body: JSON.stringify(payload) }),
  pasteAlert: (caseId: number, raw_content: string, source_system?: string) =>
    request<AlertRecord>(`/cases/${caseId}/alerts/paste`, {
      method: "POST",
      body: JSON.stringify({ raw_content, source_system })
    }),
  uploadAlert: (caseId: number, file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<AlertRecord>(`/cases/${caseId}/alerts/upload`, { method: "POST", body: form });
  },
  alerts: (caseId: number) => request<AlertRecord[]>(`/cases/${caseId}/alerts`),
  iocs: (caseId: number) => request<IOC[]>(`/cases/${caseId}/iocs`),
  enrichAll: (caseId: number) => request(`/cases/${caseId}/iocs/enrich-all`, { method: "POST" }),
  timeline: (caseId: number) => request<TimelineEvent[]>(`/cases/${caseId}/timeline`),
  createTimeline: (caseId: number, payload: Partial<TimelineEvent>) =>
    request<TimelineEvent>(`/cases/${caseId}/timeline`, { method: "POST", body: JSON.stringify(payload) }),
  suggestMitre: (caseId: number) => request(`/cases/${caseId}/mitre/suggest`, { method: "POST" }),
  mitre: (caseId: number) => request<MitreMapping[]>(`/cases/${caseId}/mitre`),
  tasks: (caseId: number) => request<TaskRecord[]>(`/cases/${caseId}/tasks`),
  updateTask: (taskId: number, payload: Partial<TaskRecord>) =>
    request<TaskRecord>(`/tasks/${taskId}`, { method: "PATCH", body: JSON.stringify(payload) }),
  evidence: (caseId: number) => request<EvidenceRecord[]>(`/cases/${caseId}/evidence`),
  uploadEvidence: (caseId: number, file: File, description: string) => {
    const form = new FormData();
    form.append("file", file);
    if (description) form.append("description", description);
    return request<EvidenceRecord>(`/cases/${caseId}/evidence`, { method: "POST", body: form });
  },
  deleteEvidence: (evidenceId: number) => request(`/evidence/${evidenceId}`, { method: "DELETE" }),
  downloadEvidence: (evidenceId: number) => requestBlob(`/evidence/${evidenceId}/download`),
  notes: (caseId: number) => request<NoteRecord[]>(`/cases/${caseId}/notes`),
  createNote: (caseId: number, body: string) =>
    request<NoteRecord>(`/cases/${caseId}/notes`, { method: "POST", body: JSON.stringify({ body }) }),
  reports: (caseId: number) => request<ReportRecord[]>(`/cases/${caseId}/reports`),
  generateReport: (caseId: number, report_type = "analyst", format = "markdown") =>
    request<ReportRecord>(`/cases/${caseId}/reports/generate`, {
      method: "POST",
      body: JSON.stringify({ report_type, format })
    }),
  audit: (caseId: number) => request<AuditLogRecord[]>(`/cases/${caseId}/audit`),
  users: () => request<User[]>("/users"),
  createUser: (payload: { email: string; display_name: string; password: string; role: string }) =>
    request<User>("/users", { method: "POST", body: JSON.stringify(payload) }),
  search: (q: string) => request<Record<string, unknown>>(`/search?q=${encodeURIComponent(q)}`)
};
