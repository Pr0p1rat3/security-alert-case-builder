import type { Severity } from "../types/models";

const colors: Record<Severity, string> = {
  Informational: "border-slate-500 bg-slate-900 text-slate-200",
  Low: "border-emerald-500 bg-emerald-950 text-emerald-200",
  Medium: "border-amber-500 bg-amber-950 text-amber-200",
  High: "border-orange-500 bg-orange-950 text-orange-200",
  Critical: "border-red-500 bg-red-950 text-red-200"
};

export function SeverityBadge({ severity }: { severity: Severity }) {
  return <span className={`rounded border px-2 py-1 text-xs font-semibold ${colors[severity]}`}>{severity}</span>;
}

