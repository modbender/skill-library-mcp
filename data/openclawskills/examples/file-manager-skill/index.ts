/**
 * File Manager Skill
 * Basic file operations
 */

import * as fs from 'fs/promises';
import * as path from 'path';

interface FileManagerConfig {
  basePath?: string;
  allowedExtensions?: string[];
}

interface SkillContext {
  userId: string;
  logger: Logger;
}

interface Logger {
  debug(msg: string): void;
  info(msg: string): void;
  error(msg: string): void;
}

interface FileInfo {
  name: string;
  path: string;
  size: number;
  isDirectory: boolean;
  modifiedAt: Date;
}

export class FileManagerSkill {
  private config: FileManagerConfig;
  private context: SkillContext;

  constructor(config: FileManagerConfig, context: SkillContext) {
    this.config = config;
    this.context = context;
  }

  private resolvePath(filePath: string): string {
    const base = this.config.basePath || process.cwd();
    // Prevent directory traversal
    const resolved = path.resolve(base, filePath);
    if (!resolved.startsWith(path.resolve(base))) {
      throw new Error('Access denied: Path outside base directory');
    }
    return resolved;
  }

  /**
   * Read file contents
   */
  async readFile(filePath: string, encoding: 'utf-8' | 'base64' = 'utf-8'): Promise<string> {
    const fullPath = this.resolvePath(filePath);
    this.context.logger.debug(`Reading file: ${fullPath}`);
    
    try {
      const content = await fs.readFile(fullPath, { encoding });
      return content;
    } catch (error) {
      this.context.logger.error(`Failed to read file: ${error}`);
      throw new Error(`Could not read file: ${filePath}`);
    }
  }

  /**
   * Write to a file
   */
  async writeFile(filePath: string, content: string, encoding: 'utf-8' | 'base64' = 'utf-8'): Promise<void> {
    const fullPath = this.resolvePath(filePath);
    
    // Check extension if restrictions apply
    if (this.config.allowedExtensions) {
      const ext = path.extname(filePath);
      if (!this.config.allowedExtensions.includes(ext)) {
        throw new Error(`File type not allowed: ${ext}`);
      }
    }

    this.context.logger.info(`Writing file: ${fullPath}`);

    // Ensure directory exists
    await fs.mkdir(path.dirname(fullPath), { recursive: true });
    
    await fs.writeFile(fullPath, content, { encoding });
  }

  /**
   * List files in directory
   */
  async listFiles(dirPath: string = ''): Promise<FileInfo[]> {
    const fullPath = this.resolvePath(dirPath);
    this.context.logger.debug(`Listing files: ${fullPath}`);

    try {
      const entries = await fs.readdir(fullPath, { withFileTypes: true });
      const files: FileInfo[] = [];

      for (const entry of entries) {
        const entryPath = path.join(fullPath, entry.name);
        const stats = await fs.stat(entryPath);
        
        files.push({
          name: entry.name,
          path: path.relative(this.config.basePath || process.cwd(), entryPath),
          size: stats.size,
          isDirectory: entry.isDirectory(),
          modifiedAt: stats.mtime
        });
      }

      return files;
    } catch (error) {
      this.context.logger.error(`Failed to list files: ${error}`);
      throw new Error(`Could not list files in: ${dirPath}`);
    }
  }

  /**
   * Delete a file
   */
  async deleteFile(filePath: string): Promise<void> {
    const fullPath = this.resolvePath(filePath);
    this.context.logger.info(`Deleting file: ${fullPath}`);
    
    await fs.unlink(fullPath);
  }

  /**
   * Check if file exists
   */
  async exists(filePath: string): Promise<boolean> {
    try {
      const fullPath = this.resolvePath(filePath);
      await fs.access(fullPath);
      return true;
    } catch {
      return false;
    }
  }
}

export default function createSkill(config: FileManagerConfig, context: SkillContext) {
  return new FileManagerSkill(config, context);
}

export type { FileManagerConfig, FileInfo };
