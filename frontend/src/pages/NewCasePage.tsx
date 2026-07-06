import { FormEvent, useState } from "react";
import { api } from "../api/client";
import type { CaseRecord, Severity } from "../types/models";

export function NewCasePage({ onCreated }: { onCreated: (caseRecord: CaseRecord) => void }) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [severity, setSeverity] = useState<Severity>("Medium");
  const [source, setSource] = useState("Generic");

  async function submit(event: FormEvent) {
    event.preventDefault();
    const created = await api.createCase({ title, description, severity, source_system: source });
    onCreated(created);
  }

  return (
    <form onSubmit={submit} className="max-w-3xl space-y-4 rounded-lg border border-line bg-panel p-5">
      <h1 className="text-2xl font-semibold text-white">New case</h1>
      <input value={title} onChange={(event) => setTitle(event.target.value)} placeholder="Case title" className="w-full rounded border border-line bg-night px-3 py-2 text-white" required />
      <textarea value={description} onChange={(event) => setDescription(event.target.value)} placeholder="Initial description" className="min-h-36 w-full rounded border border-line bg-night px-3 py-2 text-white" />
      <div className="grid gap-4 md:grid-cols-2">
        <select value={severity} onChange={(event) => setSeverity(event.target.value as Severity)} className="rounded border border-line bg-night px-3 py-2 text-white">
          {["Informational", "Low", "Medium", "High", "Critical"].map((item) => <option key={item}>{item}</option>)}
        </select>
        <input value={source} onChange={(event) => setSource(event.target.value)} className="rounded border border-line bg-night px-3 py-2 text-white" />
      </div>
      <button className="rounded-md bg-sky-500 px-4 py-2 font-semibold text-white hover:bg-sky-400">Create</button>
    </form>
  );
}

