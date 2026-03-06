export const DEFAULT_SLIDES = [
  "The trading card market runs on messy data.",
  "Prices fragment. Condition drifts. Signals lie.",
  "Collectors make real decisions on incomplete info.",
  "JK Index = market intelligence for TCGs.",
  "Truth first. No guessing. Built in public.",
  "Alpha today. Compounding weekly. Brick by brick. 👑🧱",
];

const TEMPLATE_BUILDERS = {
  intro: (topic) => [
    `${topic}: why this matters now.`,
    "Most people see polished outputs and miss the messy middle.",
    "Without structure, important signals get lost in noise.",
    `${topic}: turned into a clear, practical narrative.`,
    "Each slide does one job: inform, connect, and move forward.",
    "Start simple, publish consistently, and improve every cycle.",
  ],
  educational: (topic) => [
    `${topic}: the core idea in 6 steps.`,
    "Step 1: define the problem in plain language.",
    "Step 2: identify the common mistake people make.",
    "Step 3: show the practical framework that works.",
    "Step 4: apply it to a real-world example.",
    "Step 5: summarize the takeaway and next action.",
  ],
  "product-update": (topic) => [
    `${topic}: what changed this week.`,
    "New capability: faster workflow for repeatable output.",
    "Quality upgrade: stronger validation before publish.",
    "Reliability upgrade: deterministic rendering and checks.",
    "User impact: less manual effort, clearer results.",
    "Next: iterate with feedback and ship improvements.",
  ],
  announcement: (topic) => [
    `${topic}: official announcement.`,
    "What is launching and who it is for.",
    "What problem this solves right now.",
    "What users can expect from day one.",
    "How to get started in under 5 minutes.",
    "Follow for updates as we roll out improvements.",
  ],
};

export function validateSlides(slides, sourceLabel) {
  if (!Array.isArray(slides)) {
    throw new Error(`${sourceLabel} must provide a 'slides' array.`);
  }
  if (slides.length !== 6) {
    throw new Error(`${sourceLabel} must provide exactly 6 slides.`);
  }
  for (const [idx, line] of slides.entries()) {
    if (typeof line !== "string" || !line.trim()) {
      throw new Error(`${sourceLabel} slide ${idx + 1} must be a non-empty string.`);
    }
  }
  return slides.map((line) => line.trim());
}

export function listTemplates() {
  return Object.keys(TEMPLATE_BUILDERS);
}

export function generateSlidesFromTemplate(templateName, topic = "Your topic") {
  const builder = TEMPLATE_BUILDERS[templateName];
  if (!builder) {
    throw new Error(
      `Unknown template '${templateName}'. Allowed: ${listTemplates().join(", ")}`
    );
  }
  return validateSlides(builder(topic.trim() || "Your topic"), `Template (${templateName})`);
}

export function generateSlidesFromTopic(topic) {
  const cleanTopic = topic.trim();
  if (!cleanTopic) {
    throw new Error("Topic cannot be empty when generating custom slides.");
  }
  return generateSlidesFromTemplate("intro", cleanTopic);
}

export function resolveSlides({ topic, template = "intro" }) {
  if (topic) return generateSlidesFromTopic(topic);
  if (template) return generateSlidesFromTemplate(template, "Your topic");
  return validateSlides([...DEFAULT_SLIDES], "Default slides");
}
