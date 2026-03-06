import React from 'react';
import { VideoClip } from '../types';
import { useFootageClip, AroundTitleRenderer, FullScreenRenderer } from '../animations';

interface Props {
    clip: VideoClip;
    currentTime: number;
    projectId: string;
    clipIndex: number;
    duration: number;
}

export const FootageClip: React.FC<Props> = (props) => {
    const { animationData, isRendering } = useFootageClip(props);

    if (!animationData) return null;

    if (animationData.type === 'aroundTitle') {
        return (
            <AroundTitleRenderer
                data={animationData.data}
                clip={props.clip}
                currentTime={props.currentTime}
                isRendering={isRendering}
            />
        );
    }

    if (animationData.type === 'fullScreen') {
        return (
            <FullScreenRenderer
                data={animationData.data}
                clip={props.clip}
            />
        );
    }

    return null;
};
