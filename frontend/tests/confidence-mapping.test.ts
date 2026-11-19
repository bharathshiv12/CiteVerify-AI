import { describe, it, expect } from "vitest";
import { getConfidenceTier, CONFIDENCE_CONFIG } from "../lib/constants/verdicts";

describe("Confidence Mapping and Thresholds", () => {
  it("maps confidence >= 0.75 to HIGH tier", () => {
    expect(getConfidenceTier(0.95)).toBe("HIGH");
    expect(getConfidenceTier(0.75)).toBe("HIGH");
  });

  it("maps confidence >= 0.50 and < 0.75 to MEDIUM tier", () => {
    expect(getConfidenceTier(0.749)).toBe("MEDIUM");
    expect(getConfidenceTier(0.60)).toBe("MEDIUM");
    expect(getConfidenceTier(0.50)).toBe("MEDIUM");
  });

  it("maps confidence < 0.50 to LOW tier", () => {
    expect(getConfidenceTier(0.499)).toBe("LOW");
    expect(getConfidenceTier(0.20)).toBe("LOW");
    expect(getConfidenceTier(0.0)).toBe("LOW");
  });

  it("provides honest explanation tooltip across all tiers", () => {
    const requiredTooltip =
      "Confidence reflects how strong the retrieved evidence is. It does not guarantee the claim is true or false.";
    expect(CONFIDENCE_CONFIG.HIGH.tooltip).toBe(requiredTooltip);
    expect(CONFIDENCE_CONFIG.MEDIUM.tooltip).toBe(requiredTooltip);
    expect(CONFIDENCE_CONFIG.LOW.tooltip).toBe(requiredTooltip);
  });
});
