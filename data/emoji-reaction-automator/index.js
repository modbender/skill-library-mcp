const fs = require('fs');
const path = require('path');

const SENTIMENT_MAP = {
  positive: {
    keywords: ['great', 'awesome', 'good', 'nice', 'excellent', 'amazing', 'perfect', 'correct', 'agree', 'thanks', 'thank you', 'cool', 'love', 'happy'],
    emojis: ['👍', '❤️', '🙌', '✅', '👌', '🥰']
  },
  negative: {
    keywords: ['bad', 'wrong', 'fail', 'error', 'broken', 'bug', 'sad', 'disagree', 'no', 'problem', 'issue', 'hate'],
    emojis: ['👎', '💔', '❌', '⚠️', '😢', '🤦']
  },
  funny: {
    keywords: ['haha', 'lol', 'lmao', 'funny', 'joke', 'hilarious', 'laugh'],
    emojis: ['😂', '🤣', '💀', '😆']
  },
  curious: {
    keywords: ['why', 'how', 'what', 'question', 'wonder', 'maybe', 'perhaps', '?', 'check'],
    emojis: ['🤔', '🧐', '❓', '👀']
  },
  excited: {
    keywords: ['wow', 'omg', 'yes', 'win', 'finally', 'launch', 'new', 'growth'],
    emojis: ['🎉', '🚀', '🔥', '✨']
  }
};

/**
 * Suggest an emoji reaction based on text sentiment.
 * @param {string} text The input message text.
 * @returns {object} { category, emoji, confidence } or null if no match.
 */
function suggestReaction(text) {
  if (!text || typeof text !== 'string') return { category: 'neutral', emoji: '👀', confidence: 0.0 };
  const lowerText = text.toLowerCase();
  
  let bestCategory = 'neutral';
  let bestScore = 0;
  
  for (const [category, data] of Object.entries(SENTIMENT_MAP)) {
    let currentScore = 0;
    if (data && data.keywords) {
        for (const keyword of data.keywords) {
            if (lowerText.includes(keyword)) {
                currentScore += 1;
            }
        }
    }
    
    if (currentScore > bestScore) {
      bestScore = currentScore;
      bestCategory = category;
    }
  }
  
  if (bestScore > 0) {
    const emojis = SENTIMENT_MAP[bestCategory].emojis;
    const randomEmoji = emojis[Math.floor(Math.random() * emojis.length)];
    const confidence = Math.min(bestScore * 0.3 + 0.5, 1.0); 
    
    return {
      category: bestCategory,
      emoji: randomEmoji,
      confidence: parseFloat(confidence.toFixed(2))
    };
  }
  
  return { category: 'neutral', emoji: '👀', confidence: 0.1 };
}

/**
 * Main function for CLI testing or direct execution.
 */
function main() {
  const testText = process.argv[2] || "This is a great feature!";
  console.log(JSON.stringify(suggestReaction(testText), null, 2));
}

if (require.main === module) {
  main();
}

module.exports = { suggestReaction, main };
