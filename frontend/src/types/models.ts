export type Role = "Admin" | "Analyst" | "Viewer";
export type Severity = "Informational" | "Low" | "Medium" | "High" | "Critical";
export type CaseStatus =
  | "New"
  | "Triage"
  | "Investigating"
  | "Containment"
  | "Eradication"
  | "Recovery"
  | "Closed"
  | "False Positive";

export interface User {
  id: number;
  email: string;
  display_name: string;
  role: Role;
}

export interface CaseRecord {
  id: number;
  title: string;
  description: string;
  severity: Severity;
  status: CaseStatus;
  source_system?: string;
  created_by_id: number;
  assigned_analyst_id?: number;
  created_at: string;
  updated_at: string;
  business_impact?: string;
  affected_users?: string;
  affected_hosts?: string;
  affected_ips?: string;
  affected_domains_urls?: string;
}

export interface AlertRecord {
  id: number;
  case_id: number;
  source_system?: string;
  alert_type: string;
  raw_content: string;
  parsed: Record<string, unknown>;
  confidence: number;
  created_at: string;
}

export interface IOC {
  id: number;
  case_id: number;
  type: string;
  value: string;
  raw_value: string;
  enrichments?: IOCEnrichment[];
}

export interface IOCEnrichment {
  id: number;
  ioc_id: number;
  provider_name: string;
  verdict: "Unknown" | "Benign" | "Suspicious" | "Malicious";
  confidence: number;
  summary: string;
  enriched_at: string;
}

export interface TimelineEvent {
  id: number;
  timestamp: string;
  event_type: string;
  source_system?: string;
  short_title: string;
  description: string;
  related_user?: string;
  related_host?: string;
  related_entity?: string;
  confidence: number;
}

export interface TaskRecord {
  id: number;
  case_id?: number;
  title: string;
  description: string;
  priority: string;
  status: string;
  assigned_to_id?: number;
  due_date?: string;
  completion_notes?: string;
}

export interface ReportRecord {
  id: number;
  report_type: string;
  format: string;
  content: string;
  created_at: string;
}

export interface EvidenceRecord {
  id: number;
  case_id: number;
  timeline_event_id?: number;
  file_name: string;
  content_type: string;
  sha256: string;
  size_bytes: number;
  uploaded_by_id: number;
  uploaded_at: string;
  description?: string;
}

export interface NoteRecord {
  id: number;
  case_id: number;
  author_id: number;
  body: string;
  created_at: string;
}

export interface TechniqueRecord {
  id: number;
  technique_id: string;
  technique_name: string;
  tactic: string;
  description?: string;
}

export interface MitreMapping {
  id: number;
  case_id: number;
  technique_id: number;
  technique?: TechniqueRecord;
  why_suggested: string;
  confidence: number;
  related_evidence?: string;
  analyst_status: "Suggested" | "Confirmed" | "Rejected";
}

export interface AuditLogRecord {
  id: number;
  actor_id?: number;
  case_id?: number;
  action: string;
  entity_type?: string;
  entity_id?: string;
  details: Record<string, unknown>;
  created_at: string;
}
