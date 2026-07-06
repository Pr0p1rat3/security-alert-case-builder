/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        night: "#0b1117",
        panel: "#111a24",
        line: "#243244",
        accent: "#38bdf8"
      }
    }
  },
  plugins: []
};

