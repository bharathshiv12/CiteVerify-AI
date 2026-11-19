import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ProgressTracker } from "../components/verification/progress-tracker";

describe("ProgressTracker Component", () => {
  it("renders all 6 workflow step labels", () => {
    render(
      <ProgressTracker
        documentId="doc-test-123"
        currentStageSlug="extract"
        backendStage="CLAIM_EXTRACTION"
      />
    );

    expect(screen.getAllByText("Upload").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Extract").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Map Citations").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Retrieve Research").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Compare Evidence").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Verify").length).toBeGreaterThan(0);
  });
});
