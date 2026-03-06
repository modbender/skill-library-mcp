/**
 * Export 78 cards from tarot_game to data/cards.json for Python tarot_skill.
 * Run from tarot_skill dir: npx tsx scripts/export_cards_from_tarot_game.ts
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
// @ts-expect-error import from parent tarot_game
import { ALL_CARDS } from "../../tarot_game/constants/tarotCards";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const outPath = path.join(__dirname, "../data/cards.json");

const dir = path.dirname(outPath);
if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });

const serializable = ALL_CARDS.map((c: any) => ({
  id: c.id,
  name: c.name,
  arcana: c.arcana,
  image: c.image,
  meanings: c.meanings,
}));

fs.writeFileSync(outPath, JSON.stringify(serializable, null, 0), "utf-8");
console.log("Written", ALL_CARDS.length, "cards to", outPath);
