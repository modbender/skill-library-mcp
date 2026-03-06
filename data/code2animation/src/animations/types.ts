import { VideoClip } from '../types';

export interface AnimationProps {
    clip: VideoClip;
    currentTime: number;
    duration: number;
    wordTimings: Record<string, number>;
    isRendering: boolean;
}

export interface AnimationResult {
    typedLines: string[];
    caretVisible: boolean;
    // Common states can be added here
    [key: string]: any;
}
