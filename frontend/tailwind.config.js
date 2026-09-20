/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        space: {
          950: '#04070F',
          900: '#080E1E',
          850: '#0C152B',
          800: '#111E3A',
          750: '#152548',
          700: '#1C315E',
          600: '#284685',
        },
        tactical: {
          cyan: '#00E5FF',
          emerald: '#00E676',
          amber: '#FFB300',
          red: '#FF3355',
          purple: '#A855F7',
          blue: '#3B82F6',
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Menlo', 'Consolas', 'Courier New', 'monospace'],
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      boxShadow: {
        'hud-cyan': '0 0 15px -3px rgba(0, 229, 255, 0.25)',
        'hud-emerald': '0 0 15px -3px rgba(0, 230, 118, 0.25)',
        'hud-amber': '0 0 15px -3px rgba(255, 179, 0, 0.25)',
        'hud-red': '0 0 15px -3px rgba(255, 51, 85, 0.3)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 12s linear infinite',
      }
    },
  },
  plugins: [],
}
