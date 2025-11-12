import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Background hierarchy
        "bg-pure-black": "#000000",
        "bg-near-black": "#0A0A0A",
        "bg-elevated": "#141414",
        "bg-hover": "#1E1E1E",
        "bg-tooltip": "#282828",
        
        // Text colors
        "text-primary": "#E4E4E7",
        "text-secondary": "#A1A1AA",
        "text-tertiary": "#71717A",
        "text-white": "#FFFFFF",
        
        // Accent colors
        "accent-primary": "#3B82F6",
        "accent-hover": "#60A5FA",
        "accent-secondary": "#06B6D4",
        
        // Semantic colors
        "semantic-success": "#22C55E",
        "semantic-warning": "#F59E0B",
        "semantic-error": "#EF4444",
        "semantic-info": "#8B5CF6",
        
        // Borders
        "border-subtle": "rgba(255, 255, 255, 0.1)",
        "border-moderate": "rgba(255, 255, 255, 0.15)",
        "border-strong": "rgba(255, 255, 255, 0.2)",
        "border-accent": "#3B82F6",
      },
      fontFamily: {
        sans: ["Inter", "var(--font-geist-sans)", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "Courier New", "monospace"],
      },
      borderRadius: {
        sm: "8px",
        DEFAULT: "12px",
        md: "12px",
        lg: "16px",
        xl: "24px",
        full: "9999px",
      },
      boxShadow: {
        card: "0 0 0 1px rgba(255,255,255,0.05), 0 4px 12px rgba(0,0,0,0.5)",
        modal: "0 0 0 1px rgba(255,255,255,0.1), 0 8px 24px rgba(0,0,0,0.7)",
        "glow-accent": "0 0 20px rgba(59,130,246,0.5), 0 0 40px rgba(59,130,246,0.3)",
        "glow-subtle": "0 0 12px rgba(59,130,246,0.3)",
      },
      animation: {
        "pulse-glow": "pulse-glow 2s ease-in-out infinite",
      },
      keyframes: {
        "pulse-glow": {
          "0%, 100%": { opacity: "0.3" },
          "50%": { opacity: "0.5" },
        },
      },
    },
  },
  plugins: [],
};
export default config;
