import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import fc from 'fast-check';
import { findSkillManifest } from '../index.js';
import type { ToolsInterface } from '../types.js';

/**
 * Feature: security-review-fixes
 * Property 1: Downloaded content without SKILL.md is rejected
 *
 * **Validates: Requirements 2.4, 2.5**
 */

// Arbitrary for generating file names that are NOT skill.md (case-insensitive)
const nonSkillFileName: fc.Arbitrary<string> = fc
  .string({ minLength: 1, maxLength: 30 })
  .filter((name) => name.toLowerCase() !== 'skill.md' && name.trim().length > 0 && !name.includes('/') && !name.includes('\0'));

// Arbitrary for generating a flat directory structure (list of file names, no SKILL.md)
const nonSkillFileList: fc.Arbitrary<string[]> = fc.array(nonSkillFileName, { minLength: 0, maxLength: 20 });

// Arbitrary for SKILL.md name variants (case-insensitive)
const skillMdVariant: fc.Arbitrary<string> = fc.constantFrom(
  'SKILL.md',
  'skill.md',
  'Skill.md',
  'SKILL.MD',
  'Skill.Md',
  'sKiLl.Md',
);

/**
 * Build a mock ToolsInterface that simulates a directory structure.
 *
 * @param structure - Map of directory path to its entries (file/dir names).
 * @param directories - Set of paths that are directories.
 */
function buildMockTools(
  structure: Map<string, string[]>,
  directories: Set<string>,
): ToolsInterface {
  return {
    async readdir(dirPath: string): Promise<string[]> {
      const entries = structure.get(dirPath);
      if (!entries) throw new Error(`ENOENT: ${dirPath}`);
      return entries;
    },
    async lstat(filePath: string) {
      return {
        isDirectory: () => directories.has(filePath),
        isFile: () => !directories.has(filePath),
        isSymbolicLink: () => false,
      };
    },
    // Unused methods — stub them out
    async readFile() { return ''; },
    async writeFile() {},
    async stat() { return { isDirectory: () => false, isFile: () => true, isSymbolicLink: () => false }; },
    async realpath(p: string) { return p; },
    async mkdtemp(prefix: string) { return prefix + 'tmp'; },
    async rm() {},
    async exists() { return false; },
  };
}

describe('findSkillManifest — Property Tests', () => {
  it('Property 1: rejects any directory without SKILL.md at root or one level deep', async () => {
    await fc.assert(
      fc.asyncProperty(
        nonSkillFileList,
        fc.array(nonSkillFileName, { minLength: 0, maxLength: 5 }),
        fc.array(nonSkillFileList, { minLength: 0, maxLength: 5 }),
        async (rootFiles: string[], subDirNames: string[], subDirContents: string[][]) => {
          const rootDir = '/tmp/test-root';
          const structure = new Map<string, string[]>();
          const directories = new Set<string>();

          const rootEntries: string[] = [...rootFiles, ...subDirNames];
          structure.set(rootDir, rootEntries);

          for (let i = 0; i < subDirNames.length; i++) {
            const subPath = `${rootDir}/${subDirNames[i]}`;
            directories.add(subPath);
            const contents: string[] = subDirContents[i] ?? [];
            structure.set(subPath, contents);
          }

          const tools = buildMockTools(structure, directories);
          const result = await findSkillManifest(rootDir, tools);
          assert.equal(result, false, `Expected false for structure without SKILL.md`);
        },
      ),
      { numRuns: 100 },
    );
  });

  it('Property 1: accepts any directory with SKILL.md at root level', async () => {
    await fc.assert(
      fc.asyncProperty(
        nonSkillFileList,
        skillMdVariant,
        async (otherFiles: string[], skillName: string) => {
          const rootDir = '/tmp/test-root';
          const structure = new Map<string, string[]>();
          const directories = new Set<string>();

          structure.set(rootDir, [...otherFiles, skillName]);

          const tools = buildMockTools(structure, directories);
          const result = await findSkillManifest(rootDir, tools);
          assert.equal(result, true, `Expected true when ${skillName} is at root`);
        },
      ),
      { numRuns: 100 },
    );
  });

  it('Property 1: accepts any directory with SKILL.md one level deep', async () => {
    await fc.assert(
      fc.asyncProperty(
        nonSkillFileList,
        nonSkillFileName,
        nonSkillFileList,
        skillMdVariant,
        async (rootFiles: string[], subDirName: string, subDirFiles: string[], skillName: string) => {
          const rootDir = '/tmp/test-root';
          const structure = new Map<string, string[]>();
          const directories = new Set<string>();

          structure.set(rootDir, [...rootFiles, subDirName]);

          const subPath = `${rootDir}/${subDirName}`;
          directories.add(subPath);
          structure.set(subPath, [...subDirFiles, skillName]);

          const tools = buildMockTools(structure, directories);
          const result = await findSkillManifest(rootDir, tools);
          assert.equal(result, true, `Expected true when ${skillName} is one level deep in ${subDirName}`);
        },
      ),
      { numRuns: 100 },
    );
  });

  it('Property 1: rejects SKILL.md at depth 2 or deeper', async () => {
    await fc.assert(
      fc.asyncProperty(
        nonSkillFileList,
        nonSkillFileName,
        nonSkillFileName,
        nonSkillFileList,
        skillMdVariant,
        async (rootFiles: string[], subDirName: string, deepDirName: string, deepFiles: string[], skillName: string) => {
          const rootDir = '/tmp/test-root';
          const structure = new Map<string, string[]>();
          const directories = new Set<string>();

          structure.set(rootDir, [...rootFiles, subDirName]);

          const subPath = `${rootDir}/${subDirName}`;
          directories.add(subPath);
          structure.set(subPath, [deepDirName]);

          const deepPath = `${subPath}/${deepDirName}`;
          directories.add(deepPath);
          structure.set(deepPath, [...deepFiles, skillName]);

          const tools = buildMockTools(structure, directories);
          const result = await findSkillManifest(rootDir, tools);
          assert.equal(result, false, `Expected false when SKILL.md is at depth 2+`);
        },
      ),
      { numRuns: 100 },
    );
  });
});
