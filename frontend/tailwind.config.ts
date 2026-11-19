import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        supported: "#10b981",
        partly: "#f59e0b",
        unsupported: "#ef4444",
        contradictory: "#dc2626",
        outdated: "#8b5cf6",
      },
    },
  },
  plugins: [],
};
export default config;

