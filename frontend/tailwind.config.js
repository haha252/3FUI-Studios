/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'gray-750': '#2d3748',
        'gray-850': '#1a202c',
        'gray-950': '#0d1117',
      }
    },
  },
  plugins: [],
}
