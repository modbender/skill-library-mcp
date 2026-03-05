import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

/**
 * Returns the absolute path to the R4 vault skill markdown file.
 * Useful for tools that need to read the skill file directly from disk.
 */
export function getSkillPath(): string {
  return path.join(__dirname, 'SKILL.md')
}

/**
 * The R4 skill content as a string.
 * Contains instructions for agents on how to use R4 as their
 * password manager (vault secrets) and domain registrar (search,
 * purchase, and manage domains), including all available commands,
 * API endpoints, and security rules.
 */
export const skillContent: string = fs.readFileSync(getSkillPath(), 'utf8')
