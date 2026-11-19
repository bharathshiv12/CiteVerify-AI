import React from "react";
import {
  CheckCircle2,
  AlertTriangle,
  XCircle,
  AlertOctagon,
  Clock,
  HelpCircle,
  FileText,
  BookOpen,
  Info,
  MinusCircle,
  Check,
  Lock,
  AlertCircle,
} from "lucide-react";
import {
  VerificationVerdict,
  EvidenceLevel,
  RetrievalStatus,
} from "../../types";
import {
  VERDICT_CONFIGS,
  NULL_VERDICT_CONFIG,
  CITATION_STATUS_CONFIG,
  CitationMatchStatus,
  EVIDENCE_LEVEL_CONFIG,
  RETRIEVAL_STATUS_CONFIG,
} from "../../lib/constants/verdicts";

interface VerdictBadgeProps {
  verdict: VerificationVerdict | null | undefined;
  size?: "sm" | "md";
  showDescriptionTooltip?: boolean;
  className?: string;
}

export function VerdictBadge({ verdict, size = "md", className = "" }: VerdictBadgeProps) {
  const config = verdict ? VERDICT_CONFIGS[verdict] : NULL_VERDICT_CONFIG;

  const iconMap: Record<string, React.ReactNode> = {
    CheckCircle2: <CheckCircle2 className={size === "sm" ? "w-3 h-3" : "w-3.5 h-3.5"} aria-hidden="true" />,
    AlertTriangle: <AlertTriangle className={size === "sm" ? "w-3 h-3" : "w-3.5 h-3.5"} aria-hidden="true" />,
    XCircle: <XCircle className={size === "sm" ? "w-3 h-3" : "w-3.5 h-3.5"} aria-hidden="true" />,
    AlertOctagon: <AlertOctagon className={size === "sm" ? "w-3 h-3" : "w-3.5 h-3.5"} aria-hidden="true" />,
    Clock: <Clock className={size === "sm" ? "w-3 h-3" : "w-3.5 h-3.5"} aria-hidden="true" />,
    HelpCircle: <HelpCircle className={size === "sm" ? "w-3 h-3" : "w-3.5 h-3.5"} aria-hidden="true" />,
  };

  const icon = iconMap[config.iconName] || iconMap.HelpCircle;
  const padding = size === "sm" ? "px-2 py-0.5 text-xs gap-1" : "px-2.5 py-1 text-xs font-semibold gap-1.5";

  return (
    <span
      className={`inline-flex items-center rounded-full border border-current/20 select-none ${config.badgeBg} ${config.badgeText} ${padding} ${className}`}
      title={config.description}
    >
      <span className="flex-shrink-0">{icon}</span>
      <span>{config.label}</span>
    </span>
  );
}

interface CitationBadgeProps {
  status: CitationMatchStatus;
  size?: "sm" | "md";
  className?: string;
}

export function CitationBadge({ status, size = "md", className = "" }: CitationBadgeProps) {
  const config = CITATION_STATUS_CONFIG[status] || CITATION_STATUS_CONFIG.UNMATCHED;

  const iconMap: Record<string, React.ReactNode> = {
    CheckCircle2: <CheckCircle2 className={size === "sm" ? "w-3 h-3" : "w-3.5 h-3.5"} aria-hidden="true" />,
    AlertTriangle: <AlertTriangle className={size === "sm" ? "w-3 h-3" : "w-3.5 h-3.5"} aria-hidden="true" />,
    XCircle: <XCircle className={size === "sm" ? "w-3 h-3" : "w-3.5 h-3.5"} aria-hidden="true" />,
    HelpCircle: <HelpCircle className={size === "sm" ? "w-3 h-3" : "w-3.5 h-3.5"} aria-hidden="true" />,
  };

  const icon = iconMap[config.iconName] || iconMap.HelpCircle;
  const padding = size === "sm" ? "px-2 py-0.5 text-xs gap-1" : "px-2.5 py-1 text-xs font-semibold gap-1.5";

  return (
    <span
      className={`inline-flex items-center rounded-full border border-current/20 select-none ${config.badgeBg} ${config.badgeText} ${padding} ${className}`}
      title={config.description}
    >
      <span className="flex-shrink-0">{icon}</span>
      <span>{config.label}</span>
    </span>
  );
}

interface EvidenceLevelBadgeProps {
  level: EvidenceLevel;
  className?: string;
}

export function EvidenceLevelBadge({ level, className = "" }: EvidenceLevelBadgeProps) {
  const config = EVIDENCE_LEVEL_CONFIG[level] || EVIDENCE_LEVEL_CONFIG.NONE;

  const icons: Record<EvidenceLevel, React.ReactNode> = {
    FULL_TEXT: <BookOpen className="w-3 h-3" aria-hidden="true" />,
    ABSTRACT_ONLY: <FileText className="w-3 h-3" aria-hidden="true" />,
    METADATA_ONLY: <Info className="w-3 h-3" aria-hidden="true" />,
    NONE: <MinusCircle className="w-3 h-3" aria-hidden="true" />,
  };

  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium border border-current/15 ${config.badge} ${className}`}
    >
      {icons[level]}
      <span>{config.label}</span>
    </span>
  );
}

interface RetrievalBadgeProps {
  status: RetrievalStatus;
  className?: string;
}

export function RetrievalBadge({ status, className = "" }: RetrievalBadgeProps) {
  const config = RETRIEVAL_STATUS_CONFIG[status] || RETRIEVAL_STATUS_CONFIG.NOT_FOUND;

  const icons: Record<RetrievalStatus, React.ReactNode> = {
    RETRIEVED: <Check className="w-3 h-3 text-emerald-600" aria-hidden="true" />,
    NOT_FOUND: <XCircle className="w-3 h-3 text-stone-500" aria-hidden="true" />,
    PAYWALLED: <Lock className="w-3 h-3 text-amber-600" aria-hidden="true" />,
    API_ERROR: <AlertCircle className="w-3 h-3 text-rose-600" aria-hidden="true" />,
  };

  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium border border-current/15 ${config.badge} ${className}`}
    >
      {icons[status]}
      <span>{config.label}</span>
    </span>
  );
}
