export type ClipType = 'footagesAroundTitle' | 'footagesFullScreen';

export interface MediaItem {
  src: string;
  word: string; // The word in the title/speech that triggers this media
  type?: 'video' | 'image' | 'html'; // Optional type for rendering
}

export interface VideoClip {
  type: ClipType;
  title?: string;
  speech?: string;
  media?: MediaItem[];
  // TTS overrides
  voice?: string;
}

export interface AudioAlignment {
  characters: string[];
  character_start_times_seconds: number[];
  character_end_times_seconds: number[];
}

export interface Project {
  name: string;
  clips: VideoClip[];
  background?: string;
}
