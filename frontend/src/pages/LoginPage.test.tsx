import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { LoginPage } from "./LoginPage";

vi.mock("../api/client", () => ({
  api: { login: vi.fn(), me: vi.fn() },
  setToken: vi.fn()
}));

describe("LoginPage", () => {
  it("renders the local authentication form", () => {
    render(<LoginPage onLogin={vi.fn()} />);
    expect(screen.getByText("Security Alert Case Builder")).toBeInTheDocument();
    expect(screen.getByLabelText("Email")).toBeInTheDocument();
    expect(screen.getByLabelText("Password")).toBeInTheDocument();
  });
});
