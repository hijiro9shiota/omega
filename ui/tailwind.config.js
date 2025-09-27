/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"OryonRobot"', 'Inter', 'system-ui', 'sans-serif']
      },
      colors: {
        primary: {
          500: '#38bdf8',
          600: '#0ea5e9',
          700: '#0284c7'
        },
        accent: {
          500: '#a855f7',
          600: '#9333ea'
        }
      },
      boxShadow: {
        neon: '0 0 10px rgba(56, 189, 248, 0.35)',
        glass: '0 10px 40px rgba(15, 23, 42, 0.45)'
      }
    }
  },
  plugins: [require('@tailwindcss/forms')]
};
