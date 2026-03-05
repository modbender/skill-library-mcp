import { writeConfigToFile, type ClawbanConfig, type FsLike } from './config.js';

export type SetupFs = FsLike & {
  readFile(path: string, encoding: 'utf-8'): Promise<string>;
};

export async function runSetup(opts: {
  fs: Pick<SetupFs, 'readFile' | 'writeFile' | 'mkdir'>;
  configPath: string;
  force: boolean;
  config: ClawbanConfig;
  /** Validate selected adapters are installed/authenticated (read-only). Throw to fail hard. */
  validate: () => Promise<void>;
}): Promise<void> {
  const exists = await fileExists(opts.fs, opts.configPath);
  if (exists && !opts.force) {
    throw new Error(`Refusing to overwrite existing ${opts.configPath}. Re-run with --force.`);
  }

  // Required: validate before writing config.
  await opts.validate();

  await writeConfigToFile({ fs: opts.fs, path: opts.configPath, config: opts.config });
}

async function fileExists(
  fs: Pick<SetupFs, 'readFile'>,
  filePath: string,
): Promise<boolean> {
  try {
    await fs.readFile(filePath, 'utf-8');
    return true;
  } catch (err: any) {
    if (err?.code === 'ENOENT') return false;
    return true;
  }
}
