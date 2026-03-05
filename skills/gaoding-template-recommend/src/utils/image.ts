import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

const EXPORT_DIR = path.join(os.homedir(), '.openclaw', 'skills', 'gaoding-template', 'exports');

/** 确保导出目录存在 */
export function ensureExportDir(): string {
    if (!fs.existsSync(EXPORT_DIR)) {
        fs.mkdirSync(EXPORT_DIR, { recursive: true });
    }
    return EXPORT_DIR;
}

/** 将 Buffer 保存为临时图片文件，返回路径 */
export function saveTempImage(buffer: Buffer, name: string): string {
    const dir = ensureExportDir();
    const filePath = path.join(dir, `${name}-${Date.now()}.png`);
    fs.writeFileSync(filePath, buffer);
    return filePath;
}

/** 清理过期的导出文件（超过 24 小时） */
export function cleanExpiredExports(): void {
    if (!fs.existsSync(EXPORT_DIR)) return;

    const now = Date.now();
    const maxAge = 24 * 60 * 60 * 1000;

    for (const file of fs.readdirSync(EXPORT_DIR)) {
        try {
            const filePath = path.join(EXPORT_DIR, file);
            const stat = fs.statSync(filePath);
            if (now - stat.mtimeMs > maxAge) {
                fs.unlinkSync(filePath);
            }
        } catch (err) {
            console.warn(`[image] failed to clean ${file}:`, err);
        }
    }
}
