'use client'

export default function Logo({ size = 'default' }: { size?: 'small' | 'default' }) {
  const iconSize = size === 'small' ? 'w-6 h-6' : 'w-8 h-8'
  const textSize = size === 'small' ? 'text-lg' : 'text-xl'

  return (
    <div className="flex items-center gap-2.5">
      {/* 3D Box Icon */}
      <div className={`${iconSize} relative`}>
        <svg
          viewBox="0 0 32 32"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="w-full h-full"
        >
          {/* Back face */}
          <path
            d="M8 8L16 4L24 8L16 12L8 8Z"
            fill="white"
            fillOpacity="0.3"
          />
          {/* Left face */}
          <path
            d="M8 8L8 20L16 24L16 12L8 8Z"
            fill="white"
            fillOpacity="0.6"
          />
          {/* Right face */}
          <path
            d="M24 8L24 20L16 24L16 12L24 8Z"
            fill="white"
            fillOpacity="0.9"
          />
          {/* Top highlight line */}
          <path
            d="M8 8L16 12L24 8"
            stroke="white"
            strokeWidth="0.5"
            strokeOpacity="0.5"
          />
          {/* Bottom edges */}
          <path
            d="M8 20L16 24L24 20"
            stroke="white"
            strokeWidth="0.5"
            strokeOpacity="0.3"
          />
        </svg>
      </div>

      {/* Text */}
      <span className={`${textSize} font-semibold tracking-tight text-white`}>
        OpenClawdy
      </span>
    </div>
  )
}
