/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      fontFamily: {
        'sans': ['Inter', '-apple-system', 'BlinkMacSystemFont', 'system-ui', 'sans-serif'],
        'serif': ['Playfair Display', 'Georgia', 'serif'],
      },
      colors: {
        // Deep Jewel Tones - Minimalist Chic Palette
        emerald: {
          DEFAULT: '#15796a',
          dark: '#0f5849',
          light: '#1a9080',
        },
        sapphire: {
          DEFAULT: '#2d5282',
          dark: '#1e3a5f',
          light: '#3d6ba5',
        },
        burgundy: {
          DEFAULT: '#8b3449',
          dark: '#6b2737',
          light: '#a84560',
        },
        gold: {
          DEFAULT: '#d4a574',
          light: '#e4c19a',
          dark: '#b8915f',
        },
        neutral: {
          50: '#fafafa',
          100: '#f5f5f5',
          200: '#e5e5e5',
          300: '#d4d4d4',
          400: '#a3a3a3',
          500: '#737373',
          600: '#525252',
          700: '#404040',
          800: '#262626',
          900: '#171717',
        },
      },
      boxShadow: {
        'elegant': '0 2px 8px rgba(0, 0, 0, 0.08)',
        'elegant-lg': '0 10px 25px rgba(0, 0, 0, 0.1)',
        'elegant-xl': '0 20px 40px rgba(0, 0, 0, 0.12)',
      },
    },
  },
  plugins: [],
};