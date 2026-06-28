/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        topology: {
          dark: "#0b101c",
          darker: "#070a13",
          darkest: "#04060c",
          border: "rgba(255,255,255,.2)",
          text: {
            primary: "#ffffff",
            secondary: "rgba(255,255,255,.5)",
            muted: "rgba(255,255,255,.4)",
          }
        }
      },
      fontFamily: {
        sans: ['-apple-system', '"Segoe UI"', 'system-ui', 'sans-serif'],
        mono: ['ui-monospace', '"Cascadia Code"', 'Consolas', 'monospace'],
      }
    },
  },
  plugins: [],
}
