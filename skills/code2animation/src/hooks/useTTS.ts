import { useState, useEffect, useRef, useCallback } from 'react';
import { AudioAlignment, VideoClip } from '../types';

interface UseTTSProps {
  clip?: VideoClip;
  projectId?: string;
  clipIndex?: number;
  onWordBoundary?: (word: string) => void;
  onEnd?: () => void;
}

export function useTTS({ clip, projectId, clipIndex, onWordBoundary, onEnd }: UseTTSProps = {}) {
  const [alignment, setAlignment] = useState<AudioAlignment | null>(null);
  const [duration, setDuration] = useState(0);
  const [audio, setAudio] = useState<HTMLAudioElement | null>(null);
  const [isSpeaking, setIsSpeaking] = useState(false);

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const onWordBoundaryRef = useRef(onWordBoundary);
  const onEndRef = useRef(onEnd);
  const currentUrlRef = useRef<string | null>(null);

  useEffect(() => {
    onWordBoundaryRef.current = onWordBoundary;
    onEndRef.current = onEnd;
  }, [onWordBoundary, onEnd]);

  const stop = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    setIsSpeaking(false);
  }, []);

  const loadResource = useCallback(async (pId: string, cIdx: number, speech?: string, options?: { voice?: string }) => {
    let isMounted = true;
    let objectUrl: string | null = null;

    try {
      if (!speech || !speech.trim()) return null;
      const audioPath = `/audio/${pId}/${cIdx}.mp3`;
      const jsonPath = `/audio/${pId}/${cIdx}.json`;

      // 1. Try static
      const audioRes = await fetch(audioPath);
      if (audioRes.ok) {
        // ... existing static load logic
        const blob = await audioRes.blob();
        objectUrl = URL.createObjectURL(blob);
        const newAudio = new Audio(objectUrl);

        await new Promise((resolve) => {
          newAudio.onloadedmetadata = () => resolve(true);
          newAudio.onerror = () => resolve(false);
        });

        setDuration(newAudio.duration);
        setAudio(newAudio);
        audioRef.current = newAudio;
        currentUrlRef.current = objectUrl;

        const metaRes = await fetch(jsonPath);
        if (metaRes.ok) {
          const data = await metaRes.json();
          const parsedAlignment: AudioAlignment = {
            characters: [],
            character_start_times_seconds: [],
            character_end_times_seconds: []
          };

          if (Array.isArray(data)) {
            data.forEach((item: any) => {
              const entry = item.Metadata?.[0]?.Data || item;
              if (entry.Type === 'WordBoundary' || item.Type === 'WordBoundary') {
                const evt = entry.Type === 'WordBoundary' ? entry : item;
                const start = evt.Offset / 10000000;
                const dur = evt.Duration / 10000000;
                parsedAlignment.characters.push(evt.text?.Text || '');
                parsedAlignment.character_start_times_seconds.push(start);
                parsedAlignment.character_end_times_seconds.push(start + dur);
              }
            });
            setAlignment(parsedAlignment);

            newAudio.ontimeupdate = () => {
              if (onWordBoundaryRef.current) {
                const currentTime = newAudio.currentTime;
                const word = parsedAlignment.characters.find((_, i) => {
                  return currentTime >= parsedAlignment.character_start_times_seconds[i] &&
                    currentTime < parsedAlignment.character_end_times_seconds[i];
                });
                if (word) onWordBoundaryRef.current(word);
              }
            };
          }
        }

        newAudio.onended = () => {
          setIsSpeaking(false);
          onEndRef.current?.();
        };

        return newAudio;
      }

      // 2. Fallback
      const response = await fetch('/api/tts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: speech,
          voice: options?.voice
        }),
      });
      if (response.ok) {
        const blob = await response.blob();
        objectUrl = URL.createObjectURL(blob);
        const fallbackAudio = new Audio(objectUrl);
        await new Promise((resolve) => {
          fallbackAudio.onloadedmetadata = () => resolve(true);
          fallbackAudio.onerror = () => resolve(false);
        });
        setDuration(fallbackAudio.duration);
        setAudio(fallbackAudio);
        audioRef.current = fallbackAudio;
        currentUrlRef.current = objectUrl;

        fallbackAudio.onended = () => {
          setIsSpeaking(false);
          onEndRef.current?.();
        };
        return fallbackAudio;
      }
    } catch (e) {
      console.warn("Resource load failed", e);
    }
    return null;
  }, []);

  // Sync mode (for App.tsx)
  useEffect(() => {
    if (clip && projectId && clipIndex !== undefined) {
      if (!clip.speech || !clip.speech.trim()) {
        stop();
        setAlignment(null);
        setDuration(0);
        setAudio(null);
      } else {
        loadResource(projectId, clipIndex, clip.speech, {
          voice: clip.voice
        });
      }
    }
    return () => {
      stop();
      if (currentUrlRef.current) URL.revokeObjectURL(currentUrlRef.current);
    };
  }, [clip?.speech, projectId, clipIndex, loadResource, stop]);

  // Imperative mode (for user snippet compliance)
  const speak = useCallback(async (text: string, options?: { projectId?: string, stepIndex?: number }) => {
    stop();
    setIsSpeaking(true);
    const audioObj = await loadResource(
      options?.projectId || projectId || 'default',
      options?.stepIndex ?? clipIndex ?? 0,
      text
    );
    if (audioObj) {
      audioObj.play().catch(e => console.error("Speak failed", e));
    } else {
      setIsSpeaking(false);
    }
  }, [loadResource, stop, projectId, clipIndex]);

  return {
    alignment,
    duration,
    audio,
    isSpeaking,
    speak,
    stop
  };
}
