import fs from "node:fs";
import path from "node:path";
import {
    AppBskyEmbedImages,
    AppBskyEmbedVideo,
    type AppBskyFeedPost,
    type BlobRef,
} from "@atproto/api";
import { validateFilePath } from "./utils.ts";

// ── Flags ───────────────────────────────────────────────────────

const args = process.argv.slice(2);
const dryRun = args.includes("--dry-run");
const filtered = args.filter((a) => a !== "--dry-run");

// ── MIME helpers ────────────────────────────────────────────────

const MIME_MAP: Record<string, string> = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".mp4": "video/mp4",
    ".webm": "video/webm",
    ".mov": "video/quicktime",
};

function mimeFor(filePath: string): string {
    const ext = path.extname(filePath).toLowerCase();
    const mime = MIME_MAP[ext];
    if (!mime) {
        console.error(`Unsupported file type: ${ext}`);
        console.error(`Supported: ${Object.keys(MIME_MAP).join(", ")}`);
        process.exit(1);
    }
    return mime;
}

function isVideo(mime: string): boolean {
    return mime.startsWith("video/");
}

// ── Video upload (recommended flow via video.bsky.app) ─────────

async function uploadVideo(filePath: string, mime: string): Promise<BlobRef> {
    const validatedPath = validateFilePath(filePath);
    const { login } = await import("./agent.ts");
    const agent = await login();
    const fileBytes = fs.readFileSync(validatedPath);

    // 1. Get service auth token scoped for video upload service
    const serviceAuth = await agent.com.atproto.server.getServiceAuth({
        aud: `did:web:video.bsky.app`,
        lxm: "com.atproto.repo.uploadBlob",
        exp: Math.floor(Date.now() / 1000) + 60 * 30, // 30 min
    });

    // 2. Upload video to the dedicated video service
    const uploadUrl = new URL("https://video.bsky.app/xrpc/app.bsky.video.uploadVideo");
    uploadUrl.searchParams.set("did", agent.session!.did);
    uploadUrl.searchParams.set("name", path.basename(filePath));

    let uploadRes = await fetch(uploadUrl.toString(), {
        method: "POST",
        headers: {
            Authorization: `Bearer ${serviceAuth.data.token}`,
            "Content-Type": mime,
            "Content-Length": fileBytes.length.toString(),
        },
        body: fileBytes,
    });

    let jobId: string;
    if (uploadRes.status === 409) {
        const errorData = await uploadRes.json() as { jobId?: string };
        jobId = errorData.jobId!;
        console.log(`Video already exists/uploading, resuming (job: ${jobId})...`);
    } else if (!uploadRes.ok) {
        throw new Error(`Video upload failed: ${uploadRes.status} ${await uploadRes.text()}`);
    } else {
        const uploadData = (await uploadRes.json()) as { jobId: string };
        jobId = uploadData.jobId;
        console.log(`Video uploaded, processing (job: ${jobId})...`);
    }

    // 3. Poll job status until complete
    let blob: BlobRef | undefined;
    for (let i = 0; i < 120; i++) {
        await new Promise((r) => setTimeout(r, 2000));

        const statusRes = await fetch(`https://video.bsky.app/xrpc/app.bsky.video.getJobStatus?jobId=${jobId}`, {
            headers: { Authorization: `Bearer ${serviceAuth.data.token}` }
        });

        if (!statusRes.ok) continue;

        const statusData = await statusRes.json() as any;
        const job = statusData.jobStatus;

        if (job.state === "JOB_STATE_COMPLETED" && job.blob) {
            blob = job.blob;
            break;
        }
        if (job.state === "JOB_STATE_FAILED") {
            throw new Error(`Video processing failed: ${job.error ?? "unknown error"}`);
        }

        if (i % 5 === 0) {
            console.log(`  still processing... (${job.state})`);
        }
    }

    if (!blob) throw new Error("Video processing timed out after 4 minutes");
    console.log("Video processing complete.");
    return blob;
}

// ── Image upload ───────────────────────────────────────────────

async function uploadImage(filePath: string, mime: string): Promise<BlobRef> {
    const validatedPath = validateFilePath(filePath);
    const { login } = await import("./agent.ts");
    const agent = await login();
    const fileBytes = fs.readFileSync(validatedPath);
    const response = await agent.uploadBlob(fileBytes, { encoding: mime });
    return response.data.blob;
}

// ── Main ───────────────────────────────────────────────────────

async function main() {
    const text = filtered[0];
    if (!text) {
        console.error("Usage: npx tsx scripts/post.ts <TEXT> [MEDIA_PATH...] [--dry-run]");
        process.exit(1);
    }

    const mediaPaths = filtered.slice(1);
    const record: Partial<AppBskyFeedPost.Record> = {
        text,
        createdAt: new Date().toISOString(),
    };

    const imageFiles: string[] = [];
    let videoFile: string | undefined;

    for (const mp of mediaPaths) {
        if (!fs.existsSync(mp)) {
            console.error(`File not found: ${mp}`);
            process.exit(1);
        }
        const mime = mimeFor(mp);
        if (isVideo(mime)) {
            if (videoFile) {
                console.error("Error: only one video per post is allowed.");
                process.exit(1);
            }
            videoFile = mp;
        } else {
            imageFiles.push(mp);
        }
    }

    if (videoFile && imageFiles.length > 0) {
        console.error("Error: cannot mix images and video.");
        process.exit(1);
    }

    if (dryRun) {
        console.log("[DRY RUN] Would post text: " + text);
        return;
    }

    const { login } = await import("./agent.ts");
    const agent = await login();

    if (mediaPaths.length > 0) {
        if (videoFile) {
            const blob = await uploadVideo(videoFile, mimeFor(videoFile));
            record.embed = { $type: "app.bsky.embed.video", video: blob, alt: "" };
        } else {
            const images: AppBskyEmbedImages.Image[] = [];
            for (const img of imageFiles) {
                const blob = await uploadImage(img, mimeFor(img));
                images.push({ image: blob, alt: "" });
            }
            record.embed = { $type: "app.bsky.embed.images", images };
        }
    }

    try {
        const res = await agent.post(record as AppBskyFeedPost.Record);
        console.log(`Posted! URI: ${res.uri}`);
    } catch (err: any) {
        console.error(`Failed to create post: ${err.message}`);
        process.exit(1);
    }
}

main();
