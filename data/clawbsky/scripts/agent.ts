import { BskyAgent } from "@atproto/api";
import * as dotenv from "dotenv";

dotenv.config();

const agent = new BskyAgent({ service: "https://bsky.social" });

/**
 * Ensures the agent is logged in.
 */
async function login() {
    if (agent.session) return agent;

    const handle = process.env.BLUESKY_HANDLE;
    const password = process.env.BLUESKY_APP_PASSWORD;

    if (!handle || !password) {
        console.error(
            "Error: BLUESKY_HANDLE and BLUESKY_APP_PASSWORD env vars are required.\n" +
            "Generate an App Password at: https://bsky.app/settings/app-passwords"
        );
        process.exit(1);
    }

    await agent.login({ identifier: handle, password });
    return agent;
}

export { agent, login };
