/**
 * Default configuration values for OpenClaw Avatar
 */

import type { Config, FillerConfig, StreamDeckColors, StreamDeckButtonPrompt } from './schema.js';

export const DEFAULT_FILLERS: FillerConfig = {
  'en-US': {
    email: ['Let me check your inbox.', 'Checking your emails now.', "Let me see what's come in."],
    calendar: ['Let me pull up your calendar.', 'Checking your schedule.', "Let me see what's coming up."],
    hubspot: ['Let me check HubSpot for you.', 'Pulling up HubSpot now.', "Let me see what's happening in HubSpot."],
    notion: ['Let me check Notion.', 'Looking through Notion now.', "Let me see what's been updated."],
    slack: ['Let me check Slack.', 'Checking your messages now.', "Let me see if there's anything important."],
    customers: ['Let me pull up your customer list.', 'Checking customer health now.', 'Let me see how your customers are doing.'],
    meetings: ['Let me check your meetings.', "Pulling up today's schedule.", 'Let me see what meetings you have.'],
    pipeline: ['Let me check the pipeline.', 'Pulling up the deals now.', 'Let me see where things stand.'],
    brief: ['Let me pull together your briefing.', 'Getting your morning brief ready.', 'Let me check everything for you.'],
    followups: ['Let me check your follow-ups.', "Checking what's due today.", 'Let me see who needs attention.'],
    churn: ['Let me check for churn risks.', 'Looking at customer health now.', "Let me see who's at risk."],
    prep: ['Let me prep you for your next meeting.', 'Pulling up meeting details now.', 'Let me get you ready.'],
    default: ['Let me check that for you.', 'One moment, let me look into that.', 'On it, give me a second.', 'Good question, let me find out.', 'Hmm, let me check.'],
  },
  'nb-NO': {
    email: ['La meg sjekke innboksen din.', 'Sjekker e-postene dine nå.', 'La meg se hva som har kommet inn.'],
    calendar: ['La meg sjekke kalenderen din.', 'Sjekker timeplanen din.', 'La meg se hva som kommer.'],
    hubspot: ['La meg sjekke HubSpot.', 'Henter opp HubSpot nå.', 'La meg se hva som skjer i HubSpot.'],
    notion: ['La meg sjekke Notion.', 'Ser gjennom Notion nå.', 'La meg se hva som er oppdatert.'],
    slack: ['La meg sjekke Slack.', 'Sjekker meldingene dine nå.', 'La meg se om det er noe viktig.'],
    customers: ['La meg hente kundelisten din.', 'Sjekker kundehelse nå.', 'La meg se hvordan det går med kundene dine.'],
    meetings: ['La meg sjekke møtene dine.', 'Henter dagens plan.', 'La meg se hvilke møter du har.'],
    pipeline: ['La meg sjekke pipelinen.', 'Henter opp avtalene nå.', 'La meg se hvor ting står.'],
    brief: ['La meg sette sammen briefingen din.', 'Gjør klar morgenbriefingen.', 'La meg sjekke alt for deg.'],
    followups: ['La meg sjekke oppfølgingene dine.', 'Sjekker hva som er på gang i dag.', 'La meg se hvem som trenger oppmerksomhet.'],
    churn: ['La meg sjekke churn-risiko.', 'Ser på kundehelsen nå.', 'La meg se hvem som er i faresonen.'],
    prep: ['La meg forberede deg til neste møte.', 'Henter møtedetaljer nå.', 'La meg gjøre deg klar.'],
    default: ['La meg sjekke det for deg.', 'Et øyeblikk, la meg se.', 'Jeg er på saken.', 'Godt spørsmål, la meg finne ut av det.', 'Hmm, la meg sjekke.'],
  },
};

export const DEFAULT_STREAMDECK_COLORS: StreamDeckColors = {
  blue: '#2563eb',
  green: '#059669',
  orange: '#d97706',
  teal: '#0d9488',
  purple: '#7c3aed',
  indigo: '#4f46e5',
  slate: '#475569',
  red: '#dc2626',
  slack: '#4A154B',
  dark: '#1e1e2e',
};

export const DEFAULT_BUTTON_PROMPTS: StreamDeckButtonPrompt = {
  check_email: 'Check my unread emails from today and summarize what needs attention.',
  check_calendar: "What's on my calendar today and tomorrow?",
  check_hubspot: 'Give me a quick overview of my HubSpot — any at-risk customers or active deals I should know about?',
  search_notion: "What's been updated in Notion in the last 2 days that's relevant to me?",
  check_slack: 'Check if there are any important Slack messages or mentions I should know about.',
  customer_health: 'Show me my customers sorted by health score, focusing on the ones that need attention.',
  todays_meetings: 'What meetings do I have today? Help me prep for the next one.',
  deal_pipeline: "What's the current deal pipeline looking like? Any deals close to closing?",
  morning_brief: "Give me a full morning briefing: unread emails, today's calendar, any important Slack messages, and customer updates. Hit all the highlights.",
  followups: "What customer follow-ups are due today or overdue? Check HubSpot for any tasks, scheduled emails, or customers I haven't contacted recently.",
  churn_risk: 'Which of my customers are at risk of churning? Look at engagement, recent activity, and any red flags in HubSpot.',
  prep_meeting: "Help me prep for my next upcoming meeting. Who's attending, what's the context, and what should I know going in?",
};

export const DEFAULT_CONFIG: Omit<Config, 'secrets'> = {
  app: {
    name: 'Avatar Assistant',
    port: 5173,
  },
  openclaw: {
    gatewayUrl: 'ws://127.0.0.1:18789',
  },
  avatars: [
    {
      id: 'default',
      name: 'Assistant',
      faceId: 'tmp_s-c5f82c46-7e9e-4eb7-95fd-8c994cca496f',
      voiceId: '21m00Tcm4TlvDq8ikWAM',
      default: true,
    },
  ],
  languages: [
    {
      code: 'en-US',
      name: 'English',
      flag: 'gb',
      default: true,
    },
  ],
  fillers: DEFAULT_FILLERS,
  integrations: {
    slack: {
      enabled: false,
    },
    email: {
      enabled: false,
    },
    streamDeck: {
      enabled: false,
      colors: DEFAULT_STREAMDECK_COLORS,
      buttonPrompts: DEFAULT_BUTTON_PROMPTS,
    },
  },
};
