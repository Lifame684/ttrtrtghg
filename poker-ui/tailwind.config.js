/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        pokerGreen: '#1a4a1a',
        pokerTable: '#2d5a27',
      }
    },
  },
  plugins: [],
}
