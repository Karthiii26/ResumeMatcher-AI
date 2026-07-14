/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        heading: ['"Space Grotesk"', 'sans-serif'],
        body:    ['"DM Sans"',       'sans-serif'],
      },
      colors: {
        navy: {
          50:  '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          600: '#1e3a5f',
          700: '#162d4a',
          800: '#0f2040',
          900: '#0a1628',
        },
        accent: '#2563EB',
      },
      keyframes: {
        'fade-up': {
          '0%':   { opacity: '0', transform: 'translateY(18px)' },
          '100%': { opacity: '1', transform: 'translateY(0)'    },
        },
        'fade-in': {
          '0%':   { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'scale-in': {
          '0%':   { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)'    },
        },
        dash: {
          '0%':   { strokeDashoffset: '339' },
          '100%': { strokeDashoffset: 'var(--target-offset)' },
        },
      },
      animation: {
        'fade-up':  'fade-up  0.45s ease-out both',
        'fade-in':  'fade-in  0.3s  ease-out both',
        'scale-in': 'scale-in 0.35s ease-out both',
        'dash':     'dash     1.2s  ease-out forwards',
      },
    },
  },
  plugins: [],
}
