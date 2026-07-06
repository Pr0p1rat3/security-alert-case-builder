import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DashboardPage } from "./DashboardPage";

vi.mock("../api/client", () => ({
  api: {
    dashboard: vi.fn().mockResolvedValue({
      open_cases_by_severity: { Critical: 1, High: 2 },
      cases_by_status: { New: 2 },
      top_iocs: [{ value: "203.0.113.10", count: 3 }]
    })
  }
}));

describe("DashboardPage", () => {
  it("renders dashboard cards and async summary data", async () => {
    render(<DashboardPage />);
    expect(screen.getByText("Dashboard")).toBeInTheDocument();
    expect(await screen.findByText("203.0.113.10")).toBeInTheDocument();
  });
});
