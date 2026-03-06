/* eslint-disable @typescript-eslint/no-explicit-any */
import React, {useEffect, useMemo, useState} from 'react';
import {AbsoluteFill} from 'remotion';
import {Excalidraw} from '@excalidraw/excalidraw';

type Camera = {x: number; y: number; scale: number};

type ExcalidrawFile = {
  type?: string;
  version?: number;
  source?: string;
  // We only need to pass-through the JSON; keep it unknown to satisfy lint.
  elements: unknown[];
  appState?: Record<string, unknown>;
  files?: Record<string, unknown>;
};

export const DiagramStage: React.FC<{
  srcUrl: string;
  camera: Camera;
  vignette?: boolean;
}> = ({srcUrl, camera, vignette}) => {
  const [data, setData] = useState<ExcalidrawFile | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const res = await fetch(srcUrl);
      const json = (await res.json()) as ExcalidrawFile;
      if (!cancelled) setData(json);
    })();
    return () => {
      cancelled = true;
    };
  }, [srcUrl]);

  // Excalidraw doesn't like changing references too often
  const initialData = useMemo(() => {
    if (!data) return null;
    return {
      elements: data.elements as any,
      appState: {
        ...((data.appState ?? {}) as any),
        viewBackgroundColor: '#0B1020',
        zenModeEnabled: true,
        gridSize: null,
      },
      files: (data.files ?? {}) as any,
    };
  }, [data]);

  return (
    <AbsoluteFill>
      <AbsoluteFill
        style={{
          transform: `translate(${camera.x}px, ${camera.y}px) scale(${camera.scale})`,
          transformOrigin: '0 0',
        }}
      >
        {/* Excalidraw fills its container */}
        <div style={{width: 1920, height: 1080}}>
          {initialData ? (
            <Excalidraw
              initialData={initialData as any}
              viewModeEnabled
              zenModeEnabled
              theme="dark"
            />
          ) : null}
        </div>
      </AbsoluteFill>

      {vignette ? (
        <AbsoluteFill
          style={{
            background:
              'radial-gradient(ellipse at center, rgba(0,0,0,0) 45%, rgba(0,0,0,0.45) 100%)',
            pointerEvents: 'none',
          }}
        />
      ) : null}
    </AbsoluteFill>
  );
};
