import { agent, login } from "./agent.ts";

async function main() {
    await login();

    const uri = process.argv[2];

    if (!uri) {
        console.error("Usage: npx tsx scripts/delete.ts <POST_URI>");
        console.error("Example: npx tsx scripts/delete.ts at://did:plc:abc123/app.bsky.feed.post/xyz");
        process.exit(1);
    }

    try {
        await agent.deletePost(uri);
        console.log(`Deleted: ${uri}`);
    } catch (err: unknown) {
        const message = err instanceof Error ? err.message : String(err);
        console.error(`Failed to delete post: ${message}`);
        process.exit(1);
    }
}

main();
