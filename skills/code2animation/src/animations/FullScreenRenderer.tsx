import React from 'react';
import { VideoClip } from '../types';
import { AnimationProps, AnimationResult } from './types';
import { buildTypedLines } from './AroundTitleRenderer';

export interface FullScreenResult extends AnimationResult {
    mediaLayers: Array<{ idx: number; opacity: number }>;
    underlineProgress: number;
}

export const footagesFullScreenAnimation = ({
    clip,
    currentTime,
    duration,
    isRendering,
}: AnimationProps): FullScreenResult => {
    const titleText = clip.title || '';
    const titleCharCount = titleText.replace(/\n/g, '').length;
    const typingStart = 0.15;
    const cps = titleCharCount > 0 ? Math.min(44, Math.max(16, titleCharCount / 1.1)) : 24;
    const visibleChars = titleCharCount > 0
        ? Math.max(0, Math.min(titleCharCount, Math.floor((currentTime - typingStart) * cps)))
        : 0;

    const typedLines = buildTypedLines(titleText, visibleChars);
    const isTyping = titleCharCount > 0 && visibleChars < titleCharCount && currentTime >= typingStart;
    const caretVisible = isTyping && (Math.floor((currentTime - typingStart) * 2) % 2 === 0);

    const mediaConfigs = clip.media || [];
    let mediaLayers: Array<{ idx: number; opacity: number }> = [];

    if (mediaConfigs.length === 0) {
        mediaLayers = [];
    } else if (duration <= 0) {
        mediaLayers = [{ idx: 0, opacity: 1 }];
    } else {
        const count = mediaConfigs.length;
        const segmentDuration = duration / count;
        const rawIndex = Math.floor(currentTime / segmentDuration);
        const idx = Math.max(0, Math.min(count - 1, rawIndex));

        if (count === 1) {
            mediaLayers = [{ idx, opacity: 1 }];
        } else {
            const tInSeg = currentTime - idx * segmentDuration;
            const crossfadeWindow = Math.min(0.8, Math.max(0.15, segmentDuration * 0.25));
            const fadeStart = segmentDuration - crossfadeWindow;

            if (idx < count - 1 && tInSeg >= fadeStart) {
                const p = Math.max(0, Math.min(1, (tInSeg - fadeStart) / crossfadeWindow));
                mediaLayers = [
                    { idx, opacity: 1 - p },
                    { idx: idx + 1, opacity: p }
                ];
            } else {
                mediaLayers = [{ idx, opacity: 1 }];
            }
        }
    }

    const underlineProgress = Math.max(0, Math.min(1, (currentTime - 0.4) / 0.8));

    return {
        typedLines,
        caretVisible,
        mediaLayers,
        underlineProgress,
    };
};

interface Props {
    data: FullScreenResult;
    clip: VideoClip;
}

export const FullScreenRenderer: React.FC<Props> = ({ data, clip }) => {
    const { typedLines, caretVisible, mediaLayers, underlineProgress } = data;

    return (
        <div className="relative w-full h-full flex items-center justify-center bg-transparent overflow-hidden">
            {/* Full Screen Media Background */}
            <div className="absolute inset-0 z-0">
                {clip.media && mediaLayers.map((layer: any) => {
                    const item = clip.media?.[layer.idx];
                    if (!item) return null;
                    const isHtml = item.src.toLowerCase().endsWith('.html');

                    return (
                        <div
                            key={`${layer.idx}-${item.src}`}
                            className="absolute inset-0 w-full h-full"
                            style={{
                                opacity: layer.opacity,
                            }}
                        >
                            {isHtml ? (
                                <iframe
                                    src={item.src}
                                    className="w-full h-full border-none"
                                    title={`media-${layer.idx}`}
                                />
                            ) : (
                                <img
                                    src={item.src}
                                    alt={`media-${layer.idx}`}
                                    className="w-full h-full object-cover"
                                />
                            )}
                        </div>
                    );
                })}
            </div>





            <div className="text-center z-30 relative">
                <div className="text-[12rem] font-black text-white mb-4 tracking-tighter leading-[0.8] mix-blend-difference drop-shadow-[0_10px_30px_rgba(0,0,0,0.5)] uppercase">
                    {typedLines.map((line: string, lineIdx: number) => {
                        const isLastLine = lineIdx === typedLines.length - 1;
                        return (
                            <div key={lineIdx}>
                                <span>{line.length > 0 ? line : '\u00A0'}</span>
                                {isLastLine && caretVisible && (
                                    <span
                                        aria-hidden="true"
                                        style={{
                                            display: 'inline-block',
                                            width: '0.08em',
                                            height: '0.85em',
                                            marginLeft: '0.08em',
                                            transform: 'translateY(0.05em)',
                                            background: 'currentColor',
                                            opacity: 0.9
                                        }}
                                    />
                                )}
                            </div>
                        );
                    })}
                </div>
                <div className="h-2 bg-[#00FF00] mb-8 mx-auto" style={{ width: `${underlineProgress * 100}%` }} />
            </div>
        </div>
    );
};
