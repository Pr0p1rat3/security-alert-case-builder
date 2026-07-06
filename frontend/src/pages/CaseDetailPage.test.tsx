import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { api } from "../api/client";
import { CaseDetailPage } from "./CaseDetailPage";

vi.mock("../api/client", () => ({
  api: {
    caseDetail: vi.fn().mockResolvedValue({
      id: 10,
      title: "Suspicious PowerShell",
      description: "Endpoint alert triage",
      severity: "High",
      status: "New",
      source_system: "Sophos",
      created_by_id: 1,
      created_at: "2026-07-02T12:00:00Z",
      updated_at: "2026-07-02T12:00:00Z"
    }),
    alerts: vi.fn().mockResolvedValue([]),
    iocs: vi.fn().mockResolvedValue([]),
    timeline: vi.fn().mockResolvedValue([]),
    mitre: vi.fn().mockResolvedValue([]),
    tasks: vi.fn().mockResolvedValue([]),
    evidence: vi.fn().mockResolvedValue([]),
    notes: vi.fn().mockResolvedValue([]),
    reports: vi.fn().mockResolvedValue([]),
    audit: vi.fn().mockResolvedValue([]),
    pasteAlert: vi.fn().mockResolvedValue({ id: 1 })
  }
}));

describe("CaseDetailPage", () => {
  it("renders tabs and sends pasted alert text to the API", async () => {
    render(<CaseDetailPage caseId={10} onBack={vi.fn()} />);
    expect(await screen.findByText(/CASE-10 Suspicious PowerShell/)).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Raw Alerts" }));
    fireEvent.change(screen.getByPlaceholderText(/Paste raw alert/), { target: { value: "source_ip=203.0.113.10" } });
    fireEvent.click(screen.getByRole("button", { name: "Parse alert" }));

    await waitFor(() => {
      expect(api.pasteAlert).toHaveBeenCalledWith(10, "source_ip=203.0.113.10", "Generic");
    });
  });
});
