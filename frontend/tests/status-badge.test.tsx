import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import {
  VerdictBadge,
  CitationBadge,
  EvidenceLevelBadge,
  RetrievalBadge,
} from "../components/ui/status-badge";

describe("StatusBadge Component Tests", () => {
  it("renders Supported badge with icon and explicit text label", () => {
    const { container } = render(<VerdictBadge verdict="SUPPORTED" />);
    expect(screen.getByText("Supported")).toBeDefined();
    const svg = container.querySelector("svg");
    expect(svg).toBeDefined();
    expect(svg).not.toBeNull();
  });

  it("renders Partially Supported badge with icon and text", () => {
    render(<VerdictBadge verdict="PARTLY_SUPPORTED" />);
    expect(screen.getByText("Partially Supported")).toBeDefined();
  });

  it("renders Unsupported badge with icon and text", () => {
    render(<VerdictBadge verdict="UNSUPPORTED" />);
    expect(screen.getByText("Unsupported")).toBeDefined();
  });

  it("renders Contradictory badge with icon and text", () => {
    render(<VerdictBadge verdict="CONTRADICTORY" />);
    expect(screen.getByText("Contradictory")).toBeDefined();
  });

  it("renders Potentially Outdated badge with icon and text", () => {
    render(<VerdictBadge verdict="POTENTIALLY_OUTDATED" />);
    expect(screen.getByText("Potentially Outdated")).toBeDefined();
  });

  it("renders null verdict safely as Needs Human Review without coercing to Unsupported", () => {
    render(<VerdictBadge verdict={null} />);
    expect(screen.getByText("Needs Human Review")).toBeDefined();
    expect(screen.queryByText("Unsupported")).toBeNull();
  });

  it("renders CitationBadge with text label and icon", () => {
    render(<CitationBadge status="MATCHED" />);
    expect(screen.getByText("Matched")).toBeDefined();

    render(<CitationBadge status="MISSING_REFERENCE" />);
    expect(screen.getByText("Missing Reference")).toBeDefined();
  });

  it("renders EvidenceLevelBadge with text label", () => {
    render(<EvidenceLevelBadge level="ABSTRACT_ONLY" />);
    expect(screen.getByText("Abstract Only")).toBeDefined();
  });

  it("renders RetrievalBadge with text label", () => {
    render(<RetrievalBadge status="RETRIEVED" />);
    expect(screen.getByText("Retrieved")).toBeDefined();
  });
});
