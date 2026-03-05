import React from 'react';
import './FootageClip.css';
import { VideoClip } from '../types';
import { AnimationProps, AnimationResult } from './types';
import { normalizeToken } from './utils';

export const buildTypedLines = (text: string, visibleChars: number) => {
    const lines: string[] = [''];
    let remaining = Math.max(0, visibleChars);

    for (let i = 0; i < text.length; i++) {
        const ch = text[i];
        if (ch === '\n') {
            lines.push('');
            continue;
        }
        if (remaining <= 0) break;
        lines[lines.length - 1] += ch;
        remaining -= 1;
    }

    return lines;
};

export interface AroundTitleResult extends AnimationResult {
    animState: 'visible' | 'exiting' | 'hidden';
    isContentVisible: boolean;
    mediaConfigs: Array<{
        finalDelay: number;
        isMediaVisible: boolean;
    }>;
}

export const footagesAroundTitleAnimation = ({
    clip,
    currentTime,
    duration,
    wordTimings,
    isRendering,
}: AnimationProps): AroundTitleResult => {

    let animState: 'visible' | 'exiting' | 'hidden' = 'visible';
    let isContentVisible = true;

    if (currentTime < 0.1) {
        animState = 'hidden';
        isContentVisible = false;
    } else if (currentTime < 0.6) {
        animState = 'visible';
        isContentVisible = true;
    } else if (currentTime > duration - 0.6) {
        animState = 'exiting';
        isContentVisible = false;
    } else {
        animState = 'visible';
        isContentVisible = true;
    }

    const titleText = clip.title || '';
    const titleCharCount = titleText.replace(/\n/g, '').length;
    const typingStart = 0.15;
    const cps = titleCharCount > 0 ? Math.min(40, Math.max(14, titleCharCount / 1.35)) : 20;
    const visibleChars = titleCharCount > 0
        ? Math.max(0, Math.min(titleCharCount, Math.floor((currentTime - typingStart) * cps)))
        : 0;

    const typedLines = buildTypedLines(titleText, visibleChars);
    const isTyping = titleCharCount > 0 && visibleChars < titleCharCount && currentTime >= typingStart;
    const caretVisible = isTyping && (Math.floor((currentTime - typingStart) * 2) % 2 === 0);

    const mediaConfigs = (clip.media || []).map((item, idx) => {
        const targetWord = normalizeToken(item.word);
        let delay = 0;

        if (wordTimings[targetWord] !== undefined) {
            delay = wordTimings[targetWord];
        } else {
            const matchedDelay = Object.entries(wordTimings)
                .filter(([key]) => {
                    if (!key) return false;
                    return key === targetWord || key.startsWith(targetWord) || targetWord.startsWith(key) || key.includes(targetWord) || targetWord.includes(key);
                })
                .reduce<number | null>((min, [, value]) => {
                    if (!Number.isFinite(value)) return min;
                    if (min === null) return value as number;
                    return Math.min(min, value as number);
                }, null);

            if (matchedDelay !== null) {
                delay = matchedDelay;
            } else {
                delay = (idx * 0.5) + 1.2;
            }
        }

        const finalDelay = Math.max(0, delay - 0.4);
        const isMediaVisible = !isRendering || currentTime >= (finalDelay - 0.1);

        return { finalDelay, isMediaVisible };
    });

    return {
        typedLines,
        caretVisible,
        animState,
        isContentVisible,
        mediaConfigs,
    };
};

interface Props {
    data: AroundTitleResult;
    clip: VideoClip;
    currentTime: number;
    isRendering: boolean;
}

export const AroundTitleRenderer: React.FC<Props> = ({ data, clip, currentTime, isRendering }) => {
    const { typedLines, caretVisible, animState, isContentVisible, mediaConfigs } = data;
    const isVisibleStyle = animState !== 'hidden';

    return (
        <div
            className={`intro-overlay ${animState} align-center`}
            style={{
                visibility: isVisibleStyle ? 'visible' : 'hidden',
                opacity: isVisibleStyle ? 1 : 0,
            }}
        >


            <div className={`intro-overlay-content ${isContentVisible ? 'content-visible' : 'content-hidden'}`}>
                <div className="intro-text-section">
                    <h1
                        className="intro-title"
                        style={{
                            whiteSpace: 'pre-line',
                            animationPlayState: isRendering ? 'paused' : 'running',
                            animationDelay: isRendering ? `-${currentTime}s` : '0s'
                        }}
                    >
                        {typedLines.map((line: string, lineIdx: number) => {
                            const isLastLine = lineIdx === typedLines.length - 1;
                            return (
                                <div key={lineIdx} className="intro-title-line">
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
                    </h1>
                </div>

                {clip.media && clip.media.length > 0 && (
                    <div className="intro-media-container">
                        {clip.media.map((item, idx) => {
                            const config = mediaConfigs[idx];
                            const finalDelay = config.finalDelay;
                            const isMediaVisible = config.isMediaVisible;

                            return (
                                <div
                                    key={`${item.src}-${idx}`}
                                    className={`intro-media-item anim-fly-in-${idx % 3} ${isMediaVisible ? 'opacity-100' : 'opacity-0'}`}
                                    style={{
                                        animationPlayState: isRendering ? 'paused' : 'running',
                                        animationDelay: isRendering ? `${finalDelay - currentTime}s` : `${finalDelay}s`,
                                        transition: 'opacity 0.3s ease'
                                    }}
                                >
                                    {item.src.toLowerCase().endsWith('.html') ? (
                                        <iframe
                                            src={item.src}
                                            className="intro-media-floating-content border-none bg-transparent"
                                            title={item.word}
                                        />
                                    ) : (
                                        <img
                                            src={item.src}
                                            alt={item.word}
                                            className="intro-media-floating-content"
                                        />
                                    )}
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
};
