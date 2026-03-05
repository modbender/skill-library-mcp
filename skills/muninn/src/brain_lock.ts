import path from "path";
import fs from "fs-extra";
import crypto from "node:crypto";

const BRAIN_LOCK = "brain.lock";

export class BrainLock {
    private lockPath: string;
    private agentName: string;
    private lockId: string | null = null;

    constructor(muninnPath: string, agentName: string = "muninn-server") {
        this.lockPath = path.join(muninnPath, BRAIN_LOCK);
        this.agentName = agentName;
    }

    async acquire(timeoutMs: number = 30000): Promise<boolean> {
        const start = Date.now();
        const id = Math.random().toString(36).substring(7);

        while (Date.now() - start < timeoutMs) {
            try {
                if (!(await fs.pathExists(this.lockPath))) {
                    await fs.writeJSON(this.lockPath, {
                        agent: this.agentName,
                        pid: process.pid,
                        id: id,
                        timestamp: new Date().toISOString()
                    });
                    
                    // Atomic-ish check
                    const data = await fs.readJSON(this.lockPath);
                    if (data.id === id && data.pid === process.pid) {
                        this.lockId = id;
                        return true;
                    }
                } else {
                    const data = await fs.readJSON(this.lockPath);
                    
                    // Check if PID is still alive
                    let isAlive = true;
                    try {
                        process.kill(data.pid, 0);
                    } catch (e) {
                        isAlive = false;
                    }

                    // Check for timeout
                    const lockTime = new Date(data.timestamp).getTime();
                    const isTimedOut = Date.now() - lockTime > 5 * 60 * 1000;

                    if (!isAlive || isTimedOut) {
                        console.error(`[BrainLock] Overriding stale lock: ${data.agent} (PID ${data.pid})`);
                        await fs.remove(this.lockPath);
                        continue;
                    }
                }
            } catch (err) { }
            await new Promise(resolve => setTimeout(resolve, Math.random() * 300 + 100));
        }
        return false;
    }

    async release(): Promise<void> {
        if (!this.lockId) return;
        try {
            if (await fs.pathExists(this.lockPath)) {
                const data = await fs.readJSON(this.lockPath);
                if (data.id === this.lockId) {
                    await fs.remove(this.lockPath);
                    this.lockId = null;
                }
            }
        } catch (err) {
            console.error(`[BrainLock] Release failed:`, err);
        }
    }
}
