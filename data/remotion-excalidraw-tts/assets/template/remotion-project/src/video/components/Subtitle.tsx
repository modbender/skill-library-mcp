import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';

export const Subtitle: React.FC<{text: string; from: number; to: number}> = ({
  text,
  from,
  to,
}) => {
  const frame = useCurrentFrame();
  const inT = interpolate(frame, [from, from + 10], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const outT = interpolate(frame, [to - 10, to], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const opacity = Math.min(inT, outT);

  return (
    <AbsoluteFill style={{justifyContent: 'flex-end', alignItems: 'center'}}>
      <div
        style={{
          marginBottom: 72,
          maxWidth: 1500,
          padding: '20px 26px',
          borderRadius: 18,
          background: 'rgba(0,0,0,0.55)',
          border: '1px solid rgba(255,255,255,0.15)',
          color: 'white',
          fontSize: 40,
          lineHeight: 1.25,
          fontWeight: 600,
          opacity,
          transform: `translateY(${(1 - opacity) * 18}px)`,
        }}
      >
        {text}
      </div>
    </AbsoluteFill>
  );
};
