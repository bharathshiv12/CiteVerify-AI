import { describe, it, expect } from "vitest";
import {
  WORKFLOW_STAGES,
  getStageStep,
  isStageReached,
} from "../lib/constants/stage-mapping";

describe("6-Stage Pipeline Mapping", () => {
  it("defines exactly 6 sequential workflow stages", () => {
    expect(WORKFLOW_STAGES).toHaveLength(6);
    expect(WORKFLOW_STAGES.map((s) => s.step)).toEqual([1, 2, 3, 4, 5, 6]);
    expect(WORKFLOW_STAGES.map((s) => s.slug)).toEqual([
      "upload",
      "extract",
      "map",
      "retrieve",
      "compare",
      "verify",
    ]);
  });

  it("maps backend PipelineStages to the correct step", () => {
    expect(getStageStep("UPLOADED")).toBe(1);
    expect(getStageStep("TEXT_EXTRACTION")).toBe(2);
    expect(getStageStep("CLAIM_EXTRACTION")).toBe(2);
    expect(getStageStep("CITATION_PARSING")).toBe(2);
    expect(getStageStep("REFERENCE_PARSING")).toBe(2);
    expect(getStageStep("CITATION_MATCHING")).toBe(3);
    expect(getStageStep("PAPER_RETRIEVAL")).toBe(4);
    expect(getStageStep("EVIDENCE_EXTRACTION")).toBe(5);
    expect(getStageStep("VERIFICATION")).toBe(6);
    expect(getStageStep("REPORT_GENERATION")).toBe(6);
    expect(getStageStep("DONE")).toBe(6);
  });

  it("evaluates forward navigation gates correctly", () => {
    // When backend is at CITATION_MATCHING (step 3), step 1, 2, 3 are reachable, 4, 5, 6 are not
    expect(isStageReached("CITATION_MATCHING", 1)).toBe(true);
    expect(isStageReached("CITATION_MATCHING", 2)).toBe(true);
    expect(isStageReached("CITATION_MATCHING", 3)).toBe(true);
    expect(isStageReached("CITATION_MATCHING", 4)).toBe(false);
    expect(isStageReached("CITATION_MATCHING", 5)).toBe(false);
    expect(isStageReached("CITATION_MATCHING", 6)).toBe(false);

    // When backend is DONE (step 6), all steps are reached
    expect(isStageReached("DONE", 6)).toBe(true);
  });
});
