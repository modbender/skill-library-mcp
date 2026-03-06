
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import path from "path";
import fs from "fs-extra";
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Configuration
const SERVER_PATH = path.resolve(__dirname, "index.js");
const TEST_PROJECT_ROOT = path.resolve(__dirname, "../../"); // Root of Muninn repo

async function createClient(id: string) {
    const client = new Client(
        { name: `Agent-${id}`, version: "1.0.0" },
        { capabilities: {} }
    );

    const transport = new StdioClientTransport({
        command: "node",
        args: [SERVER_PATH],
        env: { 
            ...process.env, 
            MUNINN_PROJECT_PATH: TEST_PROJECT_ROOT,
            MUNINN_AUTO_DETECT: "false" 
        }
    });

    await client.connect(transport);
    return { client, transport };
}

async function runConcurrencyTest() {
    console.log("🚀 Starting Multi-Agent Concurrency Test...");
    
    const agents = ["A", "B", "C"];
    const clients: any[] = [];

    // Initialize clients
    for (const id of agents) {
        console.log(`Initializing Agent ${id}...`);
        clients.push(await createClient(id));
    }

    const testMemories = agents.map(id => ({
        title: `Concurrency_Test_Memory_${id}`,
        content: `This is a memory from Agent ${id} at ${new Date().toISOString()}`,
        category: "concurrency_test"
    }));

    console.log("🔥 Launching concurrent add_memory calls...");
    
    const startTime = Date.now();
    const writePromises = clients.map((c, i) => {
        console.log(`Agent ${agents[i]} adding memory...`);
        return c.client.callTool({
            name: "add_memory",
            arguments: testMemories[i]
        });
    });

    // Also throw in some concurrent searches
    const searchPromises = clients.map((c, i) => {
        console.log(`Agent ${agents[i]} searching...`);
        return c.client.callTool({
            name: "search_context",
            arguments: { query: "concurrency", limit: 5 }
        });
    });

    try {
        const results = await Promise.all([...writePromises, ...searchPromises]);
        const duration = Date.now() - startTime;
        console.log(`✅ All concurrent operations finished in ${duration}ms`);
        
        // Verify results
        console.log("🧐 Verifying data integrity...");
        const memoriesDir = path.join(TEST_PROJECT_ROOT, ".muninn/memories/concurrency_test");
        const files = await fs.readdir(memoriesDir);
        
        console.log(`Found ${files.length} memory files in ${memoriesDir}`);
        
        for (const id of agents) {
            const expectedFile = `concurrency_test_memory_${id.toLowerCase()}.md`;
            if (files.includes(expectedFile)) {
                console.log(`  ✅ Memory from Agent ${id} exists.`);
            } else {
                console.error(`  ❌ Memory from Agent ${id} is MISSING!`);
            }
        }

        if (files.length === agents.length) {
            console.log("✨ No data loss detected.");
        } else {
            console.warn(`⚠️ Unexpected number of files: ${files.length} (expected ${agents.length})`);
        }

    } catch (err) {
        console.error("❌ Concurrency test FAILED with error:", err);
    } finally {
        // Cleanup
        for (const c of clients) {
            await c.transport.close();
        }
        
        // Optionally remove the test memories
        // await fs.remove(path.join(TEST_PROJECT_ROOT, ".muninn/memories/concurrency_test"));
    }
}

runConcurrencyTest().catch(console.error);
