import { VerificationVerdict, EvidenceLevel, RetrievalStatus } from "../../types";

export interface VerdictConfig {
  label: string;
  badgeBg: string;
  badgeText: string;
  iconName: string;
  description: string;
}

export const VERDICT_CONFIGS: Record<VerificationVerdict, VerdictConfig> = {
  SUPPORTED: {
    label: "Supported",
    badgeBg: "bg-[#E4F1EA] dark:bg-[#1E3A2E]",
    badgeText: "text-[#1F5A42] dark:text-[#6EE7B7]",
    iconName: "CheckCircle2",
    description: "Claim is factually substantiated by cited research evidence.",
  },
  PARTLY_SUPPORTED: {
    label: "Partially Supported",
    badgeBg: "bg-[#F7EBCF] dark:bg-[#3D2E14]",
    badgeText: "text-[#7A5A14] dark:text-[#FCD34D]",
    iconName: "AlertTriangle",
    description: "Evidence partially aligns but contains nuances or qualified scope.",
  },
  UNSUPPORTED: {
    label: "Unsupported",
    badgeBg: "bg-[#F6E1E1] dark:bg-[#3D1A1A]",
    badgeText: "text-[#8F2E2E] dark:text-[#FCA5A5]",
    iconName: "XCircle",
    description: "Cited evidence does not validate the asserted factual claim.",
  },
  CONTRADICTORY: {
    label: "Contradictory",
    badgeBg: "bg-[#EDE3F3] dark:bg-[#2D1B38]",
    badgeText: "text-[#54346B] dark:text-[#D8B4FE]",
    iconName: "AlertOctagon",
    description: "Evidence directly opposes or refutes the asserted factual claim.",
  },
  POTENTIALLY_OUTDATED: {
    label: "Potentially Outdated",
    badgeBg: "bg-[#F8E7D2] dark:bg-[#382618]",
    badgeText: "text-[#8A5214] dark:text-[#FDBA74]",
    iconName: "Clock",
    description: "Subsequent research may supersede or qualify original findings.",
  },
};

export const NULL_VERDICT_CONFIG: VerdictConfig = {
  label: "Needs Human Review",
  badgeBg: "bg-[#ECE8E4] dark:bg-[#38332E]",
  badgeText: "text-[#4F4943] dark:text-[#D1CBC5]",
  iconName: "HelpCircle",
  description:
    "Insufficient retrieved evidence; human verification is required before forming a conclusion.",
};

export type CitationMatchStatus =
  | "MATCHED"
  | "PARTIALLY_MATCHED"
  | "UNMATCHED"
  | "MISSING_REFERENCE";

export interface CitationStatusConfigItem {
  label: string;
  badgeBg: string;
  badgeText: string;
  iconName: string;
  description: string;
}

export const CITATION_STATUS_CONFIG: Record<CitationMatchStatus, CitationStatusConfigItem> = {
  MATCHED: {
    label: "Matched",
    badgeBg: "bg-emerald-50 dark:bg-emerald-950/40",
    badgeText: "text-emerald-800 dark:text-emerald-300",
    iconName: "CheckCircle2",
    description: "Citation matched to an external scholarly publication.",
  },
  PARTIALLY_MATCHED: {
    label: "Partially Matched",
    badgeBg: "bg-amber-50 dark:bg-amber-950/40",
    badgeText: "text-amber-800 dark:text-amber-300",
    iconName: "AlertTriangle",
    description: "Partial publication metadata matched.",
  },
  UNMATCHED: {
    label: "Unmatched",
    badgeBg: "bg-stone-100 dark:bg-stone-800",
    badgeText: "text-stone-700 dark:text-stone-300",
    iconName: "XCircle",
    description: "No publication found for this citation.",
  },
  MISSING_REFERENCE: {
    label: "Missing Reference",
    badgeBg: "bg-rose-50 dark:bg-rose-950/40",
    badgeText: "text-rose-800 dark:text-rose-300",
    iconName: "HelpCircle",
    description: "Citation marker has no matching bibliography entry.",
  },
};

export interface EvidenceLevelConfigItem {
  isFullText: boolean;
  label: string;
  badge: string;
}

export const EVIDENCE_LEVEL_CONFIG: Record<EvidenceLevel, EvidenceLevelConfigItem> = {
  FULL_TEXT: {
    isFullText: true,
    label: "Full Text",
    badge: "bg-emerald-50 text-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-300",
  },
  ABSTRACT_ONLY: {
    isFullText: false,
    label: "Abstract Only",
    badge: "bg-amber-50 text-amber-800 dark:bg-amber-950/40 dark:text-amber-300",
  },
  METADATA_ONLY: {
    isFullText: false,
    label: "Metadata Only",
    badge: "bg-blue-50 text-blue-800 dark:bg-blue-950/40 dark:text-blue-300",
  },
  NONE: {
    isFullText: false,
    label: "None",
    badge: "bg-stone-100 text-stone-700 dark:bg-stone-800 dark:text-stone-300",
  },
};

export interface RetrievalStatusConfigItem {
  label: string;
  badge: string;
}

export const RETRIEVAL_STATUS_CONFIG: Record<RetrievalStatus, RetrievalStatusConfigItem> = {
  RETRIEVED: {
    label: "Retrieved",
    badge: "bg-emerald-50 text-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-300",
  },
  NOT_FOUND: {
    label: "Not Found",
    badge: "bg-stone-100 text-stone-700 dark:bg-stone-800 dark:text-stone-300",
  },
  PAYWALLED: {
    label: "Paywalled",
    badge: "bg-amber-50 text-amber-800 dark:bg-amber-950/40 dark:text-amber-300",
  },
  API_ERROR: {
    label: "API Error",
    badge: "bg-rose-50 text-rose-800 dark:bg-rose-950/40 dark:text-rose-300",
  },
};

export type ConfidenceTier = "HIGH" | "MEDIUM" | "LOW";

export function getConfidenceTier(confidence: number): ConfidenceTier {
  if (confidence >= 0.75) return "HIGH";
  if (confidence >= 0.50) return "MEDIUM";
  return "LOW";
}

export const CONFIDENCE_CONFIG: Record<
  ConfidenceTier,
  { label: string; bgClass: string; textClass: string; tooltip: string }
> = {
  HIGH: {
    label: "High Confidence",
    bgClass: "bg-[#E4F1EA] dark:bg-[#1E3A2E]",
    textClass: "text-[#1F5A42] dark:text-[#6EE7B7]",
    tooltip:
      "Confidence reflects how strong the retrieved evidence is. It does not guarantee the claim is true or false.",
  },
  MEDIUM: {
    label: "Medium Confidence",
    bgClass: "bg-[#F7EBCF] dark:bg-[#3D2E14]",
    textClass: "text-[#7A5A14] dark:text-[#FCD34D]",
    tooltip:
      "Confidence reflects how strong the retrieved evidence is. It does not guarantee the claim is true or false.",
  },
  LOW: {
    label: "Low Confidence",
    bgClass: "bg-[#ECE8E4] dark:bg-[#2A2420]",
    textClass: "text-[#4F4943] dark:text-[#D1CBC5]",
    tooltip:
      "Confidence reflects how strong the retrieved evidence is. It does not guarantee the claim is true or false.",
  },
};
