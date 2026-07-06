import { FormEvent, useEffect, useState } from "react";
import { api } from "../api/client";
import type { Role, User } from "../types/models";

export function AdminPage({ currentUser }: { currentUser: User }) {
  const [users, setUsers] = useState<User[]>([]);
  const [error, setError] = useState("");
  const [email, setEmail] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<Role>("Analyst");

  async function load() {
    setError("");
    try {
      setUsers(await api.users());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load users");
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    await api.createUser({ email, display_name: displayName, password, role });
    setEmail("");
    setDisplayName("");
    setPassword("");
    setRole("Analyst");
    await load();
  }

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-semibold text-white">Admin</h1>
        <p className="mt-1 text-sm text-slate-400">User management for local JWT authentication. Future OIDC/SAML/LDAP can attach here.</p>
      </div>
      {currentUser.role !== "Admin" && <div className="rounded-md border border-amber-500 bg-amber-950 p-3 text-sm text-amber-100">Admin role is required for user changes.</div>}
      {error && <div className="rounded-md border border-red-500 bg-red-950 p-3 text-sm text-red-100">{error}</div>}
      <section className="rounded-lg border border-line bg-panel p-4">
        <h2 className="font-semibold text-white">Create user</h2>
        <form onSubmit={submit} className="mt-4 grid gap-3 lg:grid-cols-5">
          <input value={email} onChange={(event) => setEmail(event.target.value)} placeholder="Email" className="rounded border border-line bg-night px-3 py-2 text-white" required />
          <input value={displayName} onChange={(event) => setDisplayName(event.target.value)} placeholder="Display name" className="rounded border border-line bg-night px-3 py-2 text-white" required />
          <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Temporary password" className="rounded border border-line bg-night px-3 py-2 text-white" required />
          <select value={role} onChange={(event) => setRole(event.target.value as Role)} className="rounded border border-line bg-night px-3 py-2 text-white">
            {["Admin", "Analyst", "Viewer"].map((item) => <option key={item}>{item}</option>)}
          </select>
          <button className="rounded-md bg-sky-500 px-4 py-2 font-semibold text-white hover:bg-sky-400">Add user</button>
        </form>
      </section>
      <section className="overflow-hidden rounded-lg border border-line bg-panel">
        <table className="w-full text-left text-sm">
          <thead className="bg-white/5 text-slate-300">
            <tr><th className="p-3">Email</th><th>Name</th><th>Role</th></tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id} className="border-t border-line">
                <td className="p-3 text-slate-100">{user.email}</td>
                <td className="text-slate-300">{user.display_name}</td>
                <td className="text-sky-200">{user.role}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
