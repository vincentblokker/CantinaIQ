import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#1F1B16",
        "ink-2": "#5A4F44",
        cream: "#FAF7F2",
        tuscan: "#8B3A2F",
        leaf: "#4A6B36",
        sea: "#1F3A5F",
      },
      fontFamily: {
        serif: ['"Source Serif 4"', "Georgia", "serif"],
      },
    },
  },
  plugins: [],
} satisfies Config;
