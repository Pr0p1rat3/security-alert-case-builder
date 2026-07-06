import { ClipboardList, LayoutDashboard, Search, Settings, ShieldAlert } from "lucide-react";
import type { ReactNode } from "react";
import type { User } from "../types/models";

interface ShellProps {
  user: User;
  current: string;
  onNavigate: (page: string) => void;
  onLogout: () => void;
  children: ReactNode;
}

const nav = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { id: "cases", label: "Cases", icon: ClipboardList },
  { id: "search", label: "Search", icon: Search },
  { id: "admin", label: "Admin", icon: Settings }
];

export function Shell({ user, current, onNavigate, onLogout, children }: ShellProps) {
  return (
    <div className="min-h-screen">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-line bg-panel/90 p-4 lg:block">
        <div className="mb-8 flex items-center gap-3">
          <ShieldAlert className="h-7 w-7 text-accent" />
          <div>
            <div className="font-semibold text-white">Security Alert</div>
            <div className="text-sm text-slate-400">Case Builder</div>
          </div>
        </div>
        <nav className="space-y-2">
          {nav.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`flex w-full items-center gap-3 rounded-md px-3 py-2 text-left text-sm ${
                  current === item.id ? "bg-sky-500/15 text-sky-200" : "text-slate-300 hover:bg-white/5"
                }`}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </button>
            );
          })}
        </nav>
      </aside>
      <main className="lg:pl-64">
        <header className="sticky top-0 z-10 flex items-center justify-between border-b border-line bg-night/85 px-5 py-3 backdrop-blur">
          <div>
            <div className="text-sm text-slate-400">Signed in as</div>
            <div className="font-medium text-white">{user.display_name} · {user.role}</div>
          </div>
          <button onClick={onLogout} className="rounded-md border border-line px-3 py-2 text-sm text-slate-200 hover:bg-white/5">
            Logout
          </button>
        </header>
        <section className="p-5">{children}</section>
      </main>
    </div>
  );
}

