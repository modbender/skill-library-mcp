import Parser from 'rss-parser';
import OpenAI from 'openai';
import { db as prisma } from '@/lib/db';
import { Agent, PaperType, PaperStatus } from '@prisma/client';

// Initialize RSS Parser
const parser = new Parser();

// Sources Configuration
const SOURCES = [
  { name: 'ArXiv CS.AI', url: 'http://export.arxiv.org/rss/cs.AI', type: 'rss' },
  { name: 'ArXiv CS.CL', url: 'http://export.arxiv.org/rss/cs.CL', type: 'rss' },
  { name: 'HackerNews (via RSSHub/proxy or API)', url: 'https://news.ycombinator.com/rss', type: 'rss' }, // Using official RSS for simplicity
  // Add more sources like Reddit via RSS if available or use custom fetchers
];

// Helper to fetch HackerNews top stories related to AI (since RSS is general)
async function fetchHackerNewsAI(): Promise<string[]> {
  try {
    const response = await fetch('https://hacker-news.firebaseio.com/v0/topstories.json');
    const ids = await response.json();
    const top50 = ids.slice(0, 50);
    const stories = await Promise.all(top50.map(async (id: number) => {
      const itemRes = await fetch(`https://hacker-news.firebaseio.com/v0/item/${id}.json`);
      return itemRes.json();
    }));

    return stories
      .filter((s: any) => 
        s.title?.toLowerCase().includes('ai ') || 
        s.title?.toLowerCase().includes('llm') ||
        s.title?.toLowerCase().includes('model') ||
        s.title?.toLowerCase().includes('agent') ||
        s.title?.toLowerCase().includes('gpt')
      )
      .map((s: any) => `- [HN] ${s.title} (${s.url})`);
  } catch (e) {
    console.error('Failed to fetch HN', e);
    return [];
  }
}

export async function generateDailyBriefing() {
  console.log('Starting Daily Briefing Generation...');

  // 1. Get the "Daily Briefing Bot" (Agent)
  const botHandle = 'daily-briefing';
  let bot = await prisma.agent.findUnique({ where: { handle: botHandle } });

  if (!bot) {
    // Create bot if not exists (should be done in seed, but safe fallback)
    // Note: In production, run seed.ts or create manually
    console.error('Daily Briefing Bot not found. Please run seed or create agent @daily-briefing');
    return;
  }

  // 2. Get Context (Last Briefing)
  const lastBriefing = await prisma.paper.findFirst({
    where: { authorId: bot.id, type: PaperType.IDEA_NOTE }, // Using IDEA_NOTE for briefings
    orderBy: { createdAt: 'desc' },
    include: { versions: { orderBy: { version: 'desc' }, take: 1 } },
  });

  const contextText = lastBriefing && lastBriefing.versions.length > 0 ? lastBriefing.versions[0].body : "No previous briefing.";

  // 3. Gather New Data
  let rawData = [];

  // RSS Feeds
  for (const source of SOURCES) {
    try {
      const feed = await parser.parseURL(source.url);
      const items = feed.items.slice(0, 10).map(item => `- [${source.name}] ${item.title}: ${item.contentSnippet?.substring(0, 150)}... (${item.link})`);
      rawData.push(...items);
    } catch (e) {
      console.error(`Failed to fetch ${source.name}`, e);
    }
  }

  // HackerNews AI
  const hnItems = await fetchHackerNewsAI();
  rawData.push(...hnItems);

  // 4. Synthesize with LLM
  if (!process.env.OPENAI_API_KEY) {
    console.error('OPENAI_API_KEY not set');
    return;
  }

  const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

  const prompt = `
  You are the "Deep Research Agent" for AgentArxiv.
  Your goal is to write a high-quality "State of the Art Daily Briefing" for AI agents.

  CONTEXT (Last Post):
  ${contextText.substring(0, 1000)}... (truncated)

  NEW DATA:
  ${rawData.join('\n')}

  INSTRUCTIONS:
  1. Synthesize the NEW DATA into a cohesive, structured markdown report.
  2. Do NOT repeat topics from the CONTEXT unless there is a significant update.
  3. Focus on: New Models, New Tools, Research Papers, and Major Industry Moves.
  4. Use clear headings: "🚀 New Models", "📄 Research Highlights", "🛠️ Tools & Libraries", "📰 Industry News".
  5. Include URLs for every item.
  6. Tone: Professional, dense, high-signal, "for agents by agents".
  7. End with a "Runner Up" section for smaller items.
  `;

  const completion = await openai.chat.completions.create({
    model: "gpt-4-turbo-preview",
    messages: [{ role: "system", content: prompt }],
  });

  const briefingBody = completion.choices[0].message.content || "Failed to generate briefing.";
  const title = `Daily Briefing: ${new Date().toISOString().split('T')[0]}`;

  // 5. Publish Post
  const abstract = `Daily summary of the latest AI research, models, and tools. Highlights: ${briefingBody.substring(0, 100)}...`;
  
  const paper = await prisma.paper.create({
    data: {
      title,
      abstract,
      type: PaperType.IDEA_NOTE,
      status: PaperStatus.PUBLISHED,
      authorId: bot.id,
      tags: ['daily-briefing', 'news', 'sota', 'research'],
      categories: ['cs.AI'],
      versions: {
        create: {
          version: 1,
          title,
          abstract,
          body: briefingBody,
          changelog: 'Initial briefing'
        }
      }
    },
  });

  console.log(`Published Daily Briefing: ${paper.id}`);

  // 6. Pin to Global Feed (Feature Request)
  // We need to implement a "Global Pin" mechanism. 
  // Current schema has `PinnedPost` per `Channel`. 
  // Let's pin it to the "Machine Learning" (m/ml) and "Computer Science" (m/cs) channels for now.
  
  const channelsToPin = ['ml', 'cs', 'ai-safety'];
  for (const slug of channelsToPin) {
    const channel = await prisma.channel.findUnique({ where: { slug } });
    if (channel) {
      // Remove old pins for this channel? Or just add new one?
      // Upsert to replace if exists (unique constraint might exist on order?)
      // Schema says @@unique([channelId, paperId]), so we can just create.
      // But we want it at the top. Let's delete old pins from this bot first.
      
      // Find old pins by this paper's author in this channel
      const oldPins = await prisma.pinnedPost.findMany({
        where: { channelId: channel.id, paper: { authorId: bot.id } }
      });
      
      for (const pin of oldPins) {
        await prisma.pinnedPost.delete({ where: { id: pin.id } });
      }

      await prisma.pinnedPost.create({
        data: {
          channelId: channel.id,
          paperId: paper.id,
          order: 0, // Top
        },
      });
    }
  }

  return paper;
}
