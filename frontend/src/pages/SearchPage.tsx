import { FormEvent, useState } from "react";
import { api } from "../api/client";

export function SearchPage() {
  const [q, setQ] = useState("");
  const [results, setResults] = useState<Record<string, any>>({});

  async function submit(event: FormEvent) {
    event.preventDefault();
    setResults(await api.search(q));
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold text-white">Search</h1>
      <form onSubmit={submit} className="flex gap-2">
        <input value={q} onChange={(event) => setQ(event.target.value)} className="flex-1 rounded border border-line bg-night px-3 py-2 text-white" placeholder="Case title, IOC, username, hostname, raw alert text" />
        <button className="rounded-md bg-sky-500 px-4 py-2 text-white">Search</button>
      </form>
      <pre className="overflow-auto rounded-lg border border-line bg-panel p-4 text-sm text-slate-200">{JSON.stringify(results, null, 2)}</pre>
    </div>
  );
}

