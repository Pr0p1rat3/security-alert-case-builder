import { FormEvent, useCallback, useEffect, useState } from "react";
import { api } from "../api/client";
import { SeverityBadge } from "../components/SeverityBadge";
import { Tabs } from "../components/Tabs";
import type {
  AlertRecord,
  AuditLogRecord,
  CaseRecord,
  CaseStatus,
  EvidenceRecord,
  IOC,
  MitreMapping,
  NoteRecord,
  ReportRecord,
  Severity,
  TaskRecord,
  TimelineEvent
} from "../types/models";

const tabs = ["Overview", "Raw Alerts", "Timeline", "IOCs", "Evidence", "MITRE Mapping", "Tasks", "Notes", "Reports", "Audit Log"];

export function CaseDetailPage({ caseId, onBack }: { caseId: number; onBack: () => void }) {
  const [active, setActive] = useState("Overview");
  const [caseRecord, setCaseRecord] = useState<CaseRecord | null>(null);
  const [alerts, setAlerts] = useState<AlertRecord[]>([]);
  const [iocs, setIocs] = useState<IOC[]>([]);
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [mappings, setMappings] = useState<MitreMapping[]>([]);
  const [tasks, setTasks] = useState<TaskRecord[]>([]);
  const [evidence, setEvidence] = useState<EvidenceRecord[]>([]);
  const [notes, setNotes] = useState<NoteRecord[]>([]);
  const [reports, setReports] = useState<ReportRecord[]>([]);
  const [audit, setAudit] = useState<AuditLogRecord[]>([]);
  const [message, setMessage] = useState("");

  const load = useCallback(async () => {
    const [
      detail,
      alertRows,
      iocRows,
      timelineRows,
      mappingRows,
      taskRows,
      evidenceRows,
      noteRows,
      reportRows,
      auditRows
    ] = await Promise.all([
      api.caseDetail(caseId),
      api.alerts(caseId),
      api.iocs(caseId),
      api.timeline(caseId),
      api.mitre(caseId),
      api.tasks(caseId),
      api.evidence(caseId),
      api.notes(caseId),
      api.reports(caseId),
      api.audit(caseId)
    ]);
    setCaseRecord(detail);
    setAlerts(alertRows);
    setIocs(iocRows);
    setTimeline(timelineRows);
    setMappings(mappingRows);
    setTasks(taskRows);
    setEvidence(evidenceRows);
    setNotes(noteRows);
    setReports(reportRows);
    setAudit(auditRows);
  }, [caseId]);

  useEffect(() => {
    load().catch((err) => setMessage(err instanceof Error ? err.message : "Load failed"));
  }, [load]);

  async function action(fn: () => Promise<unknown>, success: string) {
    setMessage("");
    try {
      await fn();
      await load();
      setMessage(success);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Action failed");
    }
  }

  if (!caseRecord) {
    return <div className="text-slate-300">Loading case...</div>;
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <button onClick={onBack} className="mb-2 text-sm text-sky-200 hover:underline">Back to cases</button>
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-2xl font-semibold text-white">CASE-{caseRecord.id} {caseRecord.title}</h1>
            <SeverityBadge severity={caseRecord.severity} />
            <span className="rounded border border-line bg-panel px-2 py-1 text-xs text-slate-300">{caseRecord.status}</span>
          </div>
          <p className="mt-2 max-w-4xl text-sm text-slate-400">{caseRecord.description || "No description yet."}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <select
            value={caseRecord.severity}
            onChange={(event) => action(() => api.updateCase(caseId, { severity: event.target.value as Severity }), "Case severity updated.")}
            className="rounded border border-line bg-panel px-3 py-2 text-sm text-white"
          >
            {["Informational", "Low", "Medium", "High", "Critical"].map((item) => <option key={item}>{item}</option>)}
          </select>
          <select
            value={caseRecord.status}
            onChange={(event) => action(() => api.updateCase(caseId, { status: event.target.value as CaseStatus }), "Case status updated.")}
            className="rounded border border-line bg-panel px-3 py-2 text-sm text-white"
          >
            {["New", "Triage", "Investigating", "Containment", "Eradication", "Recovery", "Closed", "False Positive"].map((item) => <option key={item}>{item}</option>)}
          </select>
        </div>
      </div>
      {message && <div className="rounded-md border border-sky-500 bg-sky-950 p-3 text-sm text-sky-100">{message}</div>}
      <Tabs tabs={tabs} active={active} onChange={setActive} />
      {active === "Overview" && <OverviewTab caseRecord={caseRecord} alerts={alerts} iocs={iocs} timeline={timeline} tasks={tasks} mappings={mappings} />}
      {active === "Raw Alerts" && <RawAlertsTab caseId={caseId} alerts={alerts} onAction={action} />}
      {active === "Timeline" && <TimelineTab caseId={caseId} timeline={timeline} onAction={action} />}
      {active === "IOCs" && <IocsTab caseId={caseId} iocs={iocs} onAction={action} />}
      {active === "Evidence" && <EvidenceTab caseId={caseId} evidence={evidence} onAction={action} />}
      {active === "MITRE Mapping" && <MitreTab caseId={caseId} mappings={mappings} onAction={action} />}
      {active === "Tasks" && <TasksTab tasks={tasks} onAction={action} />}
      {active === "Notes" && <NotesTab caseId={caseId} notes={notes} onAction={action} />}
      {active === "Reports" && <ReportsTab caseId={caseId} reports={reports} onAction={action} />}
      {active === "Audit Log" && <AuditTab audit={audit} />}
    </div>
  );
}

function OverviewTab({ caseRecord, alerts, iocs, timeline, tasks, mappings }: { caseRecord: CaseRecord; alerts: AlertRecord[]; iocs: IOC[]; timeline: TimelineEvent[]; tasks: TaskRecord[]; mappings: MitreMapping[] }) {
  return (
    <div className="grid gap-4 lg:grid-cols-3">
      <section className="rounded-lg border border-line bg-panel p-4 lg:col-span-2">
        <h2 className="font-semibold text-white">Case summary</h2>
        <dl className="mt-4 grid gap-3 text-sm md:grid-cols-2">
          <Info label="Source" value={caseRecord.source_system ?? "Not set"} />
          <Info label="Created" value={new Date(caseRecord.created_at).toLocaleString()} />
          <Info label="Affected users" value={caseRecord.affected_users ?? "-"} />
          <Info label="Affected hosts" value={caseRecord.affected_hosts ?? "-"} />
          <Info label="Affected IPs" value={caseRecord.affected_ips ?? "-"} />
          <Info label="Domains/URLs" value={caseRecord.affected_domains_urls ?? "-"} />
        </dl>
      </section>
      <section className="rounded-lg border border-line bg-panel p-4">
        <h2 className="font-semibold text-white">Workflow counts</h2>
        <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
          <Metric label="Alerts" value={alerts.length} />
          <Metric label="IOCs" value={iocs.length} />
          <Metric label="Timeline" value={timeline.length} />
          <Metric label="MITRE" value={mappings.length} />
          <Metric label="Open tasks" value={tasks.filter((task) => task.status !== "Done" && task.status !== "Not Applicable").length} />
        </div>
      </section>
    </div>
  );
}

function RawAlertsTab({ caseId, alerts, onAction }: { caseId: number; alerts: AlertRecord[]; onAction: (fn: () => Promise<unknown>, success: string) => Promise<void> }) {
  const [raw, setRaw] = useState("");
  const [source, setSource] = useState("Generic");
  const [file, setFile] = useState<File | null>(null);

  function paste(event: FormEvent) {
    event.preventDefault();
    void onAction(() => api.pasteAlert(caseId, raw, source), "Alert parsed. IOCs, timeline, and tasks were updated.").then(() => setRaw(""));
  }

  function upload(event: FormEvent) {
    event.preventDefault();
    if (!file) return;
    void onAction(() => api.uploadAlert(caseId, file), "Alert file uploaded and parsed.").then(() => setFile(null));
  }

  return (
    <div className="grid gap-4 xl:grid-cols-2">
      <section className="rounded-lg border border-line bg-panel p-4">
        <h2 className="font-semibold text-white">Paste alert</h2>
        <form onSubmit={paste} className="mt-3 space-y-3">
          <input value={source} onChange={(event) => setSource(event.target.value)} className="w-full rounded border border-line bg-night px-3 py-2 text-white" placeholder="Source system" />
          <textarea value={raw} onChange={(event) => setRaw(event.target.value)} className="min-h-64 w-full rounded border border-line bg-night px-3 py-2 font-mono text-sm text-white" placeholder="Paste raw alert, JSON, CSV, Windows event text, WAF log, Proofpoint alert..." required />
          <button className="rounded-md bg-sky-500 px-4 py-2 font-semibold text-white hover:bg-sky-400">Parse alert</button>
        </form>
        <form onSubmit={upload} className="mt-5 flex flex-wrap items-center gap-3 border-t border-line pt-4">
          <input type="file" accept=".json,.csv,.txt,.log" onChange={(event) => setFile(event.target.files?.[0] ?? null)} className="text-sm text-slate-300" />
          <button className="rounded-md border border-line px-3 py-2 text-sm text-slate-100 hover:bg-white/5">Upload file</button>
        </form>
      </section>
      <section className="space-y-3">
        {alerts.map((alert) => (
          <article key={alert.id} className="rounded-lg border border-line bg-panel p-4">
            <div className="flex items-center justify-between gap-3 text-sm">
              <span className="font-semibold text-white">{alert.source_system ?? "Unknown source"} · {alert.alert_type}</span>
              <span className="text-slate-400">{new Date(alert.created_at).toLocaleString()}</span>
            </div>
            <pre className="mt-3 max-h-52 overflow-auto rounded border border-line bg-night p-3 text-xs text-slate-200">{alert.raw_content}</pre>
          </article>
        ))}
      </section>
    </div>
  );
}

function TimelineTab({ caseId, timeline, onAction }: { caseId: number; timeline: TimelineEvent[]; onAction: (fn: () => Promise<unknown>, success: string) => Promise<void> }) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [eventType, setEventType] = useState("Analyst Observation");

  function submit(event: FormEvent) {
    event.preventDefault();
    void onAction(
      () => api.createTimeline(caseId, { timestamp: new Date().toISOString(), event_type: eventType, short_title: title, description, confidence: 0.9 }),
      "Timeline event added."
    ).then(() => {
      setTitle("");
      setDescription("");
    });
  }

  return (
    <div className="grid gap-4 xl:grid-cols-[360px,1fr]">
      <form onSubmit={submit} className="rounded-lg border border-line bg-panel p-4">
        <h2 className="font-semibold text-white">Add timeline event</h2>
        <input value={eventType} onChange={(event) => setEventType(event.target.value)} className="mt-3 w-full rounded border border-line bg-night px-3 py-2 text-white" />
        <input value={title} onChange={(event) => setTitle(event.target.value)} placeholder="Short title" className="mt-3 w-full rounded border border-line bg-night px-3 py-2 text-white" required />
        <textarea value={description} onChange={(event) => setDescription(event.target.value)} placeholder="Description" className="mt-3 min-h-32 w-full rounded border border-line bg-night px-3 py-2 text-white" required />
        <button className="mt-3 rounded-md bg-sky-500 px-4 py-2 font-semibold text-white">Add event</button>
      </form>
      <div className="space-y-3">
        {timeline.map((event) => (
          <article key={event.id} className="rounded-lg border border-line bg-panel p-4">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h3 className="font-semibold text-white">{event.short_title}</h3>
              <span className="text-xs text-slate-400">{new Date(event.timestamp).toLocaleString()}</span>
            </div>
            <div className="mt-1 text-xs text-sky-200">{event.event_type} · confidence {(event.confidence * 100).toFixed(0)}%</div>
            <p className="mt-2 text-sm text-slate-300">{event.description}</p>
          </article>
        ))}
      </div>
    </div>
  );
}

function IocsTab({ caseId, iocs, onAction }: { caseId: number; iocs: IOC[]; onAction: (fn: () => Promise<unknown>, success: string) => Promise<void> }) {
  return (
    <section className="rounded-lg border border-line bg-panel p-4">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="font-semibold text-white">Extracted IOCs</h2>
        <button onClick={() => onAction(() => api.enrichAll(caseId), "IOC enrichment completed.")} className="rounded-md bg-sky-500 px-3 py-2 text-sm font-semibold text-white">Enrich all</button>
      </div>
      <table className="w-full text-left text-sm">
        <thead className="text-slate-400"><tr><th className="py-2">Type</th><th>Value</th><th>Raw</th></tr></thead>
        <tbody>
          {iocs.map((ioc) => (
            <tr key={ioc.id} className="border-t border-line">
              <td className="py-2 text-sky-200">{ioc.type}</td>
              <td className="font-mono text-slate-100">
                <button onClick={() => navigator.clipboard?.writeText(ioc.value)} className="hover:underline">{ioc.value}</button>
                {ioc.enrichments && ioc.enrichments.length > 0 && (
                  <div className="mt-2 space-y-1 font-sans text-xs text-slate-400">
                    {ioc.enrichments.slice(0, 3).map((enrichment) => (
                      <div key={enrichment.id}>
                        <span className="text-sky-200">{enrichment.provider_name}</span>: {enrichment.verdict} - {enrichment.summary}
                      </div>
                    ))}
                  </div>
                )}
              </td>
              <td className="font-mono text-slate-400">{ioc.raw_value}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

function EvidenceTab({ caseId, evidence, onAction }: { caseId: number; evidence: EvidenceRecord[]; onAction: (fn: () => Promise<unknown>, success: string) => Promise<void> }) {
  const [file, setFile] = useState<File | null>(null);
  const [description, setDescription] = useState("");

  async function download(item: EvidenceRecord) {
    const blob = await api.downloadEvidence(item.id);
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = item.file_name;
    link.click();
    URL.revokeObjectURL(url);
  }

  function submit(event: FormEvent) {
    event.preventDefault();
    if (!file) return;
    void onAction(() => api.uploadEvidence(caseId, file, description), "Evidence uploaded and hashed.").then(() => {
      setFile(null);
      setDescription("");
    });
  }

  return (
    <div className="space-y-4">
      <form onSubmit={submit} className="flex flex-wrap items-center gap-3 rounded-lg border border-line bg-panel p-4">
        <input type="file" accept=".txt,.csv,.json,.log,.png,.jpg,.jpeg,.pdf" onChange={(event) => setFile(event.target.files?.[0] ?? null)} className="text-sm text-slate-300" />
        <input value={description} onChange={(event) => setDescription(event.target.value)} placeholder="Description" className="min-w-72 rounded border border-line bg-night px-3 py-2 text-white" />
        <button className="rounded-md bg-sky-500 px-4 py-2 font-semibold text-white">Upload evidence</button>
      </form>
      <section className="overflow-hidden rounded-lg border border-line bg-panel">
        <table className="w-full text-left text-sm">
          <thead className="bg-white/5 text-slate-300"><tr><th className="p-3">File</th><th>SHA256</th><th>Size</th><th>Actions</th></tr></thead>
          <tbody>
            {evidence.map((item) => (
              <tr key={item.id} className="border-t border-line">
                <td className="p-3 text-slate-100">{item.file_name}<div className="text-xs text-slate-500">{item.description}</div></td>
                <td className="max-w-sm truncate font-mono text-xs text-slate-400">{item.sha256}</td>
                <td className="text-slate-300">{formatBytes(item.size_bytes)}</td>
                <td className="space-x-2">
                  <button onClick={() => download(item)} className="text-sky-200 hover:underline">Download</button>
                  <button onClick={() => onAction(() => api.deleteEvidence(item.id), "Evidence deleted. Metadata remains audit-traceable.")} className="text-red-200 hover:underline">Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}

function MitreTab({ caseId, mappings, onAction }: { caseId: number; mappings: MitreMapping[]; onAction: (fn: () => Promise<unknown>, success: string) => Promise<void> }) {
  return (
    <section className="rounded-lg border border-line bg-panel p-4">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="font-semibold text-white">Suggested ATT&CK mappings</h2>
        <button onClick={() => onAction(() => api.suggestMitre(caseId), "MITRE suggestions refreshed.")} className="rounded-md bg-sky-500 px-3 py-2 text-sm font-semibold text-white">Suggest mappings</button>
      </div>
      <div className="space-y-3">
        {mappings.map((mapping) => (
          <article key={mapping.id} className="rounded border border-line bg-night p-3">
            <div className="flex flex-wrap justify-between gap-2">
              <div className="font-semibold text-white">{mapping.technique?.technique_id ?? mapping.technique_id} {mapping.technique?.technique_name ?? "Technique"}</div>
              <span className="text-xs text-sky-200">{mapping.analyst_status} · {(mapping.confidence * 100).toFixed(0)}%</span>
            </div>
            <div className="mt-1 text-xs text-slate-400">{mapping.technique?.tactic}</div>
            <p className="mt-2 text-sm text-slate-300">{mapping.why_suggested}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

function TasksTab({ tasks, onAction }: { tasks: TaskRecord[]; onAction: (fn: () => Promise<unknown>, success: string) => Promise<void> }) {
  return (
    <section className="rounded-lg border border-line bg-panel p-4">
      <h2 className="font-semibold text-white">Investigation tasks</h2>
      <div className="mt-3 space-y-3">
        {tasks.map((task) => (
          <article key={task.id} className="rounded border border-line bg-night p-3">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <div className="font-semibold text-white">{task.title}</div>
                <p className="mt-1 text-sm text-slate-400">{task.description}</p>
              </div>
              <select value={task.status} onChange={(event) => onAction(() => api.updateTask(task.id, { status: event.target.value }), "Task updated.")} className="rounded border border-line bg-panel px-2 py-1 text-sm text-white">
                {["Open", "In Progress", "Blocked", "Done", "Not Applicable"].map((item) => <option key={item}>{item}</option>)}
              </select>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function NotesTab({ caseId, notes, onAction }: { caseId: number; notes: NoteRecord[]; onAction: (fn: () => Promise<unknown>, success: string) => Promise<void> }) {
  const [body, setBody] = useState("");
  function submit(event: FormEvent) {
    event.preventDefault();
    void onAction(() => api.createNote(caseId, body), "Note added.").then(() => setBody(""));
  }
  return (
    <div className="grid gap-4 xl:grid-cols-[380px,1fr]">
      <form onSubmit={submit} className="rounded-lg border border-line bg-panel p-4">
        <h2 className="font-semibold text-white">Analyst note</h2>
        <textarea value={body} onChange={(event) => setBody(event.target.value)} className="mt-3 min-h-40 w-full rounded border border-line bg-night px-3 py-2 text-white" required />
        <button className="mt-3 rounded-md bg-sky-500 px-4 py-2 font-semibold text-white">Add note</button>
      </form>
      <div className="space-y-3">
        {notes.map((note) => (
          <article key={note.id} className="rounded-lg border border-line bg-panel p-4">
            <div className="text-xs text-slate-500">{new Date(note.created_at).toLocaleString()}</div>
            <p className="mt-2 whitespace-pre-wrap text-sm text-slate-200">{note.body}</p>
          </article>
        ))}
      </div>
    </div>
  );
}

function ReportsTab({ caseId, reports, onAction }: { caseId: number; reports: ReportRecord[]; onAction: (fn: () => Promise<unknown>, success: string) => Promise<void> }) {
  const [type, setType] = useState("analyst");
  const [format, setFormat] = useState("markdown");
  return (
    <div className="space-y-4">
      <section className="flex flex-wrap items-center gap-3 rounded-lg border border-line bg-panel p-4">
        <select value={type} onChange={(event) => setType(event.target.value)} className="rounded border border-line bg-night px-3 py-2 text-white">
          {["analyst", "ticket", "director", "false_positive"].map((item) => <option key={item}>{item}</option>)}
        </select>
        <select value={format} onChange={(event) => setFormat(event.target.value)} className="rounded border border-line bg-night px-3 py-2 text-white">
          {["markdown", "html"].map((item) => <option key={item}>{item}</option>)}
        </select>
        <button onClick={() => onAction(() => api.generateReport(caseId, type, format), "Report generated.")} className="rounded-md bg-sky-500 px-4 py-2 font-semibold text-white">Generate report</button>
      </section>
      {reports.map((report) => (
        <article key={report.id} className="rounded-lg border border-line bg-panel p-4">
          <div className="mb-3 flex items-center justify-between text-sm">
            <span className="font-semibold text-white">{report.report_type} · {report.format}</span>
            <button onClick={() => navigator.clipboard?.writeText(report.content)} className="text-sky-200 hover:underline">Copy</button>
          </div>
          <pre className="max-h-96 overflow-auto rounded border border-line bg-night p-3 text-xs text-slate-200">{report.content}</pre>
        </article>
      ))}
    </div>
  );
}

function AuditTab({ audit }: { audit: AuditLogRecord[] }) {
  return (
    <section className="overflow-hidden rounded-lg border border-line bg-panel">
      <table className="w-full text-left text-sm">
        <thead className="bg-white/5 text-slate-300"><tr><th className="p-3">Time</th><th>Action</th><th>Actor</th><th>Entity</th></tr></thead>
        <tbody>
          {audit.map((row) => (
            <tr key={row.id} className="border-t border-line">
              <td className="p-3 text-slate-400">{new Date(row.created_at).toLocaleString()}</td>
              <td className="text-slate-100">{row.action}</td>
              <td className="text-slate-300">{row.actor_id ?? "system"}</td>
              <td className="text-slate-400">{row.entity_type ?? "-"} {row.entity_id ?? ""}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-slate-500">{label}</dt>
      <dd className="mt-1 break-words text-slate-200">{value}</dd>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded border border-line bg-night p-3">
      <div className="text-xs text-slate-500">{label}</div>
      <div className="mt-1 text-2xl font-semibold text-white">{value}</div>
    </div>
  );
}

function formatBytes(value: number) {
  if (value < 1024) return `${value} B`;
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`;
  return `${(value / 1024 / 1024).toFixed(1)} MB`;
}
