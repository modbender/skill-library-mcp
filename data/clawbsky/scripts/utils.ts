import { RichText } from "@atproto/api";
import ffmpeg from "fluent-ffmpeg";
import path from "node:path";
import fs from "node:fs";

// ── Rich Text Parsing ───────────────────────────────────────────

export interface RichTextSegment {
    type: "text" | "mention" | "link";
    text: string;
    url?: string;
    handle?: string; // for mentions like @user.bsky.social
}

/**
 * Parse text for @mentions and links to create proper RichText facets.
 * This makes @mentions clickable and links actually clickable in Bluesky.
 */
export function parseRichText(text: string): {
    normalizedText: string;
    facets: RichText["facets"];
} {
    const rt = new RichText({ text });

    // Detect mentions (e.g., @joy.bsky.social)
    const mentionRegex = /@([a-zA-Z0-9._-]+(?:\.[a-zA-Z0-9._-]+)+)/g;
    let match;
    while ((match = mentionRegex.exec(text)) !== null) {
        const handle = match[1];
        const did = `did:plc:unknown`; // Would need resolution in production

        rt.facets?.push({
            index: {
                byteStart: match.index,
                byteEnd: match.index + match[0].length,
            },
            features: [
                {
                    $type: "app.bsky.richtext.facet#mention",
                    did,
                },
            ],
        });
    }

    // Detect links (http://, https://)
    const linkRegex = /(https?:\/\/[^\s]+)/g;
    while ((match = linkRegex.exec(text)) !== null) {
        rt.facets?.push({
            index: {
                byteStart: match.index,
                byteEnd: match.index + match[0].length,
            },
            features: [
                {
                    $type: "app.bsky.richtext.facet#link",
                    uri: match[1],
                },
            ],
        });
    }

    return {
        normalizedText: rt.text,
        facets: rt.facets,
    };
}

// ── File Path Validation ────────────────────────────────────────

/**
 * Validates that a file path is safe to pass to external processes.
 * Resolves to an absolute path, confirms the file exists, and rejects
 * any path containing shell meta-characters that could enable injection.
 */
export function validateFilePath(filePath: string): string {
    // Reject characters that have special meaning in shell contexts
    const forbidden = /[;|&$`(){}[\]<>\n\r\0"'\\]/;
    if (forbidden.test(filePath)) {
        throw new Error(
            `Invalid file path — contains forbidden characters: ${filePath}`
        );
    }

    const resolved = path.resolve(filePath);

    if (!fs.existsSync(resolved)) {
        throw new Error(`File not found: ${resolved}`);
    }

    return resolved;
}

// ── Video Aspect Ratio Detection ─────────────────────────────────

export interface VideoMetadata {
    width: number;
    height: number;
    duration: number;
    aspectRatio: string;
    isVertical: boolean;
    isHorizontal: boolean;
    isSquare: boolean;
}

/**
 * Get video metadata including aspect ratio using ffprobe.
 * This prevents "stretched" videos on Bluesky by ensuring proper metadata.
 */
export async function getVideoMetadata(filePath: string): Promise<VideoMetadata> {
    // Validate path before passing to ffprobe
    let safePath: string;
    try {
        safePath = validateFilePath(filePath);
    } catch (e) {
        return Promise.reject(e);
    }

    return new Promise((resolve, reject) => {
        ffmpeg.ffprobe(safePath, (err, metadata) => {
            if (err) {
                reject(new Error(`ffprobe failed: ${err.message}`));
                return;
            }

            const videoStream = metadata.streams.find(s => s.codec_type === "video");
            if (!videoStream || !videoStream.width || !videoStream.height) {
                reject(new Error("No video stream found in file"));
                return;
            }

            const width = videoStream.width;
            const height = videoStream.height;
            const duration = metadata.format.duration || 0;

            // Calculate aspect ratio
            const gcd = (a: number, b: number): number => b === 0 ? a : gcd(b, a % b);
            const divisor = gcd(width, height);
            const aspectRatio = `${width / divisor}:${height / divisor}`;

            resolve({
                width,
                height,
                duration: Math.round(duration * 10) / 10,
                aspectRatio,
                isVertical: height > width,
                isHorizontal: width > height,
                isSquare: width === height,
            });
        });
    });
}

// ── Thread Creation ─────────────────────────────────────────────

export interface ThreadPost {
    text: string;
    mediaPaths?: string[];
    altText?: string;
    altVideoText?: string;
}

/**
 * Post a thread to Bluesky. Each post is connected via "reply" reference.
 * Returns array of posted URIs.
 */
export async function postThread(
    thread: ThreadPost[],
    agent: import("@atproto/api").BskyAgent
): Promise<string[]> {
    if (thread.length === 0) {
        throw new Error("Thread cannot be empty");
    }

    const postedUris: string[] = [];
    let parentUri: string | undefined;
    let parentCid: string | undefined;

    for (let i = 0; i < thread.length; i++) {
        const post = thread[i];

        // Build record
        const record: import("@atproto/api").AppBskyFeedPost.Record = {
            text: post.text,
            createdAt: new Date().toISOString(),
        };

        // Add reply reference if not first post
        if (parentUri && parentCid) {
            record.reply = {
                root: {
                    uri: postedUris[0], // First post is root
                    cid: "", // Will be fetched
                },
                parent: {
                    uri: parentUri,
                    cid: parentCid,
                },
            };
        }

        // TODO: Add media handling here (similar to cli.ts)
        // For now, text-only thread support

        try {
            const res = await agent.post(record);
            postedUris.push(res.uri);
            parentUri = res.uri;
            parentCid = res.cid;
            console.log(`Thread post ${i + 1}/${thread.length}: ${res.uri}`);
        } catch (err) {
            const msg = err instanceof Error ? err.message : String(err);
            throw new Error(`Failed to post thread ${i + 1}: ${msg}`);
        }
    }

    return postedUris;
}
