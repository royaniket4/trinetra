/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'bg-primary': '#0B1020',
        'bg-secondary': '#111827',
        'bg-card': 'rgba(17, 24, 39, 0.75)',
        'neon-cyan': '#00E5FF',
        'electric-blue': '#3B82F6',
        'success': '#00FF88',
        'critical': '#FF3B3B',
        'warning': '#FFB020',
        'purple': '#8B5CF6',
      },
      fontFamily: {
        'heading': ['Orbitron', 'sans-serif'],
        'body': ['Inter', 'sans-serif'],
        'mono': ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'scan': 'scan 4s linear infinite',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px #00E5FF, 0 0 10px #00E5FF' },
          '100%': { boxShadow: '0 0 20px #00E5FF, 0 0 30px #00E5FF' },
        },
        scan: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' },
        },
      },
      backdropBlur: {
        'xs': '2px',
      },
    },
  },
  plugins: [],
}