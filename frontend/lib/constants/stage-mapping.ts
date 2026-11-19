import { PipelineStage } from "../../types";

export interface WorkflowStageDef {
  step: number;
  slug: string;
  title: string;
  shortTitle: string;
}

export const WORKFLOW_STAGES: WorkflowStageDef[] = [
  { step: 1, slug: "upload", title: "Upload Document", shortTitle: "Upload" },
  { step: 2, slug: "extract", title: "Extract Claims", shortTitle: "Extract" },
  { step: 3, slug: "map", title: "Map Citations", shortTitle: "Map Citations" },
  { step: 4, slug: "retrieve", title: "Retrieve Research", shortTitle: "Retrieve" },
  { step: 5, slug: "compare", title: "Compare Evidence", shortTitle: "Compare" },
  { step: 6, slug: "verify", title: "Verify & Report", shortTitle: "Verify" },
];

export function getStageStep(stage: PipelineStage | string): number {
  if (stage === "UPLOADED") return 1;
  if (
    [
      "TEXT_EXTRACTION",
      "CLAIM_EXTRACTION",
      "CITATION_PARSING",
      "REFERENCE_PARSING",
    ].includes(stage)
  ) {
    return 2;
  }
  if (stage === "CITATION_MATCHING") return 3;
  if (stage === "PAPER_RETRIEVAL") return 4;
  if (stage === "EVIDENCE_EXTRACTION") return 5;
  if (["VERIFICATION", "REPORT_GENERATION", "DONE"].includes(stage)) return 6;
  return 1;
}

export function isStageReached(
  backendStage: PipelineStage | string,
  step: number
): boolean {
  return getStageStep(backendStage) >= step;
}
