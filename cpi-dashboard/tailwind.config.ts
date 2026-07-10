import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: "#111827",
        muted: "#64748b",
        panel: "#ffffff",
        line: "#dbe3ef",
        wash: "#f7fafc",
        teal: "#0f766e",
        sky: "#2563eb",
        amber: "#b45309",
        rose: "#dc2626"
      },
      boxShadow: {
        subtle: "0 1px 2px rgba(15, 23, 42, 0.06)"
      }
    }
  },
  plugins: []
};

export default config;
