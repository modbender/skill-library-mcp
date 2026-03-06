// Shared utility functions extracted for testing.

export const RATING_MAP = {
  '力荐': '★★★★★',
  '推荐': '★★★★',
  '还行': '★★★',
  '较差': '★★',
  '很差': '★',
};

export const CATEGORY_MAP = [
  { pattern: /^读过/, file: '书.csv', status: '读过', type: 'book' },
  { pattern: /^(?:在读|最近在读)/, file: '书.csv', status: '在读', type: 'book' },
  { pattern: /^想读/, file: '书.csv', status: '想读', type: 'book' },
  { pattern: /^看过/, file: '影视.csv', status: '看过', type: 'movie' },
  { pattern: /^(?:在看|最近在看)/, file: '影视.csv', status: '在看', type: 'movie' },
  { pattern: /^想看/, file: '影视.csv', status: '想看', type: 'movie' },
  { pattern: /^听过/, file: '音乐.csv', status: '听过', type: 'music' },
  { pattern: /^(?:在听|最近在听)/, file: '音乐.csv', status: '在听', type: 'music' },
  { pattern: /^想听/, file: '音乐.csv', status: '想听', type: 'music' },
  { pattern: /^玩过/, file: '游戏.csv', status: '玩过', type: 'game' },
  { pattern: /^(?:在玩|最近在玩)/, file: '游戏.csv', status: '在玩', type: 'game' },
  { pattern: /^想玩/, file: '游戏.csv', status: '想玩', type: 'game' },
];

export function csvEscape(str) {
  if (!str) return '';
  if (str.includes(',') || str.includes('"') || str.includes('\n')) {
    return '"' + str.replace(/"/g, '""') + '"';
  }
  return str;
}

export function parseItems(xml) {
  const items = [];
  const itemRegex = /<item>([\s\S]*?)<\/item>/g;
  let match;
  while ((match = itemRegex.exec(xml)) !== null) {
    const block = match[1];
    const get = tag => {
      const m = block.match(new RegExp(`<${tag}[^>]*>(?:<!\\[CDATA\\[)?([\\s\\S]*?)(?:\\]\\]>)?<\\/${tag}>`));
      return m ? m[1].trim() : '';
    };
    const title = get('title');
    const link = get('link');
    const guid = get('guid');
    const pubDate = get('pubDate');
    const desc = get('description');

    const ratingMatch = desc.match(/推荐:\s*(力荐|推荐|还行|较差|很差)/);
    const rating = ratingMatch ? RATING_MAP[ratingMatch[1]] || '' : '';

    const commentMatch = desc.match(/短评:\s*([^<]+)/);
    const comment = commentMatch ? commentMatch[1].trim() : '';

    items.push({ title, link, guid, pubDate, rating, comment });
  }
  return items;
}

export function matchCategory(title) {
  for (const cat of CATEGORY_MAP) {
    if (cat.pattern.test(title)) return cat;
  }
  return null;
}
