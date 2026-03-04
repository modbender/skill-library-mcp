import { useState, useEffect, useMemo } from 'react';
import { VideoClip } from '../types';
import { footagesAroundTitleAnimation } from './AroundTitleRenderer';
import { footagesFullScreenAnimation } from './FullScreenRenderer';
import { normalizeToken } from './utils';

interface UseFootageClipProps {
    clip: VideoClip;
    currentTime: number;
    projectId: string;
    clipIndex: number;
    duration: number;
}

export const useFootageClip = ({
    clip,
    currentTime,
    projectId,
    clipIndex,
    duration
}: UseFootageClipProps) => {
    const [wordTimings, setWordTimings] = useState<Record<string, number>>({});
    const [isLoaded, setIsLoaded] = useState(false);

    // @ts-ignore
    const isRendering = typeof window !== 'undefined' && (window as any).suppressTTS === true;

    // Register with renderer
    useEffect(() => {
        if (!isRendering) return;
        // @ts-ignore
        if (typeof window.__registerComponent === 'function') {
            // @ts-ignore
            const unregister = window.__registerComponent('FootageClip');
            return () => unregister();
        }
    }, [isRendering]);

    useEffect(() => {
        if (!isRendering) return;
        // @ts-ignore
        window.__isReady_FootageClip = isLoaded;
    }, [isLoaded, isRendering]);

    // Fetch word timings (mainly for AroundTitle)
    useEffect(() => {
        if (clip.type !== 'footagesAroundTitle') {
            setIsLoaded(true);
            return;
        }

        setWordTimings({});
        if (projectId && clipIndex !== undefined) {
            if (isRendering) setIsLoaded(false);
            const fetchTimings = async () => {
                try {
                    const response = await fetch(`/audio/${projectId}/${clipIndex}.json`);
                    if (!response.ok) throw new Error('Failed to fetch timings');
                    const data = await response.json();
                    const timings: Record<string, number> = {};

                    data.forEach((item: any) => {
                        const entry = item.Metadata?.[0]?.Data || item;
                        if (entry.Type === 'WordBoundary' || item.Type === 'WordBoundary') {
                            const evt = entry.Type === 'WordBoundary' ? entry : item;
                            const textValue = normalizeToken(evt.text?.Text || evt.Text || '');
                            const offsetSeconds = evt.Offset / 10000000;
                            if (!textValue) return;
                            if (timings[textValue] === undefined || offsetSeconds < timings[textValue]) {
                                timings[textValue] = offsetSeconds;
                            }
                        }
                    });
                    setWordTimings(timings);
                    if (isRendering) setIsLoaded(true);
                } catch (e) {
                    console.warn('Word timings fetch failed', e);
                    setWordTimings({});
                    if (isRendering) setIsLoaded(true);
                }
            };
            fetchTimings();
        } else {
            if (isRendering) setIsLoaded(true);
        }
    }, [projectId, clipIndex, isRendering, clip.type]);

    // Orchestrate animation based on type
    const animationData = useMemo(() => {
        const props = { clip, currentTime, duration, wordTimings, isRendering };
        if (clip.type === 'footagesAroundTitle') {
            return { type: 'aroundTitle' as const, data: footagesAroundTitleAnimation(props) };
        } else if (clip.type === 'footagesFullScreen') {
            return { type: 'fullScreen' as const, data: footagesFullScreenAnimation(props) };
        }
        return null;
    }, [clip, currentTime, duration, wordTimings, isRendering]);

    return {
        animationData,
        isRendering
    };
};
