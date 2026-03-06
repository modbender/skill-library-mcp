import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { getStateRoot } from "../config/paths";

export type OpmlProfile = "tiny" | "full";

export interface SyncOpmlOptions {
  profile: OpmlProfile;
  env: NodeJS.ProcessEnv;
  fetcher?: typeof fetch;
}

export interface SyncOpmlResult {
  opmlPath: string;
  usedCache: boolean;
  updated: boolean;
}

function getRemoteUrl(profile: OpmlProfile): string {
  return profile === "tiny"
    ? "https://raw.githubusercontent.com/zer0yu/CyberSecurityRSS/master/tiny.opml"
    : "https://raw.githubusercontent.com/zer0yu/CyberSecurityRSS/master/CyberSecurityRSS.opml";
}

function getCachePath(root: string, profile: OpmlProfile): string {
  return path.join(root, "opml", profile === "tiny" ? "tiny.opml" : "CyberSecurityRSS.opml");
}

export async function syncOpml(options: SyncOpmlOptions): Promise<SyncOpmlResult> {
  const fetcher = options.fetcher ?? fetch;
  const root = getStateRoot(options.env);
  const cachePath = getCachePath(root, options.profile);
  await mkdir(path.dirname(cachePath), { recursive: true });

  try {
    const response = await fetcher(getRemoteUrl(options.profile));
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const content = await response.text();
    await writeFile(cachePath, content, "utf8");
    return {
      opmlPath: cachePath,
      usedCache: false,
      updated: true,
    };
  } catch {
    try {
      await readFile(cachePath, "utf8");
      return {
        opmlPath: cachePath,
        usedCache: true,
        updated: false,
      };
    } catch {
      throw new Error("No cached OPML available and remote update check failed.");
    }
  }
}
