
/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                void: {
                    DEFAULT: '#050505',
                    panel: '#0a0a0a',
                    surface: '#111111',
                },
                cyan: {
                    DEFAULT: '#00f0ff',
                    dim: '#00f0ff20', // 20% opacity
                },
                bio: {
                    DEFAULT: '#bd00ff',
                    dim: '#bd00ff20',
                },
                amber: {
                    DEFAULT: '#ffae00',
                }
            },
            fontFamily: {
                mono: ['JetBrains Mono', 'Space Mono', 'monospace'],
                sans: ['Inter', 'sans-serif'],
            },
            animation: {
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'scanline': 'scanline 8s linear infinite',
            },
            keyframes: {
                scanline: {
                    '0%': { transform: 'translateY(-100%)' },
                    '100%': { transform: 'translateY(100%)' },
                }
            }
        },
    },
    plugins: [],
}
