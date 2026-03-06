/**
 * Example: User Preference Agent
 * 
 * This agent remembers user preferences across sessions using SQ Cloud.
 * 
 * Usage in agent system prompt:
 * "You have access to permanent memory via sq-memory skill.
 *  When users mention preferences, store them with remember().
 *  When answering questions, check recall() first."
 */

// Example conversation flow:

// USER: "I prefer dark mode"
// AGENT uses: remember("user/preferences/theme", "dark")

// USER: "My timezone is America/Chicago" 
// AGENT uses: remember("user/preferences/timezone", "America/Chicago")

// USER: "Call me Will"
// AGENT uses: remember("user/identity/preferred-name", "Will")

// [AGENT RESTARTS - new session]

// USER: "What time is it?"
// AGENT uses: recall("user/preferences/timezone") → "America/Chicago"
// AGENT: "It's 3:15 PM in America/Chicago"

// USER: "What's my name?"
// AGENT uses: recall("user/identity/preferred-name") → "Will"
// AGENT: "Your name is Will!"

// USER: "What are all my preferences?"
// AGENT uses: list_memories("user/preferences/")
// AGENT returns: ["user/preferences/theme", "user/preferences/timezone"]
// AGENT: "You prefer dark mode and your timezone is America/Chicago"

/**
 * Recommended coordinate structure for user preferences:
 * 
 * user/identity/name
 * user/identity/preferred-name
 * user/identity/pronouns
 * user/preferences/theme
 * user/preferences/language
 * user/preferences/timezone
 * user/preferences/notification-level
 * user/contacts/email
 * user/contacts/phone
 * user/settings/ai-model
 * user/settings/response-style
 */

// Implementation example (pseudo-code for OpenClaw agent):

async function handleUserPreference(category, value) {
  const coordinate = `user/preferences/${category}`;
  await remember(coordinate, value);
  return `Remembered: ${category} = ${value}`;
}

async function getUserPreference(category) {
  const coordinate = `user/preferences/${category}`;
  const value = await recall(coordinate);
  return value || null;
}

async function getAllPreferences() {
  const coords = await list_memories("user/preferences/");
  const prefs = {};
  
  for (const coord of coords) {
    const category = coord.split('/').pop();
    const value = await recall(coord);
    prefs[category] = value;
  }
  
  return prefs;
}

// Usage in agent conversation:
// - User says preference → call handleUserPreference()
// - User asks question needing preference → call getUserPreference()
// - User asks "what do you know about me?" → call getAllPreferences()
