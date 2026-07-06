import { FormEvent, useState } from "react";
import { api, setToken } from "../api/client";
import type { User } from "../types/models";

export function LoginPage({ onLogin }: { onLogin: (user: User) => void }) {
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("ChangeMe123!");
  const [error, setError] = useState("");

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      const token = await api.login(email, password);
      setToken(token.access_token);
      onLogin(await api.me());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <form onSubmit={submit} className="w-full max-w-md rounded-lg border border-line bg-panel p-6 shadow-2xl">
        <h1 className="text-2xl font-semibold text-white">Security Alert Case Builder</h1>
        <p className="mt-2 text-sm text-slate-400">Internal defensive triage workspace</p>
        <label htmlFor="email" className="mt-6 block text-sm text-slate-300">Email</label>
        <input id="email" value={email} onChange={(event) => setEmail(event.target.value)} className="mt-2 w-full rounded-md border border-line bg-night px-3 py-2 text-white" />
        <label htmlFor="password" className="mt-4 block text-sm text-slate-300">Password</label>
        <input id="password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} className="mt-2 w-full rounded-md border border-line bg-night px-3 py-2 text-white" />
        {error && <div className="mt-4 rounded border border-red-500 bg-red-950 p-3 text-sm text-red-200">{error}</div>}
        <button className="mt-6 w-full rounded-md bg-sky-500 px-4 py-2 font-semibold text-white hover:bg-sky-400">Login</button>
      </form>
    </div>
  );
}
