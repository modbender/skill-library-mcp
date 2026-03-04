import React from 'react';
import {AbsoluteFill, interpolate} from 'remotion';

export type Focus = {
  x: number;
  y: number;
  width: number;
  height: number;
  radius?: number;
  dim?: number; // 0..1
  label?: string;
};

export const FocusOverlay: React.FC<Focus & {progress: number}> = ({
  x,
  y,
  width,
  height,
  radius = 28,
  dim = 0.55,
  label,
  progress,
}) => {
  const a = interpolate(progress, [0, 1], [0, 1]);

  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <svg width="100%" height="100%" viewBox="0 0 1920 1080" style={{opacity: a}}>
        <defs>
          <mask id="hole">
            <rect x="0" y="0" width="1920" height="1080" fill="white" />
            <rect
              x={x}
              y={y}
              width={width}
              height={height}
              rx={radius}
              ry={radius}
              fill="black"
            />
          </mask>
        </defs>
        <rect
          x="0"
          y="0"
          width="1920"
          height="1080"
          fill={`rgba(0,0,0,${dim})`}
          mask="url(#hole)"
        />
        <rect
          x={x}
          y={y}
          width={width}
          height={height}
          rx={radius}
          ry={radius}
          fill="transparent"
          stroke="rgba(255,255,255,0.75)"
          strokeWidth={3}
        />
      </svg>

      {label ? (
        <div
          style={{
            position: 'absolute',
            left: x,
            top: Math.max(24, y - 54),
            padding: '10px 14px',
            borderRadius: 999,
            background: 'rgba(15, 23, 42, 0.85)',
            border: '1px solid rgba(255,255,255,0.18)',
            color: 'white',
            fontSize: 28,
            fontWeight: 600,
            letterSpacing: 0.2,
          }}
        >
          {label}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};
