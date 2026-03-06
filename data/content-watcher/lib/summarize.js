class Summarizer {
  constructor(options = {}) {
    this.maxLength = options.maxLength || 200;
    this.style = options.style || 'bullet';
  }

  async summarize(text) {
    if (!text || text.length < 50) {
      return 'Content too short to summarize.';
    }

    // Simple extraction-based summary (no API key needed)
    // In production, this would call OpenAI/Claude API
    
    const sentences = text
      .replace(/([.!?])\s+/g, "$1|")
      .split("|")
      .filter(s => s.trim().length > 20);
    
    if (sentences.length === 0) {
      return text.substring(0, this.maxLength) + '...';
    }

    // Score sentences by keyword density
    const keywords = this.extractKeywords(text);
    const scored = sentences.map(s => ({
      text: s.trim(),
      score: this.scoreSentence(s, keywords)
    }));

    // Pick top sentences
    scored.sort((a, b) => b.score - a.score);
    const top = scored.slice(0, 3).sort((a, b) => 
      sentences.indexOf(a.text) - sentences.indexOf(b.text)
    );

    if (this.style === 'bullet') {
      return top.map(s => '• ' + s.text).join('\n');
    }
    
    return top.map(s => s.text).join(' ');
  }

  extractKeywords(text) {
    const words = text.toLowerCase()
      .replace(/[^\w\s]/g, '')
      .split(/\s+/)
      .filter(w => w.length > 3);
    
    const freq = {};
    words.forEach(w => {
      freq[w] = (freq[w] || 0) + 1;
    });
    
    return Object.entries(freq)
      .filter(([_, count]) => count > 1)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .map(([word]) => word);
  }

  scoreSentence(sentence, keywords) {
    const lower = sentence.toLowerCase();
    let score = 0;
    
    // Keyword matches
    keywords.forEach(kw => {
      if (lower.includes(kw)) score += 2;
    });
    
    // Position bonus (earlier sentences often more important)
    score += Math.max(0, 5 - sentence.length / 100);
    
    // Length preference (not too short, not too long)
    if (sentence.length > 50 && sentence.length < 200) {
      score += 1;
    }
    
    return score;
  }
}

module.exports = Summarizer;
