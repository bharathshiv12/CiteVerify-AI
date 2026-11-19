"use client";

import React from "react";
import Link from "next/link";
import { Check, ArrowRight } from "lucide-react";
import { PipelineStage } from "../../types";
import {
  WORKFLOW_STAGES,
  getStageStep,
  isStageReached,
} from "../../lib/constants/stage-mapping";

interface ProgressTrackerProps {
  documentId: string;
  currentStageSlug: string;
  backendStage: PipelineStage;
  className?: string;
}

export function ProgressTracker({
  documentId,
  currentStageSlug,
  backendStage,
  className = "",
}: ProgressTrackerProps) {
  const currentStepDef =
    WORKFLOW_STAGES.find((s) => s.slug === currentStageSlug) || WORKFLOW_STAGES[0];
  const currentStep = currentStepDef.step;
  const backendCurrentStep = getStageStep(backendStage);

  return (
    <div className={`w-full bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] rounded-[14px] p-4 sm:p-5 shadow-brand ${className}`}>
      {/* Mobile view: compact header + segmented bar */}
      <div className="sm:hidden">
        <div className="flex items-center justify-between text-xs mb-2">
          <span className="font-semibold text-[#8D6E63] dark:text-[#D7B8A8]">
            Stage {currentStep} of 6: <span className="text-[#3E2F27] dark:text-[#F3E9DD]">{currentStepDef.title}</span>
          </span>
          <span className="text-[11px] font-mono text-[#7A685D] dark:text-[#B8A898]">
            Backend: {backendStage}
          </span>
        </div>
        <div className="grid grid-cols-6 gap-1.5 h-2">
          {WORKFLOW_STAGES.map((s) => {
            const isCompleted = s.step < currentStep;
            const isCurrent = s.step === currentStep;
            const isAvailable = isStageReached(backendStage, s.step);

            let bg = "bg-[#F0E4D2] dark:bg-[#3D322A]";
            if (isCompleted) bg = "bg-[#39765B]";
            else if (isCurrent) bg = "bg-[#F4B860]";
            else if (isAvailable) bg = "bg-[#FFDCA8]";

            return <div key={s.slug} className={`rounded-full h-full ${bg}`} />;
          })}
        </div>
      </div>

      {/* Desktop view: 6-step horizontal linked tracker */}
      <nav aria-label="Verification progress" className="hidden sm:block">
        <ol className="flex items-center justify-between w-full">
          {WORKFLOW_STAGES.map((stage, idx) => {
            const isCompleted = stage.step < currentStep;
            const isCurrent = stage.step === currentStep;
            const isAvailable = isStageReached(backendStage, stage.step);
            const isClickable = isAvailable || isCompleted;

            const stepNode = (
              <div
                className={`flex items-center gap-2.5 ${
                  isClickable ? "cursor-pointer group" : "cursor-not-allowed opacity-50"
                }`}
                title={
                  isClickable
                    ? `Navigate to ${stage.title}`
                    : `Not reached yet. The system is currently on ${backendStage}.`
                }
              >
                {/* Step indicator circle */}
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all ${
                    isCompleted
                      ? "bg-[#39765B] text-white"
                      : isCurrent
                      ? "bg-[#F4B860] text-[#3E2F27] ring-4 ring-[#F4B860]/20 font-extrabold"
                      : isAvailable
                      ? "bg-[#FFDCA8] text-[#3E2F27]"
                      : "bg-[#F0E4D2] dark:bg-[#3D322A] text-[#7A685D] dark:text-[#B8A898]"
                  }`}
                >
                  {isCompleted ? <Check className="w-4 h-4 stroke-[3]" /> : stage.step}
                </div>
                {/* Step labels */}
                <div className="flex flex-col text-left">
                  <span
                    className={`text-xs font-semibold ${
                      isCurrent
                        ? "text-[#3E2F27] dark:text-[#F3E9DD] font-bold"
                        : "text-[#7A685D] dark:text-[#B8A898]"
                    }`}
                  >
                    {stage.shortTitle}
                  </span>
                  <span className="text-[10px] text-[#A08B78] dark:text-[#8C7A6A] leading-none mt-0.5">
                    {isCompleted ? "Done" : isCurrent ? "In Progress" : isAvailable ? "Ready" : "Pending"}
                  </span>
                </div>
              </div>
            );

            return (
              <React.Fragment key={stage.slug}>
                <li>
                  {isClickable ? (
                    <Link
                      href={`/verify/${documentId}/${stage.slug}`}
                      className="focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8D6E63] rounded-lg"
                    >
                      {stepNode}
                    </Link>
                  ) : (
                    stepNode
                  )}
                </li>
                {idx < WORKFLOW_STAGES.length - 1 && (
                  <li className="flex-1 mx-3" aria-hidden="true">
                    <div
                      className={`h-0.5 w-full rounded transition-colors ${
                        stage.step < backendCurrentStep
                          ? "bg-[#39765B]"
                          : stage.step === backendCurrentStep
                          ? "bg-[#F4B860]"
                          : "bg-[#F0E4D2] dark:bg-[#3D322A]"
                      }`}
                    />
                  </li>
                )}
              </React.Fragment>
            );
          })}
        </ol>
      </nav>
    </div>
  );
}
