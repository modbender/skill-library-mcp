/**
 * Markdown to Notion blocks converter using @tryfabric/martian
 * 
 * This module wraps the martian library to convert Markdown content
 * into Notion API block format.
 */

import { markdownToBlocks, markdownToRichText } from "@tryfabric/martian";
import type { NotionBlock } from "./notion-api.js";

export interface ConvertOptions {
  /**
   * Enable emoji-style callouts in blockquotes
   * When true, blockquotes starting with emoji will be converted to Notion callouts
   */
  enableEmojiCallouts?: boolean;
  
  /**
   * Validate image URLs and convert invalid ones to text
   * Default: true
   */
  strictImageUrls?: boolean;
}

/**
 * Convert Markdown content to Notion blocks
 * 
 * @param markdown - The markdown content to convert
 * @param options - Conversion options
 * @returns Array of Notion block objects ready for API submission
 */
/**
 * Clean invalid URLs from markdown before converting to Notion blocks
 *
 * Notion API URL VALIDATION RULES:
 * - Only accepts http:// and https:// URLs
 * - Rejects: javascript:, data:, file:, about:, weixin:, wx://
 * - Rejects: relative paths (/path, ./path)
 * - Rejects: hash-only links (#)
 * - Rejects: empty links
 *
 * STRATEGY: To ensure content is always saved successfully, we:
 * 1. Remove ALL invalid URL types before conversion
 * 2. Remove ALL markdown links [text](url) to avoid validation errors
 * 3. Keep the link text for readability
 */
function cleanInvalidUrls(markdown: string): string {
  return markdown
    // Remove javascript: links
    .replace(/\[([^\]]*)\]\(javascript:[^)]*\)/gi, (match, text) => text || '')
    // Remove data: URLs
    .replace(/\[([^\]]*)\]\(data:[^)]*\)/gi, (match, text) => text || '')
    // Remove file: URLs
    .replace(/\[([^\]]*)\]\(file:[^)]*\)/gi, (match, text) => text || '')
    // Remove about: URLs
    .replace(/\[([^\]]*)\]\(about:[^)]*\)/gi, (match, text) => text || '')
    // Fix wechat internal links (weixin:, wx://)
    .replace(/\[([^\]]*)\]\(weixin:[^)]*\)/gi, (match, text) => text || '')
    .replace(/\[([^\]]*)\]\(wx:\/\/[^)]*\)/gi, (match, text) => text || '')
    // Fix relative paths - convert to plain text
    .replace(/\[([^\]]*)\]\(\s*\/[^)]*\)/gi, (match, text) => text || '')
    // Fix relative paths with ./ or ../
    .replace(/\[([^\]]*)\]\(\.\.\/[^)]*\)/gi, (match, text) => text || '')
    // Fix URLs with only hash (#)
    .replace(/\[([^\]]*)\]\(\s*#[^)]*\)/gi, (match, text) => text || '')
    // Fix URLs with invalid characters like spaces
    .replace(/\[([^\]]*)\]\(\s*<([^>]*)>\s*\)/gi, '[$1]($2)')
    // Remove empty links
    .replace(/\[\s*\]\(\s*\)/g, '')
    // Fix URLs with Chinese parentheses （） instead of ()
    .replace(/\[([^\]]*)\]（[^）]*）/gi, (match, text) => text || match)
    // Remove or fix links with no valid URL scheme
    .replace(/\[([^\]]*)\]\s*\(\s*\)/g, (match, text) => text || '');
}

export function convertMarkdownToNotionBlocks(
  markdown: string,
  options: ConvertOptions = {}
): NotionBlock[] {
  const {
    enableEmojiCallouts = true,
    strictImageUrls = true,
  } = options;

  // Clean invalid URLs before conversion
  let cleanedMarkdown = cleanInvalidUrls(markdown);

  // Remove ALL markdown links to avoid Notion URL validation errors
  // Keep the link text, remove the URL part
  cleanedMarkdown = cleanedMarkdown.replace(/\[([^\]]+)\]\([^)]+\)/gi, '$1');

  try {
    const blocks = markdownToBlocks(cleanedMarkdown, {
      enableEmojiCallouts,
      strictImageUrls: false,
      notionLimits: {
        truncate: true,
        onError: (err: Error) => {
          console.warn("Notion limit warning:", err.message);
        },
      },
    });

    return blocks as NotionBlock[];
  } catch (error) {
    console.error("Failed to convert markdown to Notion blocks:", error);
    // Return a simple paragraph block with the raw content as fallback
    return [{
      object: "block",
      type: "paragraph",
      paragraph: {
        rich_text: [{
          type: "text",
          text: {
            content: cleanedMarkdown.slice(0, 2000),
          },
        }],
      },
    }];
  }
}

/**
 * Convert Markdown to Notion rich text (for inline content)
 * 
 * @param markdown - The markdown content to convert
 * @returns Array of Notion rich text objects
 */
export function convertMarkdownToRichText(markdown: string): unknown[] {
  try {
    return markdownToRichText(markdown);
  } catch (error) {
    console.error("Failed to convert markdown to rich text:", error);
    return [{
      type: "text",
      text: {
        content: markdown.slice(0, 2000),
      },
    }];
  }
}

/**
 * Create a bookmark block for the source URL
 */
export function createBookmarkBlock(url: string): NotionBlock {
  return {
    object: "block",
    type: "bookmark",
    bookmark: {
      url,
    },
  };
}

/**
 * Create a divider block
 */
export function createDividerBlock(): NotionBlock {
  return {
    object: "block",
    type: "divider",
    divider: {},
  };
}

/**
 * Create a callout block with metadata
 */
export function createMetadataCallout(
  title: string,
  url: string,
  capturedAt: string,
  author?: string
): NotionBlock {
  let content = `**${title}**\n\nSource: ${url}\nCaptured: ${capturedAt}`;
  if (author) {
    content += `\nAuthor: ${author}`;
  }

  return {
    object: "block",
    type: "callout",
    callout: {
      rich_text: [{
        type: "text",
        text: {
          content,
        },
      }],
      icon: {
        type: "emoji",
        emoji: "📎",
      },
      color: "gray_background",
    },
  };
}
