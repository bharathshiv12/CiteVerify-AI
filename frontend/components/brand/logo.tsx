import React from "react";
import Link from "next/link";

interface LogoProps {
  iconOnly?: boolean;
  size?: "sm" | "md" | "lg";
  className?: string;
  withLink?: boolean;
}

export function Logo({ iconOnly = false, size = "md", className = "", withLink = true }: LogoProps) {
  const sizeMap = {
    sm: { icon: 24, text: "text-lg", sub: "text-[10px]" },
    md: { icon: 32, text: "text-xl", sub: "text-xs" },
    lg: { icon: 40, text: "text-2xl", sub: "text-sm" },
  };

  const { icon, text, sub } = sizeMap[size];

  const content = (
    <div className={`inline-flex items-center gap-2.5 select-none ${className}`}>
      {/* SVG Icon combining:
          1) Scientific document outline
          2) Citation bracket [ ]
          3) Verification check mark
      */}
      <svg
        width={icon}
        height={icon}
        viewBox="0 0 40 40"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="flex-shrink-0"
        aria-hidden="true"
      >
        {/* Document Outline with folded corner */}
        <path
          d="M10 6C8.89543 6 8 6.89543 8 8V32C8 33.1046 8.89543 34 10 34H30C31.1046 34 32 33.1046 32 32V14L24 6H10Z"
          fill="#FFF0D6"
          stroke="#8D6E63"
          strokeWidth="2"
          strokeLinejoin="round"
        />
        {/* Document Fold Corner */}
        <path
          d="M24 6V14H32"
          fill="#FFDCA8"
          stroke="#8D6E63"
          strokeWidth="2"
          strokeLinejoin="round"
        />
        {/* Citation Left Bracket '[' */}
        <path
          d="M13 14H11V26H13"
          stroke="#8D6E63"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        {/* Citation Right Bracket ']' */}
        <path
          d="M27 14H29V26H27"
          stroke="#8D6E63"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        {/* Verification Checkmark */}
        <path
          d="M16 20L19.5 23.5L25 17"
          stroke="#39765B"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        {/* Golden accent node */}
        <circle cx="20" cy="28.5" r="1.5" fill="#F4B860" />
      </svg>

      {!iconOnly && (
        <div className="flex flex-col leading-none">
          <span className={`font-extrabold tracking-tight text-[#8D6E63] dark:text-[#D7B8A8] ${text}`}>
            Cite<span className="text-[#3E2F27] dark:text-[#F3E9DD]">Verify</span>
            <span className="ml-1 text-xs px-1.5 py-0.5 rounded bg-[#F4B860] text-[#3E2F27] font-semibold tracking-normal uppercase">
              AI
            </span>
          </span>
          <span className={`text-[#7A685D] dark:text-[#B8A898] font-medium tracking-wide mt-0.5 ${sub}`}>
            Scientific Claim Verification
          </span>
        </div>
      )}
    </div>
  );

  if (withLink) {
    return (
      <Link href="/dashboard" className="focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8D6E63] rounded-lg">
        {content}
      </Link>
    );
  }

  return content;
}
