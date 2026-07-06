import { useEffect, useState } from "react";
import { api } from "../api/client";
import { SeverityBadge } from "../components/SeverityBadge";
import type { CaseRecord } from "../types/models";

export function CasesPage({ onOpen, onNew }: { onOpen: (id: number) => void; onNew: () => void }) {
  const [cases, setCases] = useState<CaseRecord[]>([]);

  useEffect(() => {
    api.cases().then(setCases).catch(console.error);
  }, []);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-white">Cases</h1>
        <button onClick={onNew} className="rounded-md bg-sky-500 px-4 py-2 font-semibold text-white hover:bg-sky-400">New case</button>
      </div>
      <div className="overflow-hidden rounded-lg border border-line bg-panel">
        <table className="w-full text-left text-sm">
          <thead className="bg-white/5 text-slate-300">
            <tr><th className="p-3">Case</th><th>Severity</th><th>Status</th><th>Source</th><th>Updated</th></tr>
          </thead>
          <tbody>
            {cases.map((item) => (
              <tr key={item.id} className="border-t border-line hover:bg-white/5">
                <td className="p-3"><button onClick={() => onOpen(item.id)} className="text-sky-200 hover:underline">CASE-{item.id} {item.title}</button></td>
                <td><SeverityBadge severity={item.severity} /></td>
                <td className="text-slate-300">{item.status}</td>
                <td className="text-slate-300">{item.source_system ?? "-"}</td>
                <td className="text-slate-400">{new Date(item.updated_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

