import os from "node:os";
import path from "node:path";

export function getStateRoot(env: NodeJS.ProcessEnv): string {
  return env.SEC_DAILY_DIGEST_HOME || path.join(os.homedir(), ".sec-daily-digest");
}
