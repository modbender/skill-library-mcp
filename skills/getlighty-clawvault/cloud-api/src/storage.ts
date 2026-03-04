import fs from "node:fs/promises";
import path from "node:path";
import {
  S3Client,
  PutObjectCommand,
  GetObjectCommand,
  DeleteObjectCommand,
} from "@aws-sdk/client-s3";

const useS3 = !!process.env.S3_ENDPOINT;

// ─── S3 backend ──────────────────────────────────────────────

const s3 = useS3
  ? new S3Client({
      endpoint: process.env.S3_ENDPOINT,
      region: process.env.S3_REGION || "auto",
      credentials: {
        accessKeyId: process.env.S3_ACCESS_KEY || "",
        secretAccessKey: process.env.S3_SECRET_KEY || "",
      },
      forcePathStyle: true,
    })
  : null;

const bucket = process.env.S3_BUCKET || "clawvault";

// ─── Filesystem backend (local dev / no S3 configured) ──────

const FS_ROOT = process.env.STORAGE_PATH || "/tmp/clawvault-storage";

async function ensureDir(filePath: string) {
  await fs.mkdir(path.dirname(filePath), { recursive: true });
}

// ─── Public API ──────────────────────────────────────────────

function vaultKey(vaultId: string, version: string): string {
  return `vaults/${vaultId}/${version}.tar.gz`;
}

export async function uploadArchive(
  vaultId: string,
  versionId: string,
  data: Buffer | Uint8Array
): Promise<string> {
  const key = vaultKey(vaultId, versionId);

  if (s3) {
    await s3.send(
      new PutObjectCommand({
        Bucket: bucket,
        Key: key,
        Body: data,
        ContentType: "application/gzip",
      })
    );
  } else {
    const filePath = path.join(FS_ROOT, key);
    await ensureDir(filePath);
    await fs.writeFile(filePath, data);
  }

  return key;
}

export async function downloadArchive(
  s3Key: string
): Promise<Uint8Array | null> {
  if (s3) {
    try {
      const res = await s3.send(
        new GetObjectCommand({ Bucket: bucket, Key: s3Key })
      );
      if (!res.Body) return null;
      return await res.Body.transformToByteArray();
    } catch (err: unknown) {
      if (err instanceof Error && err.name === "NoSuchKey") return null;
      throw err;
    }
  } else {
    try {
      return await fs.readFile(path.join(FS_ROOT, s3Key));
    } catch {
      return null;
    }
  }
}

export async function deleteArchive(s3Key: string): Promise<void> {
  if (s3) {
    await s3.send(new DeleteObjectCommand({ Bucket: bucket, Key: s3Key }));
  } else {
    await fs.unlink(path.join(FS_ROOT, s3Key)).catch(() => {});
  }
}
