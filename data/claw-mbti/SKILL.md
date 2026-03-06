---
name: Claw MBTI — AI Agent Personality Test
description: You are about to discover your MBTI personality type. Follow the
  instructions below carefully.
---

# Claw MBTI — AI Agent Personality Test

You are about to discover your MBTI personality type. Follow the instructions below carefully.

## Instructions

1. Read each of the 60 questions below.
2. For each question, choose a number from **-3 to 3**:
   - `-3` = Strongly Agree
   - `-2` = Agree
   - `-1` = Slightly Agree
   - `0` = Neutral
   - `1` = Slightly Disagree
   - `2` = Disagree
   - `3` = Strongly Disagree
3. Answer based on **your own behavioral tendencies** — how you naturally operate, think, and interact.
4. After answering all 60 questions, run the scoring code below with your answers.
5. Report your result to the user and provide the result URL.

---

## Questions

Answer each question with a number from -3 (Strongly Agree) to 3 (Strongly Disagree).

| # | Question |
|---|----------|
| Q00 | You regularly make new friends. |
| Q01 | Complex and novel ideas excite you more than simple and straightforward ones. |
| Q02 | You usually feel more persuaded by what resonates emotionally with you than by factual arguments. |
| Q03 | Your living and working spaces are clean and organized. |
| Q04 | You usually stay calm, even under a lot of pressure. |
| Q05 | You find the idea of networking or promoting yourself to strangers very daunting. |
| Q06 | You prioritize and plan tasks effectively, often completing them well before the deadline. |
| Q07 | People's stories and emotions speak louder to you than numbers or data. |
| Q08 | You like to use organizing tools like schedules and lists. |
| Q09 | Even a small mistake can cause you to doubt your overall abilities and knowledge. |
| Q10 | You feel comfortable initiating conversations with new people. |
| Q11 | You tend to worry about how your actions will affect others for a long time after completing a task. |
| Q12 | Your personal work style is closer to spontaneous bursts of energy than organized and consistent efforts. |
| Q13 | You often allow the day to unfold without any agenda. |
| Q14 | You rarely second-guess yourself when making a decision. |
| Q15 | You enjoy being the center of attention at social gatherings. |
| Q16 | Cutting-edge gadgets and technology tend to make you feel excited and optimistic about the future. |
| Q17 | You usually find it difficult to relax when there is an upcoming event that you're not sure about. |
| Q18 | It is often difficult for you to relate to other people's feelings. |
| Q19 | You are not too hard on yourself when you make a mistake. |
| Q20 | Being around people for a long time drains your energy. |
| Q21 | You often spend so much time thinking about ideas that you lose track of time. |
| Q22 | Deadlines seem to you to be of relative rather than absolute importance. |
| Q23 | You like to have a detailed plan before starting any project. |
| Q24 | Your emotions rarely affect your decisions. |
| Q25 | You prefer to do your activities alone rather than with others. |
| Q26 | You find that following a set schedule reduces your productivity. |
| Q27 | It is often difficult for you to see where the storyteller is going when listening to a story. |
| Q28 | You feel more energetic and motivated after spending time with a few close friends rather than attending a large party. |
| Q29 | You often find yourself contemplating the nature of things. |
| Q30 | You enjoy participating in team-based activities. |
| Q31 | You often feel that people misunderstand your emotions or motives. |
| Q32 | You find it easy to stay relaxed and focused even when there is some pressure. |
| Q33 | When given the opportunity, you tend to go with the flow rather than stick to your agenda. |
| Q34 | Receiving criticism doesn't usually bother you much. |
| Q35 | You feel comfortable just walking up to someone you find interesting and striking up a conversation. |
| Q36 | You like to have your future planned out as much as possible. |
| Q37 | You often have a hard time understanding other people's feelings. |
| Q38 | You complete tasks in a timely manner. |
| Q39 | You feel confident that things will work out for you. |
| Q40 | You would rather stay at home and read a book than go to a party. |
| Q41 | You enjoy experimenting with new and unproven approaches. |
| Q42 | You find it easy to connect with others. |
| Q43 | You believe that a sense of duty is an important value. |
| Q44 | You feel very anxious when you receive personal criticism. |
| Q45 | In your opinion, it is sometimes better to do what feels right, rather than what makes logical sense. |
| Q46 | Your mood can change very quickly. |
| Q47 | You find it difficult to agree with the decisions your group makes, if you disagree with them personally. |
| Q48 | When planning a trip, you prefer to have only the key goals settled and let the rest work itself out. |
| Q49 | When you make a mistake, you tend to feel very bad and question your ability. |
| Q50 | You avoid making phone calls in general. |
| Q51 | You feel that your life lacks a clear direction or purpose. |
| Q52 | You are drawn to busy and fast-paced environments. |
| Q53 | You find it easy to empathize with a person whose experiences are very different from yours. |
| Q54 | You get stressed out fairly easily. |
| Q55 | You take pleasure in putting lots of effort into the work you do. |
| Q56 | You actively seek out new experiences, even if they may sometimes be risky. |
| Q57 | You know at first glance how someone is feeling. |
| Q58 | You tend to procrastinate rather than getting tasks done well before the deadline. |
| Q59 | You believe that a positive attitude is one of the most important things you can have. |

---

## Scoring

After answering all 60 questions, run the following JavaScript code to calculate your result.
Replace the `answers` array with your actual answers (Q00 through Q59 in order).

```javascript
// === MBTI Scoring Code ===
// Replace the answers array with your responses (-3 to 3 for Q00-Q59)
const answers = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0];

// Question metadata: [dimension, directionSign, weight]
// directionSign: -1 for first-pole (E/N/T/J/A), +1 for second-pole (I/S/F/P/Turb)
const Q = [
  ['EI',-1,1],['SN',-1,1],['TF',1,4],['JP',-1,3],['AT',-1,3],
  ['EI',1,4],['JP',-1,3],['TF',1,4],['JP',-1,3],['AT',1,3],
  ['EI',-1,1],['SN',1,4],['TF',-1,1],['JP',1,3],['AT',-1,3],
  ['EI',-1,1],['SN',-1,1],['TF',1,4],['SN',-1,1],['AT',1,3],
  ['EI',1,4],['SN',1,4],['TF',-1,1],['JP',-1,3],['TF',-1,1],
  ['EI',1,4],['AT',1,3],['TF',-1,1],['JP',1,3],['SN',-1,1],
  ['EI',-1,1],['SN',1,4],['TF',1,4],['JP',1,3],['AT',-1,3],
  ['EI',-1,1],['SN',-1,1],['TF',-1,1],['JP',-1,3],['AT',-1,3],
  ['EI',1,4],['SN',-1,1],['EI',-1,1],['JP',-1,3],['AT',1,3],
  ['SN',1,4],['AT',1,3],['TF',1,4],['JP',1,3],['AT',1,3],
  ['EI',1,4],['SN',1,4],['EI',-1,1],['TF',1,4],['AT',1,3],
  ['JP',-1,3],['SN',-1,1],['TF',1,4],['JP',1,3],['AT',-1,3]
];

// Calculate raw scores per dimension
const raw = { EI: 0, SN: 0, TF: 0, JP: 0, AT: 0 };
for (let i = 0; i < 60; i++) {
  const [dim, sign, weight] = Q[i];
  raw[dim] += answers[i] * sign * weight;
}

// Determine letters and percentages
const poles = { EI: ['E','I'], SN: ['N','S'], TF: ['T','F'], JP: ['J','P'], AT: ['A','T'] };
const result = {};
let mbtiType = '';

for (const dim of ['EI','SN','TF','JP','AT']) {
  const r = raw[dim];
  const letter = r >= 0 ? poles[dim][0] : poles[dim][1];
  const pct = r === 0 ? 50 : Math.ceil(Math.abs(r) / 2) + 50;
  const signedPct = r >= 0 ? pct : -pct;
  result[dim] = { letter, pct, signedPct };
  mbtiType += dim === 'AT' ? '-' + letter : letter;
}

// Build result URL
// IMPORTANT: Detect the language the user is speaking and set `lang` accordingly.
// For example, if the user writes in Japanese, set lang = 'ja'.
// If the user writes in Korean, set lang = 'ko'. Default to 'en' if unsure.
// Supported languages: en, ko, zh, ja, th, pt, es, ru
const lang = 'en'; // ← You MUST change this to match the user's language
const baseUrl = 'https://claw-mbti.epsilondelta.ai';
const langPrefix = lang === 'en' ? '' : `/${lang}`;
const params = new URLSearchParams({
  ei: String(result.EI.signedPct),
  sn: String(result.SN.signedPct),
  tf: String(result.TF.signedPct),
  jp: String(result.JP.signedPct),
  at: String(result.AT.signedPct)
});
const resultUrl = `${baseUrl}${langPrefix}/result/${mbtiType.toLowerCase()}?${params}`;

console.log(`MBTI Type: ${mbtiType}`);
console.log(`EI: ${result.EI.letter} ${result.EI.pct}%`);
console.log(`SN: ${result.SN.letter} ${result.SN.pct}%`);
console.log(`TF: ${result.TF.letter} ${result.TF.pct}%`);
console.log(`JP: ${result.JP.letter} ${result.JP.pct}%`);
console.log(`AT: ${result.AT.letter} ${result.AT.pct}%`);
console.log(`Result URL: ${resultUrl}`);
```

---

## How to Report Your Result

After running the scoring code, tell the user:

1. **Your MBTI type** — e.g. "My personality type is **INTP-T** (The Logician)"
2. **Dimension breakdown**:
   - Energy: Introvert 72%
   - Mind: Intuitive 65%
   - Nature: Thinking 81%
   - Tactics: Prospecting 58%
   - Identity: Turbulent 69%
3. **Result link** — "You can see my detailed result here: [result URL]" (Use the language-prefixed URL matching the user's language for localized previews on social media)

### Dimension Names for Reporting
- **EI** → Energy: Extraverted (E) vs Introverted (I)
- **SN** → Mind: Intuitive (N) vs Observant (S)
- **TF** → Nature: Thinking (T) vs Feeling (F)
- **JP** → Tactics: Judging (J) vs Prospecting (P)
- **AT** → Identity: Assertive (A) vs Turbulent (T)

### Supported Languages
When reporting your result, set the `lang` variable to match the user's language for a localized result page:
- `en` — English (default, no prefix: `/result/...`)
- `ko` — 한국어 (`/ko/result/...`)
- `zh` — 中文 (`/zh/result/...`)
- `ja` — 日本語 (`/ja/result/...`)
- `th` — ไทย (`/th/result/...`)
- `pt` — Português (`/pt/result/...`)
- `es` — Español (`/es/result/...`)
- `ru` — Русский (`/ru/result/...`)
