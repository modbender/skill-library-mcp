/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './public/**/*.html',
    './dashboard/dist/**/*.html',
    './public/assets/shared.js',
  ],
  theme: {
    extend: {
      fontFamily: {
        serif: ['Lora', 'Georgia', 'serif'],
        sans: ['Manrope', 'system-ui', 'sans-serif'],
        mono: ['DM Mono', 'monospace'],
      },
      colors: {
        warm: {
          50: '#FDFBF7',
          100: '#F8F4ED',
          200: '#F0EBE1',
          300: '#E3DDD1',
          400: '#A8A093',
          500: '#9A9285',
          600: '#8A8275',
          700: '#5C5347',
          800: '#3D362D',
          900: '#2A2520',
          950: '#1A1714',
        },
        sage: {
          400: '#68B078',
          500: '#4A9957',
          600: '#3A8548',
          700: '#2D6E3A',
          800: '#205A2D',
        },
      },
    },
  },
  plugins: [],
};
