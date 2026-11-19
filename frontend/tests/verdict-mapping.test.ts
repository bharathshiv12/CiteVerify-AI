import { describe, it, expect } from "vitest";
import {
  VERDICT_CONFIGS,
  NULL_VERDICT_CONFIG,
  EVIDENCE_LEVEL_CONFIG,
  CITATION_STATUS_CONFIG,
} from "../lib/constants/verdicts";
import { VerificationVerdict, EvidenceLevel } from "../types";

describe("Verdict and Evidence Level Mapping", () => {
  it("defines configs for all five canonical verification verdicts", () => {
    const verdicts: VerificationVerdict[] = [
      "SUPPORTED",
      "PARTLY_SUPPORTED",
      "UNSUPPORTED",
      "CONTRADICTORY",
      "POTENTIALLY_OUTDATED",
    ];

    verdicts.forEach((v) => {
      const config = VERDICT_CONFIGS[v];
      expect(config).toBeDefined();
      expect(config.label).toBeTruthy();
      expect(config.badgeBg).toBeTruthy();
      expect(config.badgeText).toBeTruthy();
      expect(config.iconName).toBeTruthy();
    });
  });

  it("handles null verdict honestly without coercing to Unsupported", () => {
    expect(NULL_VERDICT_CONFIG.label).toBe("Needs Human Review");
    expect(NULL_VERDICT_CONFIG.label).not.toBe("Unsupported");
    expect(NULL_VERDICT_CONFIG.iconName).toBe("HelpCircle");
  });

  it("distinguishes abstracts from full text strictly", () => {
    expect(EVIDENCE_LEVEL_CONFIG.FULL_TEXT.isFullText).toBe(true);
    expect(EVIDENCE_LEVEL_CONFIG.ABSTRACT_ONLY.isFullText).toBe(false);
    expect(EVIDENCE_LEVEL_CONFIG.METADATA_ONLY.isFullText).toBe(false);
    expect(EVIDENCE_LEVEL_CONFIG.NONE.isFullText).toBe(false);

    expect(EVIDENCE_LEVEL_CONFIG.ABSTRACT_ONLY.label).toBe("Abstract Only");
    expect(EVIDENCE_LEVEL_CONFIG.FULL_TEXT.label).toBe("Full Text");
  });

  it("provides full citation mapping statuses", () => {
    expect(CITATION_STATUS_CONFIG.MATCHED.label).toBe("Matched");
    expect(CITATION_STATUS_CONFIG.PARTIALLY_MATCHED.label).toBe("Partially Matched");
    expect(CITATION_STATUS_CONFIG.UNMATCHED.label).toBe("Unmatched");
    expect(CITATION_STATUS_CONFIG.MISSING_REFERENCE.label).toBe("Missing Reference");
  });
});
