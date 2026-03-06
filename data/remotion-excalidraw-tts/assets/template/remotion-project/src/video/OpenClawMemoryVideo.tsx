import React, {useEffect, useMemo, useState} from 'react';
import {
  AbsoluteFill,
  Audio,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {DiagramStage} from './components/DiagramStage';
import {FocusOverlay} from './components/FocusOverlay';
import {Subtitle} from './components/Subtitle';
import {makeStoryboard, storyboardFromJson, type Scene} from './storyboard/storyboard';

export const OpenClawMemoryVideo: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps, width, height} = useVideoConfig();

  const fallbackStoryboard = useMemo(() => makeStoryboard({fps, width, height}), [fps, width, height]);
  const [storyboard, setStoryboard] = useState<Scene[] | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch(staticFile('storyboard.json'));
        if (!res.ok) {
          setStoryboard(null);
          return;
        }
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const json = (await res.json()) as any;
        const sb = storyboardFromJson(json, fps);
        if (!cancelled) setStoryboard(sb);
      } catch {
        setStoryboard(null);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [fps]);

  const effective = storyboard ?? fallbackStoryboard;
  const active = effective.find((s) => frame >= s.from && frame < s.to) ?? effective[effective.length - 1];

  const t = Math.min(1, Math.max(0, (frame - active.from) / Math.max(1, active.to - active.from)));
  const ease = spring({fps, frame: frame - active.from, config: {damping: 18, stiffness: 110}});

  const scale = interpolate(ease, [0, 1], [active.cameraFrom.scale, active.cameraTo.scale]);
  const x = interpolate(ease, [0, 1], [active.cameraFrom.x, active.cameraTo.x]);
  const y = interpolate(ease, [0, 1], [active.cameraFrom.y, active.cameraTo.y]);

  return (
    <AbsoluteFill style={{backgroundColor: '#0B1020'}}>
      <Audio src={staticFile('voiceover.mp3')} />

      <DiagramStage
        srcUrl={staticFile('diagram.excalidraw')}
        camera={{x, y, scale}}
        // Slight vignette for a “story” feel
        vignette
      />

      {active.focus ? <FocusOverlay {...active.focus} progress={t} /> : null}

      {active.subtitle ? (
        <Subtitle
          text={active.subtitle}
          from={active.from}
          to={active.to}
        />
      ) : null}
    </AbsoluteFill>
  );
};
