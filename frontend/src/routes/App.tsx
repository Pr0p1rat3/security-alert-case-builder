import { useEffect, useState } from "react";
import { api, clearToken } from "../api/client";
import { Shell } from "../components/Shell";
import { AdminPage } from "../pages/AdminPage";
import { CaseDetailPage } from "../pages/CaseDetailPage";
import { CasesPage } from "../pages/CasesPage";
import { DashboardPage } from "../pages/DashboardPage";
import { LoginPage } from "../pages/LoginPage";
import { NewCasePage } from "../pages/NewCasePage";
import { SearchPage } from "../pages/SearchPage";
import type { User } from "../types/models";

type Page = "dashboard" | "cases" | "new-case" | "case-detail" | "search" | "admin";

export function App() {
  const [user, setUser] = useState<User | null>(null);
  const [page, setPage] = useState<Page>("dashboard");
  const [caseId, setCaseId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .me()
      .then(setUser)
      .catch(() => clearToken())
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="p-8 text-slate-300">Loading workspace...</div>;
  }

  if (!user) {
    return <LoginPage onLogin={(nextUser) => setUser(nextUser)} />;
  }

  function openCase(id: number) {
    setCaseId(id);
    setPage("case-detail");
  }

  function logout() {
    clearToken();
    setUser(null);
  }

  let content = <DashboardPage />;
  if (page === "cases") content = <CasesPage onOpen={openCase} onNew={() => setPage("new-case")} />;
  if (page === "new-case") content = <NewCasePage onCreated={(record) => openCase(record.id)} />;
  if (page === "case-detail" && caseId) content = <CaseDetailPage caseId={caseId} onBack={() => setPage("cases")} />;
  if (page === "search") content = <SearchPage />;
  if (page === "admin") content = <AdminPage currentUser={user} />;

  return (
    <Shell user={user} current={page === "new-case" || page === "case-detail" ? "cases" : page} onNavigate={(next) => setPage(next as Page)} onLogout={logout}>
      {content}
    </Shell>
  );
}
