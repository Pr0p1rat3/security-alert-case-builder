import { useEffect, useState } from "react";
import { api } from "../api/client";

export function DashboardPage() {
  const [summary, setSummary] = useState<Record<string, any>>({});

  useEffect(() => {
    api.dashboard().then(setSummary).catch(console.error);
  }, []);

  const severity = summary.open_cases_by_severity ?? {};
  const status = summary.cases_by_status ?? {};

  return (
    <div className="space-y-5">
      <h1 className="text-2xl font-semibold text-white">Dashboard</h1>
      <div className="grid gap-4 md:grid-cols-4">
        {["Critical", "High", "Medium", "Low"].map((item) => (
          <article key={item} className="rounded-lg border border-line bg-panel p-4">
            <div className="text-sm text-slate-400">{item} cases</div>
            <div className="mt-2 text-3xl font-semibold tabular text-white">{severity[item] ?? 0}</div>
          </article>
        ))}
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <Panel title="Cases by status" rows={Object.entries(status).map(([label, value]) => ({ label, value }))} />
        <Panel title="Top observed IOCs" rows={(summary.top_iocs ?? []).map((item: any) => ({ label: item.value, value: item.count }))} />
      </div>
    </div>
  );
}

function Panel({ title, rows }: { title: string; rows: { label: string; value: unknown }[] }) {
  return (
    <section className="rounded-lg border border-line bg-panel p-4">
      <h2 className="mb-3 font-semibold text-white">{title}</h2>
      <div className="space-y-2">
        {rows.length === 0 && <div className="text-sm text-slate-400">No data</div>}
        {rows.map((row) => (
          <div key={row.label} className="flex items-center justify-between rounded border border-line bg-night px-3 py-2 text-sm">
            <span className="truncate text-slate-200">{row.label}</span>
            <span className="tabular text-sky-200">{String(row.value)}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

