/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "oklch(0.9 0.01 250)",
        input: "oklch(0.9 0.01 250)",
        ring: "oklch(0.52 0.19 250)",
        background: "oklch(0.99 0 0)",
        foreground: "oklch(0.15 0.01 250)",
        primary: {
          DEFAULT: "oklch(0.52 0.19 250)",
          foreground: "oklch(0.98 0.005 250)",
        },
        secondary: {
          DEFAULT: "oklch(0.96 0.01 250)",
          foreground: "oklch(0.15 0.01 250)",
        },
        destructive: {
          DEFAULT: "oklch(0.577 0.245 27.325)",
          foreground: "oklch(0.98 0.005 250)",
        },
        muted: {
          DEFAULT: "oklch(0.96 0.01 250)",
          foreground: "oklch(0.45 0.01 250)",
        },
        accent: {
          DEFAULT: "oklch(0.96 0.01 250)",
          foreground: "oklch(0.15 0.01 250)",
        },
        popover: {
          DEFAULT: "oklch(0.99 0 0)",
          foreground: "oklch(0.15 0.01 250)",
        },
        card: {
          DEFAULT: "oklch(0.99 0 0)",
          foreground: "oklch(0.15 0.01 250)",
        },
        // Estados de trabajo
        "status-pending": "oklch(0.7 0.15 40)",
        "status-progress": "oklch(0.6 0.19 250)",
        "status-completed": "oklch(0.6 0.15 160)",
        "status-urgent": "oklch(0.577 0.245 27.325)",
        // Sidebar
        sidebar: {
          DEFAULT: "oklch(0.98 0.005 250)",
          foreground: "oklch(0.2 0.01 250)",
          primary: "oklch(0.52 0.19 250)",
          accent: "oklch(0.94 0.01 250)",
          border: "oklch(0.88 0.01 250)",
        },
      },
      borderRadius: {
        lg: "0.5rem",
        md: "0.375rem",
        sm: "0.25rem",
      },
      fontFamily: {
        sans: ["var(--font-geist-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-geist-mono)", "monospace"],
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
