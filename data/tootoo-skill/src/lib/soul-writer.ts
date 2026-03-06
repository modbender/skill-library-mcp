// Writes content to the OpenClaw workspace
import * as fs from 'fs/promises';
import * as path from 'path';

export class SoulWriter {
  constructor(private workspacePath: string) {}

  async writeSoul(content: string): Promise<void> {
    await fs.writeFile(path.join(this.workspacePath, 'SOUL.md'), content, 'utf-8');
  }

  async writeUser(content: string): Promise<void> {
    await fs.writeFile(path.join(this.workspacePath, 'USER.md'), content, 'utf-8');
  }
}
