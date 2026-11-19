import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "var(--bg)",
        card: "var(--card)",
        primary: "var(--primary)",
        secondary: "var(--secondary)",
        highlight: "var(--highlight)",
        heading: "var(--heading)",
        border: "var(--border)",
        ink: "var(--ink)",
        "ink-muted": "var(--ink-muted)",
        "border-input": "var(--border-input)",
        focus: "var(--focus)",

        // Semantic verification colors
        verdict: {
          supported: "var(--verdict-supported)",
          "supported-bg": "var(--verdict-supported-bg)",
          "supported-text": "var(--verdict-supported-text)",

          partly: "var(--verdict-partly)",
          "partly-bg": "var(--verdict-partly-bg)",
          "partly-text": "var(--verdict-partly-text)",

          unsupported: "var(--verdict-unsupported)",
          "unsupported-bg": "var(--verdict-unsupported-bg)",
          "unsupported-text": "var(--verdict-unsupported-text)",

          contradictory: "var(--verdict-contradictory)",
          "contradictory-bg": "var(--verdict-contradictory-bg)",
          "contradictory-text": "var(--verdict-contradictory-text)",

          outdated: "var(--verdict-outdated)",
          "outdated-bg": "var(--verdict-outdated-bg)",
          "outdated-text": "var(--verdict-outdated-text)",

          review: "var(--verdict-review)",
          "review-bg": "var(--verdict-review-bg)",
          "review-text": "var(--verdict-review-text)",
        },
      },
      fontFamily: {
        heading: ["var(--font-manrope)", "Manrope", "sans-serif"],
        sans: ["var(--font-inter)", "Inter", "sans-serif"],
        mono: ["var(--font-mono)", "IBM Plex Mono", "monospace"],
      },
      borderRadius: {
        btn: "10px",
        input: "10px",
        card: "14px",
      },
      boxShadow: {
        brand: "0 1px 2px rgba(62,47,39,.06), 0 4px 12px rgba(62,47,39,.05)",
      },
    },
  },
  plugins: [],
};

export default config;
