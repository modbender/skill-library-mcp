/**
 * Discord Connect - Navigation Hooks for Plugin Architecture
 * 
 * This module provides hooks to automatically register the Discord tab
 * in the Clawdbot Control dashboard navigation system.
 * 
 * Usage: Called by the plugin installer during skill installation.
 */

/**
 * Tab configuration for the Discord Connect view
 */
export const DISCORD_TAB_CONFIG = {
  id: "discord",
  path: "/discord",
  icon: "🎮",
  title: "Discord",
  subtitle: "Bot connection & servers",
  group: "channels",
  order: 10, // Position within the Channels group
};

/**
 * Navigation registration data for injection into navigation.ts
 */
export const NAVIGATION_PATCHES = {
  // Add to TAB_GROUPS.channels.tabs array
  tabGroups: {
    target: "TAB_GROUPS",
    group: "channels",
    value: "discord",
  },

  // Add to Tab type union
  tabType: {
    target: "Tab",
    value: '"discord"',
  },

  // Add to TAB_PATHS record
  tabPaths: {
    target: "TAB_PATHS",
    key: "discord",
    value: '"/discord"',
  },

  // Add to TAB_ICONS record
  tabIcons: {
    target: "TAB_ICONS",
    key: "discord",
    value: '"🎮"',
  },

  // Add to TAB_TITLES record
  tabTitles: {
    target: "TAB_TITLES",
    key: "discord",
    value: '"Discord"',
  },

  // Add to TAB_SUBTITLES record
  tabSubtitles: {
    target: "TAB_SUBTITLES",
    key: "discord",
    value: '"Bot connection & servers"',
  },
};

/**
 * Render patch for app-render.ts
 */
export const RENDER_PATCH = {
  // Import statement to add
  import: 'import "./views/discord.js";',
  
  // Case statement for tab rendering
  caseStatement: `case "discord":
  return html\`<discord-connect-view></discord-connect-view>\`;`,
};

/**
 * Check if Discord tab is already registered
 * @param {string} navigationContent - Content of navigation.ts file
 * @returns {boolean} True if Discord tab is already registered
 */
export function isDiscordTabRegistered(navigationContent) {
  return navigationContent.includes('"discord"') && 
         navigationContent.includes('"/discord"');
}

/**
 * Check if Discord view is already imported
 * @param {string} renderContent - Content of app-render.ts file
 * @returns {boolean} True if Discord view is already imported
 */
export function isDiscordViewRegistered(renderContent) {
  return renderContent.includes('./views/discord') ||
         renderContent.includes('discord-connect-view');
}

/**
 * Generate navigation.ts patch content
 * @param {string} originalContent - Original navigation.ts content
 * @returns {string} Patched content with Discord tab
 */
export function patchNavigation(originalContent) {
  let content = originalContent;

  // Add to Tab type if not present
  if (!content.includes('"discord"')) {
    // Find Tab type definition and add discord
    content = content.replace(
      /export type Tab\s*=\s*([^;]+);/,
      (match, types) => {
        const cleanTypes = types.trim();
        if (cleanTypes.endsWith('"')) {
          return `export type Tab = ${cleanTypes}\n  | "discord";`;
        }
        return match.replace(';', '\n  | "discord";');
      }
    );
  }

  // Add TAB_PATHS entry
  if (!content.includes('discord: "/discord"')) {
    content = content.replace(
      /(TAB_PATHS[^}]+)(};)/,
      '$1  discord: "/discord",\n$2'
    );
  }

  // Add TAB_ICONS entry
  if (!content.includes('discord: "🎮"')) {
    content = content.replace(
      /(TAB_ICONS[^}]+)(};)/,
      '$1  discord: "🎮",\n$2'
    );
  }

  // Add TAB_TITLES entry
  if (!content.includes('discord: "Discord"')) {
    content = content.replace(
      /(TAB_TITLES[^}]+)(};)/,
      '$1  discord: "Discord",\n$2'
    );
  }

  // Add TAB_SUBTITLES entry
  if (!content.includes('discord: "Bot connection')) {
    content = content.replace(
      /(TAB_SUBTITLES[^}]+)(};)/,
      '$1  discord: "Bot connection & servers",\n$2'
    );
  }

  // Add to channels group in TAB_GROUPS
  if (!content.includes('tabs: ["discord"') && !content.includes('"discord",')) {
    content = content.replace(
      /(channels:\s*{\s*label:\s*"Channels",\s*tabs:\s*\[)/,
      '$1"discord", '
    );
  }

  return content;
}

/**
 * Generate app-render.ts patch content
 * @param {string} originalContent - Original app-render.ts content
 * @returns {string} Patched content with Discord view
 */
export function patchAppRender(originalContent) {
  let content = originalContent;

  // Add import if not present
  if (!content.includes('./views/discord')) {
    // Find the last view import and add after it
    const viewImportRegex = /import\s+["']\.\/views\/[^"']+["'];?\n/g;
    let lastMatch = null;
    let match;
    while ((match = viewImportRegex.exec(content)) !== null) {
      lastMatch = match;
    }
    
    if (lastMatch) {
      const insertPos = lastMatch.index + lastMatch[0].length;
      content = content.slice(0, insertPos) + 
                'import "./views/discord.js";\n' + 
                content.slice(insertPos);
    } else {
      // Fallback: add after other imports
      content = content.replace(
        /(import[^;]+;\n)(\n*(?:export|const|function))/,
        '$1import "./views/discord.js";\n$2'
      );
    }
  }

  // Add case statement if not present
  if (!content.includes('case "discord"')) {
    // Find the switch statement for tabs and add case
    content = content.replace(
      /(switch\s*\(\s*(?:this\.)?(?:current)?[Tt]ab\s*\)\s*{)/,
      `$1
      case "discord":
        return html\`<discord-connect-view></discord-connect-view>\`;`
    );
  }

  return content;
}

export default {
  DISCORD_TAB_CONFIG,
  NAVIGATION_PATCHES,
  RENDER_PATCH,
  isDiscordTabRegistered,
  isDiscordViewRegistered,
  patchNavigation,
  patchAppRender,
};
