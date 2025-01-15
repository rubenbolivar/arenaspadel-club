/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          light: '#a4bdbd', // gris verdoso claro
          DEFAULT: '#017f97', // azul verdoso
        },
        secondary: {
          DEFAULT: '#4c3f78', // morado oscuro
          light: '#6f63a8', // morado claro
        }
      }
    },
  },
  plugins: [],
}

