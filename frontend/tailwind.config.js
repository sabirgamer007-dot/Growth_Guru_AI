/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: '#0F172A',
        surface: '#1E293B',
        sidebar: '#111827',
        primary: '#22C55E',
        'primary-hover': '#1BAF54',
        secondary: '#F59E0B',
        danger: '#EF4444',
        'text-main': '#F8FAFC',
        'text-muted': '#94A3B8',
        border: 'rgba(255, 255, 255, 0.08)',
      },
      borderRadius: {
        card: '8px',
        button: '6px',
      },
      fontFamily: {
        sans: ['Inter', 'Plus Jakarta Sans', 'Manrope', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        'h1': ['24px', { lineHeight: '1.2', fontWeight: '600' }],
        'h2': ['18px', { lineHeight: '1.3', fontWeight: '500' }],
        'kpi': ['32px', { lineHeight: '1.1', fontWeight: '700' }],
        'body': ['14px', { lineHeight: '1.45', fontWeight: '400' }],
        'small': ['12px', { lineHeight: '1.4', fontWeight: '500' }],
      },
      spacing: {
        'xxs': '4px',
        'xs': '8px',
        'sm': '16px',
        'md': '24px',
        'lg': '32px',
        'xl': '48px',
      },
      width: {
        'sidebar': '250px',
      },
      height: {
        'topnav': '64px',
      },
    },
  },
  plugins: [],
}
