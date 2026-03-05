import axios from 'axios';
import { Attraction } from '../types';

export interface WikivoyageGuide {
  destination: string;
  overview: string;
  attractions: Attraction[];
  culturalTips: string[];
  practicalInfo: string;
  rawSections: Record<string, string>;
}

/**
 * Wikivoyage MediaWiki API client — free, no API key required
 * https://en.wikivoyage.org/w/api.php
 */
export class WikivoyageClient {
  private readonly apiBase = 'https://en.wikivoyage.org/w/api.php';

  async getGuide(destination: string): Promise<WikivoyageGuide> {
    const raw = await this.fetchArticle(destination);
    if (!raw) {
      return this.emptyGuide(destination);
    }
    return this.parseGuide(destination, raw);
  }

  private async fetchArticle(destination: string): Promise<string | null> {
    try {
      const response = await axios.get(this.apiBase, {
        params: {
          action: 'query',
          titles: destination,
          prop: 'extracts',
          explaintext: true,
          exsectionformat: 'plain',
          format: 'json',
          origin: '*',
        },
        timeout: 10000,
        headers: { 'User-Agent': 'OpenCLAW-TourPlanner/1.0 (openclaw.tours)' },
      });

      const pages = response.data?.query?.pages ?? {};
      const page = Object.values(pages)[0] as any;

      if (!page || page.missing !== undefined || !page.extract) {
        return null;
      }
      return page.extract as string;
    } catch {
      return null;
    }
  }

  private parseGuide(destination: string, text: string): WikivoyageGuide {
    const sections = this.splitSections(text);

    const overview =
      sections[''] ||
      sections['Understand'] ||
      text.split('\n\n')[0] ||
      '';

    const attractions = this.extractAttractions(
      sections['See'] ?? '',
      sections['Do'] ?? '',
    );

    const culturalTips = this.extractTips(
      sections['Respect'] ?? sections['Stay safe'] ?? sections['Understand'] ?? '',
    );

    const practicalInfo = [
      sections['Get around'] && `Getting around: ${sections['Get around'].slice(0, 300)}`,
      sections['Get in'] && `Getting there: ${sections['Get in'].slice(0, 200)}`,
    ]
      .filter(Boolean)
      .join('\n\n');

    return {
      destination,
      overview: overview.slice(0, 800),
      attractions,
      culturalTips,
      practicalInfo,
      rawSections: sections,
    };
  }

  /**
   * Split plain-text Wikivoyage extract into named sections
   */
  private splitSections(text: string): Record<string, string> {
    const sections: Record<string, string> = {};
    // Wikivoyage extracts use "\n== Section ==\n" pattern with explaintext
    const parts = text.split(/\n==+\s*([^=]+?)\s*==+\n/);
    // parts[0] = intro, then alternating: sectionName, sectionContent
    sections[''] = (parts[0] ?? '').trim();
    for (let i = 1; i < parts.length; i += 2) {
      const name = (parts[i] ?? '').trim();
      const content = (parts[i + 1] ?? '').trim();
      if (name) sections[name] = content;
    }
    return sections;
  }

  /**
   * Extract Attraction objects from See/Do section text
   */
  private extractAttractions(seeText: string, doText: string): Attraction[] {
    const attractions: Attraction[] = [];
    const combined = [
      ...this.parseAttractionLines(seeText, 'sight'),
      ...this.parseAttractionLines(doText, 'entertainment'),
    ];
    // Deduplicate by name
    const seen = new Set<string>();
    for (const a of combined) {
      if (!seen.has(a.name)) {
        seen.add(a.name);
        attractions.push(a);
      }
    }
    return attractions.slice(0, 20); // cap at 20
  }

  private parseAttractionLines(
    text: string,
    defaultType: Attraction['type'],
  ): Attraction[] {
    if (!text) return [];
    const results: Attraction[] = [];
    // Each attraction is typically a paragraph starting with a bold name or bullet
    const lines = text.split('\n').filter(l => l.trim().length > 20);

    for (const line of lines.slice(0, 30)) {
      const trimmed = line.trim().replace(/^\*\s*/, '');
      // First sentence is usually the name + short desc
      const dotIdx = trimmed.indexOf('.');
      const name = dotIdx > 0 ? trimmed.slice(0, dotIdx).trim() : trimmed.slice(0, 50);
      const description = trimmed.slice(0, 200);

      if (name.length < 3 || name.length > 80) continue;

      results.push({
        name,
        type: defaultType,
        description,
        estimatedDuration: 1.5,
        estimatedCost: 'low',
      });
    }
    return results;
  }

  private extractTips(text: string): string[] {
    if (!text) return [];
    return text
      .split('\n')
      .map(l => l.trim().replace(/^\*\s*/, ''))
      .filter(l => l.length > 20 && l.length < 300)
      .slice(0, 8);
  }

  private emptyGuide(destination: string): WikivoyageGuide {
    return {
      destination,
      overview: `${destination} is a popular travel destination. Check local guides for the latest information.`,
      attractions: [],
      culturalTips: [
        'Respect local customs and dress codes.',
        'Learn a few basic phrases in the local language.',
        'Keep copies of important documents.',
      ],
      practicalInfo: '',
      rawSections: {},
    };
  }
}

export const wikivoyage = new WikivoyageClient();
