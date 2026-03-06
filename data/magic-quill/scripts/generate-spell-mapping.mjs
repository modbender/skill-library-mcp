#!/usr/bin/env node

import { promises as fs } from "node:fs";
import path from "node:path";
import process from "node:process";

const DEFAULT_TOP = 50;
const DEFAULT_AUTHOR = "@spellbook-generator";
const FALLBACK_OUTPUT_DIR = "spells";
const USER_AGENT = "openclaw-spellbook/spell-mapping-generator";
const DND_TOPIC_PATTERN = /\b(?:dnd|d&d|dungeons?\s*(?:and|&)\s*dragons?|5e|5th\s*edition)\b/i;
const DUCKDUCKGO_HTML_SEARCH_URL = "https://duckduckgo.com/html/";
const SPELL_REFERENCE_MIN_NAMES = 5;
const SPELL_REFERENCE_MAX_CANDIDATES = 12;
const SPELL_REFERENCE_SEARCH_RESULTS_PER_QUERY = 6;
const SPELL_REFERENCE_MAX_JSON_NODES = 25000;
const SPELL_REFERENCE_MAX_FOLLOW_DEPTH = 2;
const SPELL_REFERENCE_MAX_FOLLOW_LINKS_PER_PAGE = 4;
const DND_SCHOOL_NAMES = [
  "Abjuration",
  "Conjuration",
  "Divination",
  "Enchantment",
  "Evocation",
  "Illusion",
  "Necromancy",
  "Transmutation"
];
const DND_SCHOOL_LINE_PATTERN = new RegExp(`^(.+?)\\s+(${DND_SCHOOL_NAMES.join("|")})\\b`, "i");
const DND_CLASS_NAMES = [
  "Artificer",
  "Barbarian",
  "Bard",
  "Cleric",
  "Druid",
  "Fighter",
  "Monk",
  "Paladin",
  "Ranger",
  "Rogue",
  "Sorcerer",
  "Warlock",
  "Wizard"
];
const DND_NON_SPELL_NAME_SET = new Set(
  [
    ...DND_CLASS_NAMES,
    ...DND_SCHOOL_NAMES,
    "Spell",
    "Spells",
    "Spells 5e",
    "Spells - DnD 5e",
    "All DnD 5e Spells",
    "Feats",
    "Invocations",
    "Herbs",
    "Poisons",
    "Français",
    "French",
    "English"
  ].map((value) => value.toLowerCase())
);
const SPELL_ENDPOINT_URL_HINT_PATTERN = /(?:^|[/?#._-])spells?(?:[/?#._-]|$)/i;
const SPELL_REFERENCE_LOW_CONFIDENCE_HOST_PATTERN =
  /(^|\.)(?:wikipedia\.org|fandom\.com|wikia\.com|reddit\.com|youtube\.com|youtu\.be|facebook\.com|x\.com|twitter\.com|steamcommunity\.com)$/i;
const SPELL_REFERENCE_UI_LABEL_PATTERN =
  /^(?:home|about|membership|pricing|pricing plans|docs|documentation|api|reference|overview|introduction|quickstart|getting started|guide|guides|tutorial|tutorials|examples?|blog|community|support|contact|faq|changelog|status|terms|privacy|cookies|login|log in|sign in|sign up|register|dashboard|account|settings|menu|search|previous|next|back|forward|top|github|discord|sponsors?|donate|download|install|setup|classes?|subclasses?|races?|subraces?|backgrounds?|equipment|weapons?|armor|armour|items?|magic items?|features?|traits?|conditions?|languages?|skills?|proficiencies?|rules?|rule sections?|sections?|endpoints?|resources?|monsters?|bestiary|damage types?|ability scores?)$/i;

const FALLBACK_POPULAR_SKILLS = [
  "search-web",
  "read-file",
  "write-file",
  "edit-file",
  "create-file",
  "delete-file",
  "list-files",
  "move-file",
  "copy-file",
  "fix-bugs",
  "debug-code",
  "run-tests",
  "lint-code",
  "format-code",
  "build-project",
  "deploy",
  "start-server",
  "stop-server",
  "restart-service",
  "kill-process",
  "install-deps",
  "update-deps",
  "git-status",
  "git-diff",
  "git-commit",
  "git-branch",
  "git-merge",
  "git-rebase",
  "review-code",
  "open-pr",
  "merge-pr",
  "query-db",
  "run-sql",
  "migrate-db",
  "fetch-api",
  "call-api",
  "parse-json",
  "transform-data",
  "extract-data",
  "scrape-web",
  "analyze-logs",
  "monitor-service",
  "backup-data",
  "restore-data",
  "write-docs",
  "summarize-text",
  "translate-text",
  "plan-task",
  "refactor-code",
  "generate-tests",
  "explain-code",
  "package-release",
  "publish-package",
  "docker-build",
  "docker-run",
  "kubectl-apply",
  "terraform-plan",
  "terraform-apply",
  "ci-run",
  "release-notes"
];

const BASE_PROFILE = {
  id: "arcane",
  fallbackIcon: "✨",
  verbs: {
    search: "Divine",
    read: "Study",
    write: "Inscribe",
    create: "Conjure",
    edit: "Etch",
    delete: "Banish",
    deploy: "Summon",
    build: "Forge",
    test: "Trial",
    lint: "Purify",
    format: "Align",
    fix: "Cleanse",
    debug: "Reveal",
    install: "Bind",
    update: "Refine",
    run: "Invoke",
    start: "Awaken",
    stop: "Quell",
    restart: "Rekindle",
    kill: "Sever",
    git: "Archive",
    review: "Appraise",
    plan: "Chart",
    explain: "Illuminate",
    transform: "Transmute",
    extract: "Harvest",
    parse: "Decode",
    query: "Consult",
    monitor: "Scry",
    backup: "Ward",
    restore: "Recall",
    publish: "Proclaim",
    release: "Unseal",
    default: "Invoke"
  },
  objects: {
    web: "the Weave",
    file: "the Grimoire",
    code: "the Runes",
    data: "the Ledger",
    database: "the Archive",
    process: "the Familiar",
    service: "the Beacon",
    api: "the Gate",
    repo: "the Repository",
    docs: "the Codex",
    infra: "the Citadel",
    package: "the Relic",
    tests: "the Trials",
    logs: "the Echoes",
    task: "the Rite",
    default: "the Rite"
  },
  icons: {
    search: "🔮",
    read: "📖",
    write: "📜",
    create: "✨",
    edit: "✍️",
    delete: "🗡️",
    deploy: "🚀",
    build: "⚒️",
    test: "🧪",
    lint: "🧹",
    format: "📐",
    fix: "💧",
    debug: "🕯️",
    install: "🪢",
    update: "♻️",
    run: "⚡",
    start: "🌅",
    stop: "🛑",
    restart: "🔥",
    kill: "⚔️",
    git: "🗃️",
    review: "👁️",
    plan: "🗺️",
    explain: "💡",
    transform: "🧬",
    extract: "⛏️",
    parse: "🔍",
    query: "📡",
    monitor: "📈",
    backup: "🛡️",
    restore: "🕰️",
    publish: "📣",
    release: "📦",
    default: "✨"
  },
  suffixes: ["Echoes", "Sigil", "Ward", "Rite", "Canticle", "Circuit"]
};

const THEME_PROFILES = [
  {
    match: /(harry\s*potter|hogwarts|wizarding|quidditch|dumbledore|voldemort)/i,
    profile: {
      id: "harry-potter",
      verbs: {
        search: "Accio",
        read: "Peruse",
        write: "Inscribe",
        create: "Conjure",
        delete: "Evanesco",
        fix: "Reparo",
        debug: "Revelio",
        deploy: "Apparate",
        kill: "Expelliarmus",
        monitor: "Maraud",
        default: "Cast"
      },
      objects: {
        web: "the Marauder Map",
        file: "the Parchment",
        code: "the Spellbook",
        repo: "the Archives",
        task: "the Charm",
        default: "the Charm"
      },
      icons: {
        default: "🪄",
        debug: "🕵️",
        deploy: "🦉"
      },
      suffixes: ["Patronus", "Pensieve", "Hallows", "Horcrux", "Phoenix"]
    }
  },
  {
    match: /(star\s*wars|jedi|sith|lightsaber|skywalker|mandalorian|force)/i,
    profile: {
      id: "star-wars",
      verbs: {
        search: "Sense",
        read: "Consult",
        write: "Engrave",
        create: "Manifest",
        fix: "Balance",
        debug: "Reveal",
        deploy: "Launch",
        kill: "Strike",
        monitor: "Track",
        default: "Channel"
      },
      objects: {
        web: "the Holonet",
        file: "the Datacard",
        code: "the Holocron",
        repo: "the Jedi Archives",
        process: "the Droid",
        infra: "the Fleet",
        default: "the Force"
      },
      icons: {
        default: "🌌",
        deploy: "🛰️",
        kill: "🗡️"
      },
      suffixes: ["Kyber", "Tatooine", "Coruscant", "Alderaan", "Naboo"]
    }
  },
  {
    match: /(genshin|teyvat|mondstadt|liyue|inazuma|sumeru|fontaine|natlan|snezhnaya)/i,
    profile: {
      id: "genshin",
      verbs: {
        search: "Survey",
        read: "Study",
        write: "Inscribe",
        create: "Conjure",
        fix: "Cleanse",
        deploy: "Ascend",
        debug: "Unveil",
        run: "Resonate",
        default: "Invoke"
      },
      objects: {
        web: "Elemental Sight",
        file: "the Tablet",
        code: "the Leyline",
        process: "the Construct",
        task: "the Resonance",
        default: "the Resonance"
      },
      icons: {
        default: "✨",
        fix: "💧",
        search: "👁️"
      },
      suffixes: ["Anemo", "Geo", "Electro", "Dendro", "Hydro", "Pyro", "Cryo"]
    }
  },
  {
    match: /(cyberpunk|netrunner|edgerunners|night\s*city|neuromancer|mech|android)/i,
    profile: {
      id: "cyberpunk",
      verbs: {
        search: "Trace",
        read: "Scan",
        write: "Patch",
        create: "Compile",
        edit: "Patch",
        fix: "Hotfix",
        debug: "Trace",
        deploy: "Jack-In",
        monitor: "Ping",
        default: "Execute"
      },
      objects: {
        web: "the Grid",
        file: "the Shard",
        code: "the ICE",
        data: "the Datastream",
        repo: "the Blackwall Cache",
        infra: "the Rig",
        process: "the Daemon",
        default: "the Stack"
      },
      icons: {
        default: "🤖",
        monitor: "📡",
        deploy: "🧷"
      },
      suffixes: ["Neon", "Chrome", "ICE", "Daemon", "Blackwall"]
    }
  },
  {
    match: /(pirate|one\s*piece|corsair|buccaneer|captain|kraken|sea|ocean)/i,
    profile: {
      id: "pirate",
      verbs: {
        search: "Scout",
        read: "Chart",
        write: "Log",
        create: "Rig",
        delete: "Scuttle",
        deploy: "Set Sail",
        fix: "Patch",
        monitor: "Spyglass",
        default: "Crew"
      },
      objects: {
        web: "the Horizon",
        file: "the Captain's Log",
        code: "the Map",
        process: "the Cannons",
        repo: "the Hold",
        task: "the Voyage",
        default: "the Voyage"
      },
      icons: {
        default: "🏴‍☠️",
        deploy: "⛵",
        monitor: "🔭"
      },
      suffixes: ["Kraken", "Reef", "Tempest", "Harbor", "Treasure"]
    }
  },
  {
    match: /(marvel|dc\b|avengers|x-men|superhero|batman|superman|spider-man|iron\s*man)/i,
    profile: {
      id: "superhero",
      verbs: {
        search: "Detect",
        read: "Brief",
        write: "Draft",
        create: "Assemble",
        fix: "Stabilize",
        debug: "Expose",
        deploy: "Launch",
        kill: "Neutralize",
        default: "Activate"
      },
      objects: {
        web: "the Network",
        file: "the Dossier",
        code: "the Suit",
        process: "the Threat",
        repo: "the HQ",
        infra: "the Helicarrier",
        default: "the Protocol"
      },
      icons: {
        default: "🦸",
        deploy: "🛫",
        kill: "🛡️"
      },
      suffixes: ["Titan", "Arc", "Shield", "Gamma", "Vibranium"]
    }
  },
  {
    match: /(pokemon|pok[eé]mon|kanto|johto|paldea|trainer|gym|pikachu)/i,
    profile: {
      id: "pokemon",
      verbs: {
        search: "Track",
        read: "Check",
        write: "Teach",
        create: "Summon",
        fix: "Heal",
        deploy: "Send Out",
        monitor: "Observe",
        default: "Use"
      },
      objects: {
        web: "the Pokédex",
        file: "the Pokédex Entry",
        code: "the Move Set",
        process: "the Team Slot",
        data: "the PC Box",
        default: "the Move"
      },
      icons: {
        default: "⚡",
        fix: "💊",
        deploy: "🎯"
      },
      suffixes: ["Kanto", "Johto", "Hoenn", "Sinnoh", "Paldea"]
    }
  }
];

function printHelp() {
  console.log(`Generate a themed OpenClaw spell mapping YAML.

Usage:
  node magic-quill/scripts/generate-spell-mapping.mjs --theme "Wizarding World" [options]
  node magic-quill/scripts/generate-spell-mapping.mjs --topic "Harry Potter" [options]
  node magic-quill/scripts/generate-spell-mapping.mjs --url "https://example.com/wiki/theme" [options]

Options:
  --theme <name>      Explicit theme name (also works without topic/url in heuristic mode)
  --topic <name>      Theme topic/game/movie/franchise name
  --url <url>         URL to fetch lore/context text from
  --out <path>        Output YAML path (default: spells/<theme-slug>.yaml)
  --output <path>     Alias for --out
  --limit <n>         Target coverage count (default: 50)
  --top <n>           Alias for --limit
  --author <name>     YAML author field (default: @spellbook-generator)
  --help              Show this help

Examples:
  npm run generate:spellbook-theme -- --theme "Star Wars" --limit 10 --author "@you"
  npm run generate:spellbook-theme -- --topic "Star Wars" --limit 50 --author "@you"
  npm run generate:spellbook-theme -- --url "https://en.wikipedia.org/wiki/Cyberpunk_2077" --limit 75 --out spells/cyberpunk.yaml
`);
}

function parseArgs(argv) {
  const args = {
    theme: "",
    topic: "",
    url: "",
    output: "",
    top: DEFAULT_TOP,
    author: DEFAULT_AUTHOR
  };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];

    if (token === "--help" || token === "-h") {
      printHelp();
      process.exit(0);
    }

    if (token === "--theme") {
      args.theme = String(argv[index + 1] ?? "").trim();
      index += 1;
      continue;
    }

    if (token === "--topic") {
      args.topic = String(argv[index + 1] ?? "").trim();
      index += 1;
      continue;
    }

    if (token === "--url") {
      args.url = String(argv[index + 1] ?? "").trim();
      index += 1;
      continue;
    }

    if (token === "--out" || token === "--output") {
      args.output = String(argv[index + 1] ?? "").trim();
      index += 1;
      continue;
    }

    if (token === "--top" || token === "--limit") {
      const value = Number.parseInt(String(argv[index + 1] ?? ""), 10);
      if (!Number.isFinite(value) || value <= 0) {
        throw new Error(`${token} must be a positive integer`);
      }
      args.top = value;
      index += 1;
      continue;
    }

    if (token === "--author") {
      args.author = String(argv[index + 1] ?? "").trim();
      index += 1;
      continue;
    }

    throw new Error(`Unknown argument: ${token}`);
  }

  if (!args.theme && !args.topic && !args.url) {
    throw new Error("Provide at least one of --theme, --topic, or --url");
  }

  if (args.url) {
    try {
      new URL(args.url);
    } catch {
      throw new Error(`Invalid --url value: ${args.url}`);
    }
  }

  if (!args.author) {
    args.author = DEFAULT_AUTHOR;
  }

  return args;
}

async function fetchJson(url, headers = {}) {
  const response = await fetch(url, {
    headers: {
      accept: "application/json",
      "user-agent": USER_AGENT,
      ...headers
    }
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status} from ${url}`);
  }

  return response.json();
}

async function fetchText(url, headers = {}) {
  const response = await fetch(url, {
    headers: {
      accept: "text/html,application/xhtml+xml",
      "user-agent": USER_AGENT,
      ...headers
    }
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status} from ${url}`);
  }

  return response.text();
}

function normalizeReferenceSpellName(value) {
  if (typeof value !== "string") {
    return "";
  }

  return decodeHtmlEntities(value)
    .replace(/<[^>]+>/g, " ")
    .replace(/\s+/g, " ")
    .replace(/^["'“”‘’]+|["'“”‘’]+$/g, "")
    .trim();
}

function mergeAndDedupeSpellNames(lists) {
  const merged = [];
  const seen = new Set();

  for (const list of lists) {
    for (const rawName of list) {
      const name = normalizeReferenceSpellName(rawName);
      if (!name) {
        continue;
      }

      const key = name.toLowerCase();
      if (seen.has(key)) {
        continue;
      }

      seen.add(key);
      merged.push(name);
    }
  }

  return merged;
}

function mergeAndDedupeReferenceUrls(values) {
  const merged = [];
  const seen = new Set();

  for (const value of values) {
    const url = canonicalizeReferenceUrl(value);
    if (!url || seen.has(url)) {
      continue;
    }
    seen.add(url);
    merged.push(url);
  }

  return merged;
}

function buildReferenceTopicText({ args, themeName, lore }) {
  return [
    args.topic,
    args.theme,
    themeName,
    args.url,
    lore?.title,
    lore?.summary,
    lore?.text
  ]
    .filter(Boolean)
    .join(" \n ");
}

function safeDecodeURIComponent(value) {
  try {
    return decodeURIComponent(value);
  } catch {
    return value;
  }
}

function canonicalizeReferenceUrl(value) {
  try {
    const url = new URL(String(value).trim());
    if (!/^https?:$/i.test(url.protocol)) {
      return "";
    }
    url.hash = "";
    if (url.pathname !== "/") {
      url.pathname = url.pathname.replace(/\/+$/g, "") || "/";
    }
    return url.toString();
  } catch {
    return "";
  }
}

function unwrapDuckDuckGoResultUrl(rawHref) {
  const decodedHref = decodeHtmlEntities(String(rawHref ?? "").trim());
  if (!decodedHref) {
    return "";
  }

  let href = decodedHref;
  if (href.startsWith("//")) {
    href = `https:${href}`;
  } else if (href.startsWith("/")) {
    href = new URL(href, "https://duckduckgo.com").toString();
  }

  try {
    const parsed = new URL(href);
    const isDuckDuckGo = /(^|\.)duckduckgo\.com$/i.test(parsed.hostname);
    if (!isDuckDuckGo) {
      return canonicalizeReferenceUrl(parsed.toString());
    }

    const unwrapped = parsed.searchParams.get("uddg") || parsed.searchParams.get("rut");
    if (unwrapped) {
      return canonicalizeReferenceUrl(safeDecodeURIComponent(unwrapped));
    }

    return "";
  } catch {
    return canonicalizeReferenceUrl(href);
  }
}

function parseDuckDuckGoResultLinks(html) {
  const links = [];
  const seen = new Set();
  const pattern = /<a\b([^>]*)>([\s\S]*?)<\/a>/gi;
  let match;

  while ((match = pattern.exec(html)) !== null) {
    const attrs = match[1] ?? "";
    if (!/\bclass=["'][^"']*result__a[^"']*["']/i.test(attrs)) {
      continue;
    }

    const hrefMatch = attrs.match(/\bhref=["']([^"']+)["']/i);
    if (!hrefMatch) {
      continue;
    }

    const url = unwrapDuckDuckGoResultUrl(hrefMatch[1]);
    if (!url) {
      continue;
    }

    if (seen.has(url)) {
      continue;
    }
    seen.add(url);
    links.push(url);
  }

  return links;
}

function buildSpellReferenceSearchQueries({ args, themeName, lore }) {
  const seeds = [];
  const seen = new Set();

  for (const value of [args.topic, args.theme, themeName]) {
    const normalized = String(value ?? "").replace(/\s+/g, " ").trim();
    if (!normalized) {
      continue;
    }
    const key = normalized.toLowerCase();
    if (seen.has(key)) {
      continue;
    }
    seen.add(key);
    seeds.push(normalized);
  }

  const topicText = buildReferenceTopicText({ args, themeName, lore });
  if (DND_TOPIC_PATTERN.test(topicText)) {
    const dndSeed = "D&D 5e";
    if (!seen.has(dndSeed.toLowerCase())) {
      seen.add(dndSeed.toLowerCase());
      seeds.unshift(dndSeed);
    }
  }

  const queries = [];
  const querySeen = new Set();

  for (const seed of seeds) {
    for (const suffix of ["spell list", "spells api"]) {
      const query = `${seed} ${suffix}`.trim();
      const key = query.toLowerCase();
      if (querySeen.has(key)) {
        continue;
      }
      querySeen.add(key);
      queries.push(query);
    }
  }

  return queries.slice(0, 6);
}

function scoreSpellReferenceCandidate(candidate) {
  const urlValue = canonicalizeReferenceUrl(candidate?.url);
  if (!urlValue) {
    return Number.NEGATIVE_INFINITY;
  }

  let score = 0;
  if (candidate?.source === "input-url") {
    score += 120;
  }
  if (typeof candidate?.rank === "number" && Number.isFinite(candidate.rank)) {
    score += Math.max(0, 20 - candidate.rank * 2);
  }

  const query = String(candidate?.query ?? "").toLowerCase();
  if (query.includes("spells api")) {
    score += 20;
  } else if (query.includes("spell list")) {
    score += 10;
  }

  try {
    const parsed = new URL(urlValue);
    const host = parsed.hostname.toLowerCase();
    const pathText = `${parsed.pathname} ${parsed.search}`.toLowerCase();

    if (SPELL_REFERENCE_LOW_CONFIDENCE_HOST_PATTERN.test(host)) {
      score -= 50;
    }
    if (/\b(?:api|developer)\b/i.test(host)) {
      score += 18;
    }
    if (SPELL_ENDPOINT_URL_HINT_PATTERN.test(pathText)) {
      score += 70;
    } else if (/\bspell/i.test(pathText)) {
      score += 35;
    }
    if (/\/(?:api|v\d+)(?:\/|$)/i.test(parsed.pathname)) {
      score += 15;
    }
    if (/\b(?:docs?|swagger|openapi|redoc|reference)\b/i.test(pathText)) {
      score += 8;
    }
    if (/\/wiki\//i.test(parsed.pathname)) {
      score -= 30;
    }
    if (/\b(?:lore|story|background|history)\b/i.test(pathText)) {
      score -= 20;
    }
    if (/\.(?:pdf|jpg|jpeg|png|gif|svg|webp|zip|tar|gz)$/i.test(parsed.pathname)) {
      score -= 80;
    }
  } catch {
    score -= 10;
  }

  return score;
}

function dedupeReferenceCandidates(candidates) {
  const sortedCandidates = [...candidates]
    .map((candidate) => ({
      ...candidate,
      confidence: scoreSpellReferenceCandidate(candidate)
    }))
    .sort((a, b) => {
      if (b.confidence !== a.confidence) {
        return b.confidence - a.confidence;
      }
      if (typeof a.rank === "number" && typeof b.rank === "number" && a.rank !== b.rank) {
        return a.rank - b.rank;
      }
      return String(a.url ?? "").localeCompare(String(b.url ?? ""));
    });

  const deduped = [];
  const seen = new Set();

  for (const candidate of sortedCandidates) {
    const normalizedUrl = canonicalizeReferenceUrl(candidate?.url);
    if (!normalizedUrl) {
      continue;
    }
    if (seen.has(normalizedUrl)) {
      continue;
    }
    seen.add(normalizedUrl);
    deduped.push({
      ...candidate,
      url: normalizedUrl
    });
    if (deduped.length >= SPELL_REFERENCE_MAX_CANDIDATES) {
      break;
    }
  }

  return deduped;
}

async function searchSpellReferenceCandidates(query) {
  const endpoint = new URL(DUCKDUCKGO_HTML_SEARCH_URL);
  endpoint.searchParams.set("q", query);

  const html = await fetchText(endpoint.toString(), {
    accept: "text/html,application/xhtml+xml",
    referer: "https://duckduckgo.com/"
  });

  return parseDuckDuckGoResultLinks(html).slice(0, SPELL_REFERENCE_SEARCH_RESULTS_PER_QUERY);
}

async function discoverSpellListReferences({ args, themeName, lore }) {
  const warnings = [];
  const queries = buildSpellReferenceSearchQueries({ args, themeName, lore });
  const candidates = [];

  if (args.url) {
    candidates.push({
      url: args.url,
      source: "input-url",
      query: "",
      rank: 0
    });
  }

  if (queries.length > 0) {
    const settled = await Promise.allSettled(queries.map((query) => searchSpellReferenceCandidates(query)));

    for (let index = 0; index < settled.length; index += 1) {
      const query = queries[index];
      const result = settled[index];

      if (result.status !== "fulfilled") {
        warnings.push(`spell list search failed (${query}): ${result.reason?.message ?? String(result.reason)}`);
        continue;
      }

      for (let rank = 0; rank < result.value.length; rank += 1) {
        candidates.push({
          url: result.value[rank],
          source: "duckduckgo",
          query,
          rank: rank + 1
        });
      }
    }
  }

  return {
    candidates: dedupeReferenceCandidates(candidates),
    warnings,
    debug: {
      queries
    }
  };
}

function countMatches(input, pattern) {
  if (!input) {
    return 0;
  }

  const flags = pattern.flags.includes("g") ? pattern.flags : `${pattern.flags}g`;
  const matcher = new RegExp(pattern.source, flags);
  let count = 0;
  while (matcher.exec(input) !== null) {
    count += 1;
  }
  return count;
}

function isLikelySpellName(value) {
  const name = normalizeReferenceSpellName(value);
  if (!name) {
    return false;
  }
  if (name.length < 2 || name.length > 90) {
    return false;
  }
  if (/https?:\/\//i.test(name)) {
    return false;
  }
  if (/[<>{}\[\]]/.test(name)) {
    return false;
  }
  if ((name.match(/[A-Za-z]/g) ?? []).length < 2) {
    return false;
  }
  if (name.split(/\s+/).length > 8) {
    return false;
  }
  if ((name.match(/[,:;.!?]/g) ?? []).length > 2) {
    return false;
  }
  if (
    /\b(?:all spells?|spell list|search|filter|sort|navigation|privacy|terms|login|sign in|register)\b/i.test(
      name
    )
  ) {
    return false;
  }
  if (SPELL_REFERENCE_UI_LABEL_PATTERN.test(name)) {
    return false;
  }
  if (
    /\b(?:casting time|components?|concentration|duration|range|class(?:es)?|subclass|description)\b/i.test(name)
  ) {
    return false;
  }
  if (/^(?:name|level|school|source|ritual|cantrip|spell name)$/i.test(name)) {
    return false;
  }
  if (/^(?:get|post|put|patch|delete)\s+/i.test(name)) {
    return false;
  }
  if (/^[A-Z][A-Z0-9_ -]+$/.test(name) && !/[a-z]/.test(name)) {
    return false;
  }

  return true;
}

function isDndReferenceTopic(topicText) {
  return DND_TOPIC_PATTERN.test(String(topicText ?? ""));
}

function isDndNonSpellName(name) {
  const normalized = normalizeReferenceSpellName(name).toLowerCase();
  return DND_NON_SPELL_NAME_SET.has(normalized);
}

function scoreReferenceSpellNameCandidate(name, options = {}) {
  const normalized = normalizeReferenceSpellName(name);
  if (!normalized) {
    return Number.NEGATIVE_INFINITY;
  }

  const sourceUrl = String(options.sourceUrl ?? "");
  const isDndTopic = Boolean(options.isDndTopic);
  let score = 0;

  const tokenCount = normalized.split(/\s+/).filter(Boolean).length;
  if (tokenCount >= 2 && tokenCount <= 4) {
    score += 2;
  } else if (tokenCount === 1) {
    score += 0.5;
  }

  if (/\bspell/i.test(sourceUrl)) {
    score += 1;
  }

  if (/\b(?:api|docs?|reference|guide|tutorial|wiki|list|table|index|catalog)\b/i.test(normalized)) {
    score -= 8;
  }
  if (/\b(?:classes?|subclasses?|schools?|feats?|invocations?|herbs?|poisons?)\b/i.test(normalized)) {
    score -= 8;
  }
  if (/\b(?:all|every|full|complete)\b/i.test(normalized) && /\bspells?\b/i.test(normalized)) {
    score -= 12;
  }

  if (isDndTopic) {
    if (isDndNonSpellName(normalized)) {
      score -= 20;
    }
    if (/\b(?:fran[cç]ais|french|english|deutsch|espa[ñn]ol)\b/i.test(normalized)) {
      score -= 10;
    }
  }

  return score;
}

function rankReferenceSpellNames(referenceResults, options = {}) {
  const topicText = String(options.topicText ?? "");
  const isDndTopic = isDndReferenceTopic(topicText);
  const byName = new Map();

  for (const reference of referenceResults) {
    const sourceUrl = canonicalizeReferenceUrl(reference?.url) || String(reference?.url ?? "");
    const localSeen = new Set();

    for (const rawName of reference?.names ?? []) {
      const normalized = normalizeReferenceSpellName(rawName);
      if (!isLikelySpellName(normalized)) {
        continue;
      }

      const key = normalized.toLowerCase();
      if (localSeen.has(key)) {
        continue;
      }
      localSeen.add(key);

      const entry =
        byName.get(key) ?? {
          name: normalized,
          score: 0,
          sourceCount: 0,
          sources: new Set()
        };

      entry.score += scoreReferenceSpellNameCandidate(normalized, {
        isDndTopic,
        sourceUrl
      });

      if (!entry.sources.has(sourceUrl)) {
        entry.sources.add(sourceUrl);
        entry.sourceCount += 1;
      }

      byName.set(key, entry);
    }
  }

  const ranked = [...byName.values()]
    .map((entry) => ({
      ...entry,
      score: entry.score + Math.max(0, entry.sourceCount - 1) * 3
    }))
    .filter((entry) => {
      if (isDndTopic && isDndNonSpellName(entry.name)) {
        return false;
      }
      return entry.score >= (isDndTopic ? 2 : 1);
    })
    .sort((a, b) => {
      if (b.score !== a.score) {
        return b.score - a.score;
      }
      if (b.sourceCount !== a.sourceCount) {
        return b.sourceCount - a.sourceCount;
      }
      return a.name.localeCompare(b.name);
    });

  return ranked.map((entry) => entry.name);
}

function objectLooksSpellLike(value, pathSegments, sourceUrl) {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return false;
  }

  const keys = Object.keys(value);
  const lowerKeys = keys.map((key) => key.toLowerCase());
  const lowerPath = pathSegments.map((segment) => segment.toLowerCase());
  const source = String(sourceUrl ?? "").toLowerCase();

  if (lowerPath.some((segment) => segment.includes("spell"))) {
    return true;
  }
  if (lowerKeys.some((key) => key.includes("spell"))) {
    return true;
  }
  if (
    lowerKeys.some((key) =>
      [
        "level",
        "school",
        "components",
        "casting_time",
        "castingtime",
        "duration",
        "range",
        "ritual",
        "concentration",
        "higher_level",
        "classes"
      ].includes(key)
    )
  ) {
    return true;
  }
  if (source.includes("spell")) {
    return true;
  }

  for (const key of ["url", "href", "link", "api_url", "resource_url", "slug", "index"]) {
    if (typeof value[key] === "string" && /spell/i.test(value[key])) {
      return true;
    }
  }

  return false;
}

function collectSpellNamesFromJsonValue(value, state, pathSegments = []) {
  if (state.nodesVisited >= SPELL_REFERENCE_MAX_JSON_NODES) {
    return;
  }
  state.nodesVisited += 1;

  if (Array.isArray(value)) {
    const pathHasSpellHint = pathSegments.some((segment) => /spell/i.test(segment));

    for (const item of value) {
      if (typeof item === "string" && pathHasSpellHint && isLikelySpellName(item)) {
        state.names.push(item);
        continue;
      }
      collectSpellNamesFromJsonValue(item, state, pathSegments);
      if (state.nodesVisited >= SPELL_REFERENCE_MAX_JSON_NODES) {
        return;
      }
    }
    return;
  }

  if (!value || typeof value !== "object") {
    return;
  }

  if (typeof value.name === "string" && objectLooksSpellLike(value, pathSegments, state.sourceUrl) && isLikelySpellName(value.name)) {
    state.names.push(value.name);
  }

  for (const [key, child] of Object.entries(value)) {
    collectSpellNamesFromJsonValue(child, state, [...pathSegments, key]);
    if (state.nodesVisited >= SPELL_REFERENCE_MAX_JSON_NODES) {
      return;
    }
  }
}

function extractSpellNamesFromJsonPayload(payload, reference) {
  const state = {
    names: [],
    nodesVisited: 0,
    sourceUrl: reference.url
  };

  collectSpellNamesFromJsonValue(payload, state);
  return mergeAndDedupeSpellNames([state.names]).filter(isLikelySpellName);
}

function extractHtmlAnchors(html, baseUrl) {
  const anchors = [];
  const pattern = /<a\b[^>]*href=["']([^"']+)["'][^>]*>([\s\S]*?)<\/a>/gi;
  let match;

  while ((match = pattern.exec(html)) !== null) {
    const rawHref = decodeHtmlEntities(match[1]);
    const text = normalizeReferenceSpellName(match[2]);
    if (!text) {
      continue;
    }

    let resolvedHref = rawHref;
    try {
      resolvedHref = new URL(rawHref, baseUrl).toString();
    } catch {
      resolvedHref = rawHref;
    }

    anchors.push({
      href: resolvedHref,
      text
    });
  }

  return anchors;
}

function resolveReferenceCandidateUrl(rawValue, baseUrl) {
  const value = String(rawValue ?? "").trim();
  if (!value) {
    return "";
  }

  try {
    return canonicalizeReferenceUrl(new URL(value, baseUrl).toString());
  } catch {
    return "";
  }
}

function scoreLikelySpellEndpointUrl(url, baseUrl = "") {
  const normalized = canonicalizeReferenceUrl(url);
  if (!normalized) {
    return Number.NEGATIVE_INFINITY;
  }

  let score = 0;
  try {
    const parsed = new URL(normalized);
    const path = parsed.pathname.toLowerCase();
    const text = `${parsed.pathname} ${parsed.search}`.toLowerCase();

    if (SPELL_ENDPOINT_URL_HINT_PATTERN.test(text)) {
      score += 80;
    } else if (/\bspell/i.test(text)) {
      score += 40;
    }
    if (/\/(?:api|v\d+)(?:\/|$)/i.test(parsed.pathname)) {
      score += 20;
    }
    if (/\.(?:json)$/i.test(parsed.pathname)) {
      score += 10;
    }
    if (/\b(?:docs?|swagger|openapi|redoc|reference)\b/i.test(text) && !SPELL_ENDPOINT_URL_HINT_PATTERN.test(text)) {
      score -= 10;
    }
    if (/\/wiki\//i.test(path)) {
      score -= 25;
    }
    if (SPELL_REFERENCE_LOW_CONFIDENCE_HOST_PATTERN.test(parsed.hostname)) {
      score -= 30;
    }

    if (baseUrl) {
      try {
        const base = new URL(baseUrl);
        if (base.origin === parsed.origin) {
          score += 12;
        } else {
          score -= 8;
        }
      } catch {
        // noop
      }
    }
  } catch {
    return Number.NEGATIVE_INFINITY;
  }

  return score;
}

function rankLikelySpellEndpointUrls(urls, baseUrl) {
  const scored = [];
  const seen = new Set();

  for (const rawUrl of urls) {
    const normalized = resolveReferenceCandidateUrl(rawUrl, baseUrl);
    if (!normalized || seen.has(normalized)) {
      continue;
    }
    seen.add(normalized);
    const score = scoreLikelySpellEndpointUrl(normalized, baseUrl);
    if (score < 25) {
      continue;
    }
    scored.push({ url: normalized, score });
  }

  scored.sort((a, b) => {
    if (b.score !== a.score) {
      return b.score - a.score;
    }
    return a.url.localeCompare(b.url);
  });

  return scored.slice(0, SPELL_REFERENCE_MAX_FOLLOW_LINKS_PER_PAGE);
}

function inferCommonSpellEndpointUrls(baseUrl) {
  const normalizedBase = canonicalizeReferenceUrl(baseUrl);
  if (!normalizedBase) {
    return [];
  }

  let parsed;
  try {
    parsed = new URL(normalizedBase);
  } catch {
    return [];
  }

  const candidates = [];
  const path = parsed.pathname.toLowerCase();
  const looksLikeDocsOrRoot =
    path === "/" || /\b(?:docs?|swagger|openapi|redoc|reference|api)\b/i.test(`${parsed.pathname} ${parsed.search}`);

  if (looksLikeDocsOrRoot) {
    candidates.push(`${parsed.origin}/api/spells`);
    candidates.push(`${parsed.origin}/spells`);
    candidates.push(`${parsed.origin}/api/v1/spells`);
    candidates.push(`${parsed.origin}/v1/spells`);
  }

  return rankLikelySpellEndpointUrls(candidates, normalizedBase);
}

function extractLikelySpellEndpointUrlsFromHtml(html, baseUrl) {
  const candidates = [];

  for (const anchor of extractHtmlAnchors(html, baseUrl)) {
    if (/\bspell/i.test(`${anchor.text} ${anchor.href}`)) {
      candidates.push(anchor.href);
    }
  }

  const urlLikePattern =
    /["']((?:https?:\/\/[^"'#<>\s]+|\/[^"'#<>]*spell[^"'#<>]*|[^"'#<>]*\/api\/[^"'#<>]*spell[^"'#<>]*))["']/gi;

  let match;
  while ((match = urlLikePattern.exec(html)) !== null) {
    if (/\bspell/i.test(match[1])) {
      candidates.push(decodeHtmlEntities(match[1]));
    }
  }

  return rankLikelySpellEndpointUrls(candidates, baseUrl);
}

function collectLikelySpellEndpointUrlsFromJsonValue(value, state, pathSegments = []) {
  if (state.nodesVisited >= SPELL_REFERENCE_MAX_JSON_NODES) {
    return;
  }
  state.nodesVisited += 1;

  if (typeof value === "string") {
    const joinedPath = pathSegments.join(".").toLowerCase();
    if (/\bspell/i.test(value) || joinedPath.includes("spell")) {
      state.urls.push(value);
    }
    return;
  }

  if (Array.isArray(value)) {
    for (const item of value) {
      collectLikelySpellEndpointUrlsFromJsonValue(item, state, pathSegments);
      if (state.nodesVisited >= SPELL_REFERENCE_MAX_JSON_NODES) {
        return;
      }
    }
    return;
  }

  if (!value || typeof value !== "object") {
    return;
  }

  for (const [key, child] of Object.entries(value)) {
    collectLikelySpellEndpointUrlsFromJsonValue(child, state, [...pathSegments, key]);
    if (state.nodesVisited >= SPELL_REFERENCE_MAX_JSON_NODES) {
      return;
    }
  }
}

function extractLikelySpellEndpointUrlsFromJsonPayload(payload, baseUrl) {
  const state = {
    urls: [],
    nodesVisited: 0
  };

  collectLikelySpellEndpointUrlsFromJsonValue(payload, state);
  return rankLikelySpellEndpointUrls(state.urls, baseUrl);
}

function shouldProbeNestedSpellEndpoints(finalUrl, bestParserKind, parsedNameCount) {
  if (bestParserKind !== "html") {
    return false;
  }

  if (parsedNameCount < SPELL_REFERENCE_MIN_NAMES * 3) {
    return true;
  }

  try {
    const parsed = new URL(finalUrl);
    const pathText = `${parsed.pathname} ${parsed.search}`.toLowerCase();
    if (/\b(?:docs?|swagger|openapi|redoc|reference)\b/i.test(pathText)) {
      return true;
    }
    if (/^\/?$/.test(parsed.pathname) && /\b(?:api|developer)\b/i.test(parsed.hostname)) {
      return true;
    }
  } catch {
    return false;
  }

  return false;
}

function extractSpellNamesFromHtmlPayload(html, reference) {
  const title = extractTitle(html);
  const text = stripHtmlToText(html);
  const signalText = `${reference.url}\n${title}\n${text.slice(0, 12000)}`;
  const spellSignalScore =
    countMatches(signalText, /\bspells?\b/i) +
    countMatches(signalText, /\b(?:cantrip|ritual|school|casting time|spell name)\b/i);

  if (spellSignalScore === 0) {
    return [];
  }

  const names = [];
  const addName = (candidate) => {
    const normalized = normalizeReferenceSpellName(candidate);
    if (!isLikelySpellName(normalized)) {
      return;
    }
    if (SPELL_REFERENCE_UI_LABEL_PATTERN.test(normalized)) {
      return;
    }
    if (/\b(?:endpoint|resource|documentation|openapi|swagger|redoc)\b/i.test(normalized)) {
      return;
    }
    names.push(normalized);
  };

  for (const rawLine of text.split(/\n+/)) {
    const line = rawLine.trim();
    if (!line) {
      continue;
    }

    const dndMatch = line.match(DND_SCHOOL_LINE_PATTERN);
    if (dndMatch) {
      addName(dndMatch[1]);
      continue;
    }

    if (line.includes("|") && /\b(?:school|level|ritual|components?|range|duration)\b/i.test(line)) {
      const [firstCell] = line.split("|");
      addName(firstCell);
      continue;
    }

    if (/\s+-\s+/.test(line) && /\b(?:school|level|ritual|components?|range|duration)\b/i.test(line)) {
      const [beforeMeta] = line.split(/\s+-\s+/, 1);
      addName(beforeMeta);
      continue;
    }

    if (
      spellSignalScore >= 4 &&
      isLikelySpellName(line) &&
      !/\b(?:api|docs?|reference|endpoint|resource|guide|tutorial)\b/i.test(line)
    ) {
      addName(line.replace(/^[*•-]\s+/, ""));
    }
  }

  for (const anchor of extractHtmlAnchors(html, reference.url)) {
    const hrefText = `${anchor.href} ${anchor.text}`;
    const hrefHasSpellHint = /\bspell/i.test(anchor.href);
    const textHasSpellHint = /\bspell/i.test(anchor.text);
    if (!hrefHasSpellHint && !textHasSpellHint && spellSignalScore < 5) {
      continue;
    }
    if (!hrefHasSpellHint && SPELL_REFERENCE_UI_LABEL_PATTERN.test(anchor.text)) {
      continue;
    }
    addName(anchor.text);
  }

  return mergeAndDedupeSpellNames([names]);
}

function looksLikeJsonPayload(text, contentType) {
  const normalizedType = String(contentType ?? "").toLowerCase();
  if (normalizedType.includes("json")) {
    return true;
  }
  const trimmed = String(text ?? "").trimStart();
  return trimmed.startsWith("{") || trimmed.startsWith("[");
}

function looksLikeHtmlPayload(text, contentType) {
  const normalizedType = String(contentType ?? "").toLowerCase();
  if (normalizedType.includes("html") || normalizedType.includes("xml")) {
    return true;
  }
  return /<!doctype html|<html\b|<body\b|<table\b|<a\b/i.test(String(text ?? "").slice(0, 2000));
}

async function fetchSpellListReference(reference, context = {}) {
  const depth = Number.isFinite(context.depth) ? Number(context.depth) : 0;
  const visited = context.visited instanceof Set ? context.visited : new Set();
  const trail = Array.isArray(context.trail) ? context.trail : [];
  const requestedUrl = canonicalizeReferenceUrl(reference.url) || reference.url;

  if (requestedUrl && visited.has(requestedUrl)) {
    throw new Error(`Already visited ${requestedUrl}`);
  }
  if (requestedUrl) {
    visited.add(requestedUrl);
  }

  const response = await fetch(reference.url, {
    headers: {
      accept: "application/json,text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
      "user-agent": USER_AGENT
    }
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status} from ${reference.url}`);
  }

  const finalUrl = canonicalizeReferenceUrl(response.url || reference.url) || reference.url;
  if (finalUrl) {
    visited.add(finalUrl);
  }

  const contentType = response.headers.get("content-type") || "";
  const text = await response.text();
  const parserResults = [];
  const parseErrors = [];
  let jsonPayload = null;
  let htmlPayload = "";

  if (looksLikeJsonPayload(text, contentType)) {
    try {
      jsonPayload = JSON.parse(text);
      const names = extractSpellNamesFromJsonPayload(jsonPayload, { ...reference, url: finalUrl });
      if (names.length > 0) {
        parserResults.push({ kind: "json", names });
      }
    } catch (error) {
      parseErrors.push(`json parse failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  if (looksLikeHtmlPayload(text, contentType) || parserResults.length === 0) {
    htmlPayload = text;
    const names = extractSpellNamesFromHtmlPayload(text, { ...reference, url: finalUrl });
    if (names.length > 0) {
      parserResults.push({ kind: "html", names });
    }
  }

  const mergedNames = mergeAndDedupeSpellNames(parserResults.map((entry) => entry.names));
  const bestParser = parserResults
    .slice()
    .sort((a, b) => b.names.length - a.names.length)[0];

  const shouldFollow =
    depth < SPELL_REFERENCE_MAX_FOLLOW_DEPTH &&
    (mergedNames.length < SPELL_REFERENCE_MIN_NAMES ||
      shouldProbeNestedSpellEndpoints(finalUrl, bestParser?.kind ?? "unknown", mergedNames.length));

  if (shouldFollow) {
    const followCandidates = rankLikelySpellEndpointUrls(
      [
        ...(jsonPayload ? extractLikelySpellEndpointUrlsFromJsonPayload(jsonPayload, finalUrl).map((entry) => entry.url) : []),
        ...(htmlPayload ? extractLikelySpellEndpointUrlsFromHtml(htmlPayload, finalUrl).map((entry) => entry.url) : []),
        ...inferCommonSpellEndpointUrls(finalUrl).map((entry) => entry.url)
      ],
      finalUrl
    );

    const followErrors = [];

    for (const nextCandidate of followCandidates) {
      if (nextCandidate.url === finalUrl || visited.has(nextCandidate.url)) {
        continue;
      }

      try {
        const nested = await fetchSpellListReference(
          {
            ...reference,
            url: nextCandidate.url,
            source: `${reference.source}:follow`
          },
          {
            depth: depth + 1,
            visited,
            trail: [...trail, finalUrl]
          }
        );

        return {
          ...nested,
          referenceUrls: mergeAndDedupeReferenceUrls([finalUrl, ...(nested.referenceUrls ?? [nested.url])])
        };
      } catch (error) {
        followErrors.push(`${nextCandidate.url}: ${error instanceof Error ? error.message : String(error)}`);
      }
    }

    if (followErrors.length > 0) {
      parseErrors.push(`follow-up failed: ${followErrors.join(" | ")}`);
    }
  }

  if (mergedNames.length < SPELL_REFERENCE_MIN_NAMES) {
    const details =
      parseErrors.length > 0 ? ` (${parseErrors.join("; ")})` : mergedNames.length > 0 ? "" : " (no parsable spell names)";
    throw new Error(`Only ${mergedNames.length} spell names parsed from ${finalUrl}${details}`);
  }

  return {
    url: finalUrl,
    count: mergedNames.length,
    parser: bestParser?.kind ?? "unknown",
    names: mergedNames,
    referenceUrls: mergeAndDedupeReferenceUrls([finalUrl, ...trail])
  };
}

async function gatherReferenceSpellNames({ args, themeName, lore }) {
  const warnings = [];
  const discovery = await discoverSpellListReferences({ args, themeName, lore });
  warnings.push(...discovery.warnings);
  const references = discovery.candidates;

  if (references.length === 0) {
    return {
      spellNames: [],
      warnings,
      debug: {
        queries: discovery.debug.queries,
        attempted: [],
        succeeded: [],
        sample: []
      }
    };
  }

  const settled = await Promise.allSettled(references.map((reference) => fetchSpellListReference(reference)));
  const successfulReferences = [];
  const succeeded = [];

  for (let index = 0; index < settled.length; index += 1) {
    const reference = references[index];
    const result = settled[index];

    if (result.status === "fulfilled") {
      successfulReferences.push({
        url: result.value.url,
        names: result.value.names
      });
      succeeded.push({
        url: result.value.url,
        count: result.value.count,
        parser: result.value.parser,
        referenceUrls: Array.isArray(result.value.referenceUrls) ? result.value.referenceUrls : [result.value.url]
      });
      continue;
    }

    warnings.push(`spell list reference fetch failed (${reference.url}): ${result.reason?.message ?? String(result.reason)}`);
  }

  const topicText = buildReferenceTopicText({ args, themeName, lore });
  const rankedSpellNames = rankReferenceSpellNames(successfulReferences, { topicText });
  const fallbackSpellNames = mergeAndDedupeSpellNames(successfulReferences.map((entry) => entry.names));
  const spellNames = rankedSpellNames.length > 0 ? rankedSpellNames : fallbackSpellNames;

  return {
    spellNames,
    warnings,
    debug: {
      queries: discovery.debug.queries,
      attempted: references.map((reference) => ({
        url: reference.url,
        source: reference.source,
        query: reference.query,
        rank: reference.rank,
        confidence: reference.confidence
      })),
      succeeded,
      sample: spellNames.slice(0, 10)
    }
  };
}

function decodeEscaped(value) {
  return value
    .replaceAll('\\\\\"', '"')
    .replaceAll("\\\\/", "/")
    .replaceAll("\\\\\\\\", "\\");
}

function parseSkillsShEntries(html) {
  const pattern =
    /\\\"source\\\":\\\"([^\\\"]+)\\\",\\\"skillId\\\":\\\"([^\\\"]+)\\\",\\\"name\\\":\\\"([^\\\"]+)\\\",\\\"installs\\\":(\d+)(?:,\\\"installsYesterday\\\":(\d+),\\\"change\\\":(-?\d+))?/g;

  const seen = new Set();
  const rows = [];
  let match;

  while ((match = pattern.exec(html)) !== null) {
    const sourcePath = decodeEscaped(match[1]);
    const skillId = decodeEscaped(match[2]);
    const name = decodeEscaped(match[3]);
    const installs = Number.parseInt(match[4], 10);
    const key = `${sourcePath}::${skillId}`;

    if (seen.has(key)) {
      continue;
    }

    seen.add(key);
    rows.push({
      sourcePath,
      skillId,
      name,
      installs
    });
  }

  return rows;
}

async function fetchSkillsShTrending(limit) {
  const html = await fetchText("https://skills.sh/trending");
  const rows = parseSkillsShEntries(html);

  if (rows.length === 0) {
    throw new Error("No skills parsed from skills.sh trending page");
  }

  return rows.slice(0, limit).map((row, index) => ({
    rank: index + 1,
    skillId: row.skillId,
    displayName: row.name,
    metricValue: row.installs,
    sourcePath: row.sourcePath
  }));
}

function normalizeSkillId(value) {
  if (value === null || value === undefined) {
    return null;
  }

  let next = String(value).trim().toLowerCase();
  if (!next) {
    return null;
  }

  if (next.includes("/")) {
    next = next.split("/").pop() ?? next;
  }

  next = next
    .replace(/[^a-z0-9-]+/g, "-")
    .replace(/-{2,}/g, "-")
    .replace(/^-+|-+$/g, "");

  if (!next || !/^[a-z0-9][a-z0-9-]*$/.test(next)) {
    return null;
  }

  return next;
}

async function fetchClawhubDownloads(limit) {
  const endpoints = [
    "https://wry-manatee-359.convex.site/api/v1/skills",
    "https://clawhub.ai/api/v1/skills",
    "https://api.clawhub.ai/v1/skills"
  ];

  let lastError = null;

  for (const baseUrl of endpoints) {
    try {
      const endpoint = new URL(baseUrl);
      endpoint.searchParams.set("sort", "downloads");
      endpoint.searchParams.set("nonSuspicious", "true");
      endpoint.searchParams.set("limit", String(limit));

      const payload = await fetchJson(endpoint.toString());
      const rawItems = Array.isArray(payload)
        ? payload
        : Array.isArray(payload.items)
          ? payload.items
          : [];

      const items = rawItems
        .map((item, index) => {
          const skillId =
            normalizeSkillId(item.skillId) ||
            normalizeSkillId(item.slug) ||
            normalizeSkillId(item.name) ||
            normalizeSkillId(item.displayName);

          if (!skillId) {
            return null;
          }

          return {
            rank: index + 1,
            skillId,
            displayName:
              item.displayName ||
              item.name ||
              item.title ||
              item.slug ||
              item.skillId ||
              skillId,
            metricValue:
              Number(item.stats?.downloads) ||
              Number(item.downloads) ||
              Number(item.installs) ||
              0
          };
        })
        .filter(Boolean);

      if (items.length === 0) {
        throw new Error(`No skill items parsed from ${baseUrl}`);
      }

      return {
        items: items.slice(0, limit),
        apiUrl: endpoint.toString()
      };
    } catch (error) {
      lastError = error;
    }
  }

  throw lastError instanceof Error ? lastError : new Error(String(lastError));
}

function mergePopularSkills({ skillsShItems, clawhubItems, targetCount }) {
  const merged = new Map();

  function touch(sourceName, items) {
    for (const item of items) {
      const skillId = normalizeSkillId(item.skillId);
      if (!skillId) {
        continue;
      }

      const entry =
        merged.get(skillId) ??
        {
          skillId,
          score: 0,
          bestRank: Number.POSITIVE_INFINITY,
          sources: new Set(),
          names: new Set()
        };

      const weight = Math.max(targetCount * 2 - item.rank + 1, 1);
      entry.score += weight;
      entry.bestRank = Math.min(entry.bestRank, item.rank);
      entry.sources.add(sourceName);
      if (item.displayName) {
        entry.names.add(String(item.displayName));
      }

      merged.set(skillId, entry);
    }
  }

  touch("skills.sh", skillsShItems);
  touch("clawhub", clawhubItems);

  const ranked = [...merged.values()]
    .map((entry) => ({
      skillId: entry.skillId,
      score: entry.score + (entry.sources.size > 1 ? targetCount : 0),
      bestRank: entry.bestRank,
      sourceCount: entry.sources.size,
      sources: [...entry.sources].sort(),
      displayName: [...entry.names][0] ?? entry.skillId
    }))
    .sort((a, b) => {
      if (b.score !== a.score) {
        return b.score - a.score;
      }
      if (a.bestRank !== b.bestRank) {
        return a.bestRank - b.bestRank;
      }
      return a.skillId.localeCompare(b.skillId);
    });

  const ids = [];
  const seen = new Set();

  for (const item of ranked) {
    if (seen.has(item.skillId)) {
      continue;
    }
    seen.add(item.skillId);
    ids.push(item.skillId);
    if (ids.length >= targetCount) {
      break;
    }
  }

  for (const skillId of FALLBACK_POPULAR_SKILLS) {
    if (seen.has(skillId)) {
      continue;
    }
    seen.add(skillId);
    ids.push(skillId);
    if (ids.length >= targetCount) {
      break;
    }
  }

  return ids;
}

function decodeHtmlEntities(input) {
  if (!input) {
    return "";
  }

  const named = new Map([
    ["amp", "&"],
    ["lt", "<"],
    ["gt", ">"],
    ["quot", '"'],
    ["apos", "'"],
    ["nbsp", " "]
  ]);

  return input.replace(/&(#x?[0-9a-f]+|[a-z]+);/gi, (full, code) => {
    const normalized = String(code).toLowerCase();

    if (named.has(normalized)) {
      return named.get(normalized);
    }

    if (normalized.startsWith("#x")) {
      const value = Number.parseInt(normalized.slice(2), 16);
      return Number.isFinite(value) ? String.fromCodePoint(value) : full;
    }

    if (normalized.startsWith("#")) {
      const value = Number.parseInt(normalized.slice(1), 10);
      return Number.isFinite(value) ? String.fromCodePoint(value) : full;
    }

    return full;
  });
}

function extractMeta(html, attrName, attrValue) {
  const pattern = new RegExp(
    `<meta[^>]+${attrName}=["']${attrValue}["'][^>]+content=["']([^"']+)["'][^>]*>`,
    "i"
  );
  const match = html.match(pattern);
  return match ? decodeHtmlEntities(match[1]).trim() : "";
}

function extractTitle(html) {
  const match = html.match(/<title[^>]*>([\s\S]*?)<\/title>/i);
  return match ? decodeHtmlEntities(match[1]).replace(/\s+/g, " ").trim() : "";
}

function stripHtmlToText(html) {
  const noScripts = html
    .replace(/<script[\s\S]*?<\/script>/gi, " ")
    .replace(/<style[\s\S]*?<\/style>/gi, " ")
    .replace(/<noscript[\s\S]*?<\/noscript>/gi, " ")
    .replace(/<!--[\s\S]*?-->/g, " ");

  const text = noScripts
    .replace(/<\/(p|div|li|section|article|h[1-6]|br)>/gi, "\n")
    .replace(/<[^>]+>/g, " ")
    .replace(/\s+\n/g, "\n")
    .replace(/\n\s+/g, "\n")
    .replace(/[ \t]{2,}/g, " ")
    .replace(/\n{3,}/g, "\n\n")
    .trim();

  return decodeHtmlEntities(text);
}

async function fetchLoreFromUrl(url) {
  const html = await fetchText(url);
  const title = extractTitle(html);
  const description =
    extractMeta(html, "property", "og:description") ||
    extractMeta(html, "name", "description");
  const bodyText = stripHtmlToText(html).slice(0, 12000);

  return {
    mode: "url",
    source: url,
    title,
    summary: description,
    text: [title, description, bodyText].filter(Boolean).join("\n\n")
  };
}

async function fetchLoreFromWikipedia(topic) {
  const normalized = topic.trim().replace(/\s+/g, "_");
  const endpoint = `https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(normalized)}`;
  const payload = await fetchJson(endpoint);

  const title = typeof payload.title === "string" ? payload.title : topic;
  const summary = typeof payload.extract === "string" ? payload.extract : "";
  const description = typeof payload.description === "string" ? payload.description : "";

  if (!title && !summary && !description) {
    throw new Error("Wikipedia summary response did not include usable text");
  }

  return {
    mode: "wikipedia",
    source:
      payload.content_urls?.desktop?.page ||
      payload.content_urls?.mobile?.page ||
      endpoint,
    title,
    summary: [description, summary].filter(Boolean).join(". "),
    text: [title, description, summary].filter(Boolean).join("\n\n")
  };
}

function prettifySlug(text) {
  return text
    .replace(/[-_]+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function inferThemeName(args, lore) {
  if (args.theme) {
    return args.theme.trim();
  }

  if (args.topic) {
    return args.topic.trim();
  }

  if (lore?.title) {
    return lore.title.trim();
  }

  if (args.url) {
    try {
      const parsed = new URL(args.url);
      const tail = parsed.pathname.split("/").filter(Boolean).pop();
      if (tail) {
        return prettifySlug(tail);
      }
      return prettifySlug(parsed.hostname.replace(/^www\./, ""));
    } catch {
      return "Custom Theme";
    }
  }

  return "Custom Theme";
}

function selectThemeProfile({ themeName, loreText, url }) {
  const haystack = [themeName, loreText, url].filter(Boolean).join(" \n ").toLowerCase();

  for (const candidate of THEME_PROFILES) {
    if (candidate.match.test(haystack)) {
      return mergeProfile(candidate.profile);
    }
  }

  return mergeProfile({});
}

function mergeProfile(overrides) {
  return {
    id: overrides.id ?? BASE_PROFILE.id,
    fallbackIcon: overrides.fallbackIcon ?? BASE_PROFILE.fallbackIcon,
    verbs: { ...BASE_PROFILE.verbs, ...(overrides.verbs ?? {}) },
    objects: { ...BASE_PROFILE.objects, ...(overrides.objects ?? {}) },
    icons: { ...BASE_PROFILE.icons, ...(overrides.icons ?? {}) },
    suffixes: [...(overrides.suffixes ?? []), ...BASE_PROFILE.suffixes]
  };
}

function slugify(value) {
  return String(value)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/-{2,}/g, "-")
    .replace(/^-+|-+$/g, "") || "theme";
}

function compactWords(text) {
  return String(text)
    .replace(/[_-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function titleCase(text) {
  return compactWords(text)
    .split(" ")
    .filter(Boolean)
    .map((word) => {
      if (/^[a-z]{1,3}$/.test(word)) {
        return word.charAt(0).toUpperCase() + word.slice(1);
      }
      return word.charAt(0).toUpperCase() + word.slice(1);
    })
    .join(" ");
}

const TOKEN_STOPWORDS = new Set([
  "the",
  "and",
  "for",
  "with",
  "from",
  "into",
  "over",
  "under",
  "your",
  "this",
  "that",
  "skill",
  "skills",
  "tool",
  "tools",
  "openclaw",
  "spellbook",
  "wiki",
  "wikipedia"
]);

function extractLoreKeywords(themeName, loreText) {
  const source = [themeName, loreText].filter(Boolean).join(" ");
  const words = source.match(/[A-Za-z][A-Za-z0-9']{2,}/g) ?? [];
  const ranked = [];
  const seen = new Set();

  for (const rawWord of words) {
    const cleaned = rawWord.replace(/'s$/i, "");
    const lower = cleaned.toLowerCase();
    if (TOKEN_STOPWORDS.has(lower)) {
      continue;
    }
    if (seen.has(lower)) {
      continue;
    }
    seen.add(lower);
    ranked.push(titleCase(cleaned));
    if (ranked.length >= 24) {
      break;
    }
  }

  return ranked;
}

function hasAny(tokens, values) {
  return values.some((value) => tokens.includes(value));
}

function classifySkillId(skillId) {
  const tokens = skillId.split("-").filter(Boolean);
  const tokenSet = new Set(tokens);
  const has = (...values) => values.some((value) => tokenSet.has(value));

  let action = "default";
  if (has("search", "find", "lookup", "scrape", "crawl")) action = "search";
  else if (has("read", "open", "view", "cat", "show")) action = "read";
  else if (has("write", "save")) action = "write";
  else if (has("create", "scaffold", "init", "new", "generate")) action = "create";
  else if (has("edit", "patch", "modify", "update")) action = "edit";
  else if (has("delete", "remove", "rm", "clean", "cleanup", "prune")) action = "delete";
  else if (has("deploy", "ship")) action = "deploy";
  else if (has("build", "compile", "bundle")) action = "build";
  else if (has("test", "tests", "verify", "validate", "check")) action = "test";
  else if (has("lint")) action = "lint";
  else if (has("format", "fmt", "prettify")) action = "format";
  else if (has("fix", "repair", "heal")) action = "fix";
  else if (has("debug", "trace", "troubleshoot")) action = "debug";
  else if (has("install", "add")) action = "install";
  else if (has("upgrade")) action = "update";
  else if (has("run", "exec", "execute", "invoke")) action = "run";
  else if (has("start", "serve", "boot")) action = "start";
  else if (has("stop")) action = "stop";
  else if (has("restart", "reload")) action = "restart";
  else if (has("kill", "terminate")) action = "kill";
  else if (has("git", "commit", "branch", "merge", "rebase", "diff")) action = "git";
  else if (has("review", "audit")) action = "review";
  else if (has("plan", "design", "architect")) action = "plan";
  else if (has("explain", "describe", "summarize", "summary")) action = "explain";
  else if (has("transform", "convert")) action = "transform";
  else if (has("extract")) action = "extract";
  else if (has("parse")) action = "parse";
  else if (has("query", "ask")) action = "query";
  else if (has("monitor", "watch", "observe", "trace")) action = "monitor";
  else if (has("backup")) action = "backup";
  else if (has("restore")) action = "restore";
  else if (has("publish")) action = "publish";
  else if (has("release")) action = "release";

  let target = "default";
  if (has("web", "internet", "browser", "site", "url", "page")) target = "web";
  else if (has("file", "files", "fs", "path", "doc", "pdf")) target = "file";
  else if (has("code", "repo", "source")) target = "code";
  else if (has("data", "json", "csv", "xml")) target = "data";
  else if (has("db", "database", "sql", "postgres", "mysql", "mongo")) target = "database";
  else if (has("process", "proc", "daemon", "server")) target = "process";
  else if (has("service", "app")) target = "service";
  else if (has("api", "http", "rest", "graphql")) target = "api";
  else if (has("git", "commit", "branch", "merge", "rebase", "diff", "pr")) target = "repo";
  else if (has("docs", "doc", "readme", "wiki")) target = "docs";
  else if (has("docker", "k8s", "kubernetes", "kubectl", "terraform", "cloud", "infra")) target = "infra";
  else if (has("package", "npm", "pip", "deps", "dependency")) target = "package";
  else if (has("test", "tests")) target = "tests";
  else if (has("log", "logs", "trace")) target = "logs";
  else if (action === "git") target = "repo";
  else if (action === "query") target = "database";
  else if (action === "backup" || action === "restore") target = "data";
  else if (action === "deploy") target = "infra";
  else if (action === "test" || action === "lint" || action === "format" || action === "fix" || action === "debug") target = "code";
  else if (action === "write" || action === "edit") target = "file";
  else if (action === "monitor") target = "service";
  else target = "task";

  return {
    skillId,
    tokens,
    action,
    target
  };
}

function pickQualifier(tokens) {
  const ignore = new Set([
    "skill",
    "skills",
    "tool",
    "tools",
    "web",
    "file",
    "files",
    "code",
    "data",
    "db",
    "database",
    "sql",
    "api",
    "git",
    "repo",
    "process",
    "service",
    "server",
    "task",
    "read",
    "write",
    "create",
    "edit",
    "delete",
    "deploy",
    "build",
    "test",
    "tests",
    "lint",
    "format",
    "fix",
    "debug",
    "run",
    "start",
    "stop",
    "restart",
    "kill",
    "plan",
    "review",
    "explain",
    "transform",
    "extract",
    "parse",
    "query",
    "monitor",
    "backup",
    "restore",
    "publish",
    "release",
    "install",
    "update",
    "open",
    "merge",
    "branch",
    "commit",
    "diff"
  ]);

  const filtered = tokens.filter((token) => !ignore.has(token) && token.length > 1);
  if (filtered.length === 0) {
    return "";
  }
  return titleCase(filtered.slice(0, 2).join(" "));
}

function ensureUniqueSpell(baseSpell, { usedSpells, qualifier, loreKeywords, profile, counterRef }) {
  let spell = baseSpell;
  if (!usedSpells.has(spell)) {
    usedSpells.add(spell);
    return spell;
  }

  const candidates = [];
  if (qualifier) {
    candidates.push(`${baseSpell} of ${qualifier}`);
  }

  for (const keyword of loreKeywords) {
    candidates.push(`${baseSpell} of ${keyword}`);
  }

  for (const suffix of profile.suffixes) {
    candidates.push(`${baseSpell} of ${suffix}`);
  }

  for (const candidate of candidates) {
    if (!usedSpells.has(candidate)) {
      usedSpells.add(candidate);
      return candidate;
    }
  }

  let attempt = 2;
  while (usedSpells.has(`${baseSpell} ${attempt}`)) {
    attempt += 1;
  }
  spell = `${baseSpell} ${attempt}`;
  usedSpells.add(spell);
  counterRef.value = attempt;
  return spell;
}

function nextReferenceSpellName(referenceSpellNames, cursorRef) {
  while (cursorRef.index < referenceSpellNames.length) {
    const candidate = normalizeReferenceSpellName(referenceSpellNames[cursorRef.index]);
    cursorRef.index += 1;
    if (candidate) {
      return candidate;
    }
  }

  return "";
}

function buildSpellName(semantic, profile, loreKeywords, usedSpells, options = {}) {
  const qualifier = pickQualifier(semantic.tokens);
  const referenceSpell = normalizeReferenceSpellName(options.referenceSpell ?? "");

  if (referenceSpell) {
    return ensureUniqueSpell(referenceSpell, {
      usedSpells,
      qualifier,
      loreKeywords,
      profile,
      counterRef: { value: 0 }
    });
  }

  const verb = profile.verbs[semantic.action] ?? profile.verbs.default;
  const object = profile.objects[semantic.target] ?? profile.objects.default;
  const baseSpell = titleCase(`${verb} ${object}`);
  return ensureUniqueSpell(baseSpell, {
    usedSpells,
    qualifier,
    loreKeywords,
    profile,
    counterRef: { value: 0 }
  });
}

function pickIcon(semantic, profile) {
  return (
    profile.icons[semantic.action] ||
    profile.icons[semantic.target] ||
    profile.icons.default ||
    profile.fallbackIcon ||
    "✨"
  );
}

function generateMappings(skillIds, profile, loreKeywords, options = {}) {
  const mappings = {};
  const usedSpells = new Set();
  const referenceSpellNames = Array.isArray(options.referenceSpellNames) ? options.referenceSpellNames : [];
  const referenceCursor = { index: 0 };

  for (const skillId of skillIds) {
    const semantic = classifySkillId(skillId);
    const spell = buildSpellName(semantic, profile, loreKeywords, usedSpells, {
      referenceSpell: nextReferenceSpellName(referenceSpellNames, referenceCursor)
    });
    const icon = pickIcon(semantic, profile);
    mappings[skillId] = { spell, icon };
  }

  return mappings;
}

function yamlQuote(value) {
  const stringValue = String(value ?? "");
  return `"${stringValue
    .replace(/\\/g, "\\\\")
    .replace(/"/g, '\\"')
    .replace(/\r/g, "\\r")
    .replace(/\n/g, "\\n")}"`;
}

function toYamlDocument(doc) {
  const lines = [];
  const referenceUrls = Array.isArray(doc.spellListReferences)
    ? [...new Set(doc.spellListReferences.map((value) => String(value ?? "").trim()).filter(Boolean))]
    : [];

  if (referenceUrls.length > 0) {
    lines.push("# spell-list-references:");
    for (const url of referenceUrls) {
      lines.push(`# - ${url}`);
    }
  }
  lines.push(`theme: ${yamlQuote(doc.theme)}`);
  lines.push(`author: ${yamlQuote(doc.author)}`);
  lines.push(`description: ${yamlQuote(doc.description)}`);
  lines.push("mappings:");

  const skillIds = Object.keys(doc.mappings).sort();
  for (const skillId of skillIds) {
    const mapping = doc.mappings[skillId];
    lines.push(`  ${skillId}:`);
    lines.push(`    spell: ${yamlQuote(mapping.spell)}`);
    if (mapping.icon) {
      lines.push(`    icon: ${yamlQuote(mapping.icon)}`);
    }
  }

  return `${lines.join("\n")}\n`;
}

function summarizeSourceList(sources) {
  if (sources.length === 0) {
    return "fallback list";
  }
  if (sources.length === 1) {
    return sources[0];
  }
  return `${sources.slice(0, -1).join(" + ")} + ${sources[sources.length - 1]}`;
}

function buildDescription({ themeName, requestedTop, actualCount, loreMode, sourceNames }) {
  const lorePart =
    loreMode === "url"
      ? "page lore"
      : loreMode === "wikipedia"
        ? "Wikipedia lore"
        : "heuristic lore";

  return `${themeName} spell mappings for ${actualCount}/${requestedTop} popular skills, generated from ${summarizeSourceList(
    sourceNames
  )} with ${lorePart}.`;
}

function resolveOutputPath(explicitOutput, themeName) {
  if (explicitOutput) {
    return path.resolve(process.cwd(), explicitOutput);
  }

  const fileName = `${slugify(themeName)}.yaml`;
  return path.resolve(process.cwd(), FALLBACK_OUTPUT_DIR, fileName);
}

async function gatherPopularSkills(targetTop) {
  const fetchCount = Math.max(targetTop * 2, targetTop);
  const warnings = [];

  const [skillsShResult, clawhubResult] = await Promise.allSettled([
    fetchSkillsShTrending(fetchCount),
    fetchClawhubDownloads(fetchCount)
  ]);

  let skillsShItems = [];
  let clawhubItems = [];
  let clawhubApiUrl = "";
  const sourceNames = [];

  if (skillsShResult.status === "fulfilled") {
    skillsShItems = skillsShResult.value;
    sourceNames.push("skills.sh");
  } else {
    warnings.push(`skills.sh fetch failed: ${skillsShResult.reason?.message ?? String(skillsShResult.reason)}`);
  }

  if (clawhubResult.status === "fulfilled") {
    clawhubItems = clawhubResult.value.items;
    clawhubApiUrl = clawhubResult.value.apiUrl;
    sourceNames.push("clawhub");
  } else {
    warnings.push(`clawhub fetch failed: ${clawhubResult.reason?.message ?? String(clawhubResult.reason)}`);
  }

  const mergedSkillIds = mergePopularSkills({
    skillsShItems,
    clawhubItems,
    targetCount: targetTop
  });

  return {
    skillIds: mergedSkillIds,
    sourceNames,
    warnings,
    debug: {
      skillsShCount: skillsShItems.length,
      clawhubCount: clawhubItems.length,
      clawhubApiUrl
    }
  };
}

async function gatherLore(args) {
  const warnings = [];

  if (args.url) {
    try {
      const lore = await fetchLoreFromUrl(args.url);
      return { lore, warnings };
    } catch (error) {
      warnings.push(`URL lore fetch failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  if (args.topic) {
    try {
      const lore = await fetchLoreFromWikipedia(args.topic);
      return { lore, warnings };
    } catch (error) {
      warnings.push(`Wikipedia summary fetch failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  return {
    lore: {
      mode: "heuristic",
      source: "",
      title: args.theme || args.topic || "",
      summary: "",
      text: args.theme || args.topic || args.url || "Custom theme"
    },
    warnings
  };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));

  const preliminaryThemeName = inferThemeName(args, null);
  const popularPromise = gatherPopularSkills(args.top);
  const spellReferenceResult = await gatherReferenceSpellNames({ args, themeName: preliminaryThemeName, lore: null });
  const [popular, loreResult] = await Promise.all([popularPromise, gatherLore(args)]);
  const lore = loreResult.lore;

  const themeName = inferThemeName(args, lore);
  const profile = selectThemeProfile({
    themeName,
    loreText: lore.text,
    url: args.url
  });
  const loreKeywords = extractLoreKeywords(themeName, lore.text);

  for (const warning of [...popular.warnings, ...loreResult.warnings, ...spellReferenceResult.warnings]) {
    console.error(`Warning: ${warning}`);
  }

  const mappings = generateMappings(popular.skillIds, profile, loreKeywords, {
    referenceSpellNames: spellReferenceResult.spellNames
  });
  const description = buildDescription({
    themeName,
    requestedTop: args.top,
    actualCount: Object.keys(mappings).length,
    loreMode: lore.mode,
    sourceNames: popular.sourceNames
  });

  const outputPath = resolveOutputPath(args.output, themeName);
  await fs.mkdir(path.dirname(outputPath), { recursive: true });

  const yamlDocument = toYamlDocument({
    theme: themeName,
    author: args.author,
    description,
    mappings,
    spellListReferences: mergeAndDedupeReferenceUrls(
      spellReferenceResult.debug.succeeded.flatMap((reference) =>
        Array.isArray(reference.referenceUrls) ? reference.referenceUrls : [reference.url]
      )
    )
  });

  await fs.writeFile(outputPath, yamlDocument, "utf8");

  const relativeOutput = path.relative(process.cwd(), outputPath) || path.basename(outputPath);
  console.log(`Generated ${Object.keys(mappings).length} mappings -> ${relativeOutput}`);
  console.log(`Theme: ${themeName} (${profile.id})`);
  console.log(`Popular skill sources: ${summarizeSourceList(popular.sourceNames)}${popular.sourceNames.length === 0 ? " (fallback only)" : ""}`);
  console.log(`Lore source: ${lore.mode}${lore.source ? ` (${lore.source})` : ""}`);
  if (spellReferenceResult.debug.queries.length > 0) {
    console.log(`Spell list search queries: ${spellReferenceResult.debug.queries.join(" | ")}`);
  }
  if (spellReferenceResult.debug.attempted.length > 0) {
    console.log(
      `Spell list reference URLs attempted: ${spellReferenceResult.debug.attempted
        .map((reference) => reference.url)
        .join(", ")}`
    );
    console.log(
      `Spell list reference URLs succeeded: ${
        spellReferenceResult.debug.succeeded.length > 0
          ? spellReferenceResult.debug.succeeded
              .map((reference) => `${reference.url} (${reference.count}, ${reference.parser})`)
              .join(", ")
          : "none"
      }`
    );
    if (spellReferenceResult.debug.sample.length > 0) {
      console.log(`Spell list sample: ${spellReferenceResult.debug.sample.join(", ")}`);
    }
  }
  if (popular.debug.clawhubApiUrl) {
    console.log(`ClawHub API: ${popular.debug.clawhubApiUrl}`);
  }
}

main().catch((error) => {
  const message = error instanceof Error ? error.message : String(error);
  console.error(`Failed to generate spell mapping: ${message}`);
  process.exitCode = 1;
});
