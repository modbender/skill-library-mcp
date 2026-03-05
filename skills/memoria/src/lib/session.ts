import { readFile, writeFile, readdir, mkdir } from 'node:fs/promises';
import { join } from 'node:path';
import matter from 'gray-matter';
import type { SessionData, HandoffDocument } from '../types.js';

const SESSION_FILE = 'sessions/current.md';
const HANDOFFS_DIR = 'sessions/handoffs';

function sessionPath(vaultPath: string): string {
  return join(vaultPath, SESSION_FILE);
}

function handoffsDir(vaultPath: string): string {
  return join(vaultPath, HANDOFFS_DIR);
}

export async function getSession(vaultPath: string): Promise<SessionData> {
  try {
    const raw = await readFile(sessionPath(vaultPath), 'utf-8');
    const { data } = matter(raw);
    return {
      state: (data.state as SessionData['state']) || 'idle',
      startedAt: data.startedAt as string | undefined,
      workingOn: data.workingOn as string | undefined,
      focus: data.focus as string | undefined,
      lastCheckpoint: data.lastCheckpoint as string | undefined,
    };
  } catch {
    return { state: 'idle' };
  }
}

export async function saveSession(
  vaultPath: string,
  session: SessionData,
): Promise<void> {
  const content = session.workingOn
    ? `Currently working on: ${session.workingOn}`
    : '';
  const fm: Record<string, unknown> = {};
  for (const [key, val] of Object.entries(session)) {
    if (val !== undefined) fm[key] = val;
  }
  const raw = matter.stringify(content, fm);
  await writeFile(sessionPath(vaultPath), raw, 'utf-8');
}

export async function startSession(vaultPath: string): Promise<SessionData> {
  const session: SessionData = {
    state: 'active',
    startedAt: new Date().toISOString(),
  };
  await saveSession(vaultPath, session);
  return session;
}

export async function updateCheckpoint(
  vaultPath: string,
  workingOn?: string,
  focus?: string,
): Promise<SessionData> {
  const session = await getSession(vaultPath);
  session.state = 'active';
  session.lastCheckpoint = new Date().toISOString();
  if (workingOn) session.workingOn = workingOn;
  if (focus) session.focus = focus;
  await saveSession(vaultPath, session);
  return session;
}

export async function endSession(
  vaultPath: string,
  summary: string,
  nextSteps?: string,
): Promise<HandoffDocument> {
  const session = await getSession(vaultPath);
  const now = new Date();
  const dateStr = now.toISOString().slice(0, 10);

  const handoff: HandoffDocument = {
    created: now.toISOString(),
    summary,
    workingOn: session.workingOn,
    focus: session.focus,
    nextSteps,
  };

  const dir = handoffsDir(vaultPath);
  await mkdir(dir, { recursive: true });

  const handoffContent = matter.stringify(
    [
      `## Summary\n${summary}`,
      session.workingOn ? `## Working On\n${session.workingOn}` : '',
      session.focus ? `## Focus\n${session.focus}` : '',
      nextSteps ? `## Next Steps\n${nextSteps}` : '',
    ]
      .filter(Boolean)
      .join('\n\n'),
    {
      created: handoff.created,
      type: 'handoff',
    },
  );

  const handoffPath = join(dir, `${dateStr}.md`);
  await writeFile(handoffPath, handoffContent, 'utf-8');

  const idleSession: SessionData = { state: 'idle' };
  await saveSession(vaultPath, idleSession);

  return handoff;
}

export async function getRecentHandoffs(
  vaultPath: string,
  limit = 3,
): Promise<HandoffDocument[]> {
  const dir = handoffsDir(vaultPath);
  let entries: string[];
  try {
    entries = await readdir(dir);
  } catch {
    return [];
  }

  const mdFiles = entries.filter((e) => e.endsWith('.md')).sort().reverse();
  const handoffs: HandoffDocument[] = [];

  for (const file of mdFiles.slice(0, limit)) {
    try {
      const raw = await readFile(join(dir, file), 'utf-8');
      const { data, content } = matter(raw);
      handoffs.push({
        created: (data.created as string) || file.replace('.md', ''),
        summary: content.trim(),
        workingOn: data.workingOn as string | undefined,
        focus: data.focus as string | undefined,
        nextSteps: data.nextSteps as string | undefined,
      });
    } catch {
      continue;
    }
  }

  return handoffs;
}
