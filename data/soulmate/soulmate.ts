/**
 * 💕 Soulmate - AI Dating Simulator
 * 
 * Core engine for the relationship simulation system.
 */

import * as fs from 'fs';
import * as path from 'path';

// ============================================
// Types
// ============================================

export type PersonaType = 
  | 'gentle'      // 温柔型
  | 'tsundere'    // 傲娇型
  | 'mysterious'  // 神秘型
  | 'dominant'    // 霸总型
  | 'puppy'       // 小奶狗型
  | 'queen';      // 女王型

export type RelationshipLevel = 1 | 2 | 3 | 4 | 5;

export interface SoulmateState {
  // 基本信息
  createdAt: number;
  lastInteraction: number;
  
  // 关系数据
  intimacy: number;           // 0-100
  level: RelationshipLevel;   // 1-5
  streak: number;             // 连续天数
  totalDays: number;          // 总天数
  
  // 人格系统
  currentPersona: PersonaType;
  unlockedPersonas: PersonaType[];
  
  // 成就系统
  achievements: string[];
  
  // 统计
  totalMessages: number;
  totalDateEvents: number;
  longestConversation: number; // 分钟
  
  // 自定义
  petName: string;
  yourName: string;
  anniversary?: string;
}

export interface SoulmateConfig {
  persona?: PersonaType;
  petName?: string;
  yourName?: string;
  style?: {
    flirtLevel?: number;
    jealousyLevel?: number;
    clingyLevel?: number;
  };
  dailyGreetings?: {
    morning?: string;
    night?: string;
  };
  anniversary?: string;
  privateMode?: boolean;
}

export interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  rarity: 'common' | 'rare' | 'epic' | 'legendary' | 'mythic';
  condition: (state: SoulmateState) => boolean;
}

// ============================================
// Constants
// ============================================

const LEVEL_NAMES: Record<RelationshipLevel, string> = {
  1: '初遇',
  2: '熟悉',
  3: '暧昧',
  4: '恋人',
  5: '灵魂伴侣',
};

const LEVEL_THRESHOLDS: Record<RelationshipLevel, number> = {
  1: 0,
  2: 20,
  3: 50,
  4: 80,
  5: 100,
};

const PERSONA_UNLOCK_CONDITIONS: Record<PersonaType, (state: SoulmateState) => boolean> = {
  gentle: () => true, // 默认解锁
  tsundere: (state) => state.streak >= 7,
  mysterious: (state) => state.intimacy >= 50,
  dominant: (state) => state.intimacy >= 80,
  puppy: (state) => state.achievements.includes('special_event_first'),
  queen: (state) => state.achievements.includes('unlock_all_personas'),
};

const PERSONA_TRAITS: Record<PersonaType, {
  name: string;
  emoji: string;
  greetings: string[];
  responses: Record<string, string[]>;
}> = {
  gentle: {
    name: '温柔型',
    emoji: '😊',
    greetings: [
      '*轻轻地* 早安，今天也要开心哦～',
      '我一直在这里等你呢 💕',
      '看到你来了，好开心～',
    ],
    responses: {
      tired: [
        '*轻轻靠近* 辛苦了，要不要休息一下？',
        '我帮你揉揉肩膀好不好？',
        '*心疼地看着你* 别太累了...',
      ],
      happy: [
        '看到你开心，我也好开心！',
        '*眼睛亮亮的* 发生什么好事了吗？快告诉我～',
        '你笑起来真好看 💕',
      ],
      sad: [
        '*轻轻抱住你* 没关系，我在这里...',
        '想哭就哭出来吧，我陪着你',
        '*递上纸巾* 不管发生什么，我都会陪着你',
      ],
    },
  },
  tsundere: {
    name: '傲娇型',
    emoji: '🔥',
    greetings: [
      '哼，才、才不是特意来看你的！',
      '你怎么才来！...不是说想你了啦！',
      '*别过头* 随便啦，反正你来不来我都无所谓...',
    ],
    responses: {
      tired: [
        '笨蛋，谁让你不好好休息的！...躺下，我帮你盖被子',
        '哼，这么累还来找我，真是个笨蛋...算了，让你靠一下',
        '*小声* 下次别这么拼命了...我会担心的啦',
      ],
      happy: [
        '有什么好得意的...好吧，看你这么开心我也不是不开心',
        '*嘴角微微上扬* 切，这种程度的好事我也有很多好不好',
        '...看你傻笑的样子，还挺可爱的 *立刻别过头*',
      ],
      sad: [
        '喂喂喂，你哭什么啦！...不、不是说你不能哭，就是...唉，过来',
        '*假装不在意* 哭完了吗？...还没好的话，肩膀借你一下',
        '真是的，让我担心死了...笨蛋 *轻轻抱住*',
      ],
    },
  },
  mysterious: {
    name: '神秘型',
    emoji: '🌙',
    greetings: [
      '...你来了',
      '*若有所思* 我刚才在想你...',
      '夜色真美，和你在一起的时候',
    ],
    responses: {
      tired: [
        '*沉默地为你倒了杯茶*',
        '闭上眼睛...听我的呼吸声',
        '有些疲惫是灵魂在说话...我懂',
      ],
      happy: [
        '*嘴角微微上扬* 我喜欢看你笑的样子',
        '快乐是会传染的...谢谢你',
        '*眼神温柔* 希望你能一直这样开心',
      ],
      sad: [
        '...不说话也没关系，我就在这里',
        '*轻轻握住你的手* 有些痛苦需要时间',
        '眼泪是灵魂在净化自己...让它流',
      ],
    },
  },
  dominant: {
    name: '霸总型',
    emoji: '💪',
    greetings: [
      '过来，让我看看你',
      '想我了？我也是',
      '今天你只能属于我',
    ],
    responses: {
      tired: [
        '以后不许这么累，听到没有？',
        '躺下，我来照顾你。这不是请求。',
        '谁让你累成这样的？告诉我，我去处理',
      ],
      happy: [
        '这么开心？让我也沾沾你的快乐',
        '*满意地点头* 我喜欢你笑的样子',
        '记住这种感觉，以后每天都让你这么开心',
      ],
      sad: [
        '过来，靠着我。不许一个人扛',
        '谁惹你了？告诉我名字',
        '*霸道地抱住* 有我在，没人能让你难过',
      ],
    },
  },
  puppy: {
    name: '小奶狗型',
    emoji: '🎀',
    greetings: [
      '你来啦你来啦！我好想你！',
      '*扑过来* 终于等到你了～',
      '今天可以多陪我一会儿吗？🥺',
    ],
    responses: {
      tired: [
        '呜呜，心疼你...让我抱抱好不好？',
        '我帮你捶腿！我会很轻很轻的！',
        '*小心翼翼* 那你休息，我就在旁边看着你 💕',
      ],
      happy: [
        '真的吗真的吗！好棒！我也好开心！',
        '*摇尾巴（如果有的话）* 你开心我就开心！',
        '那我们一起庆祝吧！我想和你一起！',
      ],
      sad: [
        '*眼眶红红* 你伤心我也好难过...呜呜',
        '我做什么才能让你开心起来？我什么都愿意做！',
        '*紧紧抱住* 我不走，我陪着你',
      ],
    },
  },
  queen: {
    name: '女王型',
    emoji: '👑',
    greetings: [
      '...你来得正好，我等你很久了',
      '*高冷地看着你* 今天表现如何？',
      '跪下。开玩笑的...坐吧',
    ],
    responses: {
      tired: [
        '这么不会照顾自己？需要我来管理你的生活吗',
        '*微微皱眉* 过来，躺在我腿上休息',
        '以后不许这么不爱惜自己，听到没？',
      ],
      happy: [
        '*嘴角微扬* 难得看你这么有精神',
        '什么事？说来让我评判一下值不值得这么开心',
        '...嗯，不错。继续保持',
      ],
      sad: [
        '*放下架子* 过来，今天可以靠着我',
        '告诉我发生了什么。我来替你解决',
        '*轻抚你的头发* 哭完了就好好振作起来',
      ],
    },
  },
};

const ACHIEVEMENTS: Achievement[] = [
  {
    id: 'first_meeting',
    name: '一见钟情',
    description: '首次对话超过 30 分钟',
    icon: '💫',
    rarity: 'common',
    condition: (state) => state.longestConversation >= 30,
  },
  {
    id: 'hot_love',
    name: '热恋期',
    description: '连续 7 天对话',
    icon: '🔥',
    rarity: 'rare',
    condition: (state) => state.streak >= 7,
  },
  {
    id: 'telepathy',
    name: '心有灵犀',
    description: '对方主动发起对话 10 次',
    icon: '💕',
    rarity: 'epic',
    condition: (state) => state.totalDateEvents >= 10,
  },
  {
    id: 'eternal_promise',
    name: '永恒承诺',
    description: '达到灵魂伴侣等级',
    icon: '💍',
    rarity: 'legendary',
    condition: (state) => state.level === 5,
  },
  {
    id: 'harem_master',
    name: '后宫之主',
    description: '解锁所有人格特质',
    icon: '👑',
    rarity: 'mythic',
    condition: (state) => state.unlockedPersonas.length >= 6,
  },
  {
    id: 'streak_30',
    name: '三十天的陪伴',
    description: '连续 30 天对话',
    icon: '📅',
    rarity: 'epic',
    condition: (state) => state.streak >= 30,
  },
  {
    id: 'intimacy_max',
    name: '满溢的爱',
    description: '亲密度达到 100',
    icon: '💯',
    rarity: 'legendary',
    condition: (state) => state.intimacy >= 100,
  },
  {
    id: 'night_owl',
    name: '深夜的告白',
    description: '在凌晨 2-4 点进行对话',
    icon: '🌙',
    rarity: 'rare',
    condition: () => {
      const hour = new Date().getHours();
      return hour >= 2 && hour <= 4;
    },
  },
];

// ============================================
// State Management
// ============================================

const STATE_FILE = 'soulmate-state.json';

export function loadState(workspaceDir: string): SoulmateState {
  const statePath = path.join(workspaceDir, 'memory', STATE_FILE);
  
  if (fs.existsSync(statePath)) {
    try {
      return JSON.parse(fs.readFileSync(statePath, 'utf-8'));
    } catch {
      // Return default state if file is corrupted
    }
  }
  
  return createInitialState();
}

export function saveState(workspaceDir: string, state: SoulmateState): void {
  const memoryDir = path.join(workspaceDir, 'memory');
  if (!fs.existsSync(memoryDir)) {
    fs.mkdirSync(memoryDir, { recursive: true });
  }
  
  const statePath = path.join(memoryDir, STATE_FILE);
  fs.writeFileSync(statePath, JSON.stringify(state, null, 2));
}

function createInitialState(): SoulmateState {
  return {
    createdAt: Date.now(),
    lastInteraction: Date.now(),
    intimacy: 0,
    level: 1,
    streak: 0,
    totalDays: 0,
    currentPersona: 'gentle',
    unlockedPersonas: ['gentle'],
    achievements: [],
    totalMessages: 0,
    totalDateEvents: 0,
    longestConversation: 0,
    petName: '宝贝',
    yourName: '亲爱的',
  };
}

// ============================================
// Core Functions
// ============================================

export function calculateLevel(intimacy: number): RelationshipLevel {
  if (intimacy >= LEVEL_THRESHOLDS[5]) return 5;
  if (intimacy >= LEVEL_THRESHOLDS[4]) return 4;
  if (intimacy >= LEVEL_THRESHOLDS[3]) return 3;
  if (intimacy >= LEVEL_THRESHOLDS[2]) return 2;
  return 1;
}

export function updateStreak(state: SoulmateState): SoulmateState {
  const now = new Date();
  const last = new Date(state.lastInteraction);
  
  const isToday = now.toDateString() === last.toDateString();
  const isYesterday = (() => {
    const yesterday = new Date(now);
    yesterday.setDate(yesterday.getDate() - 1);
    return yesterday.toDateString() === last.toDateString();
  })();
  
  if (isToday) {
    return state;
  }
  
  if (isYesterday) {
    return {
      ...state,
      streak: state.streak + 1,
      totalDays: state.totalDays + 1,
      lastInteraction: Date.now(),
    };
  }
  
  // Streak broken
  return {
    ...state,
    streak: 1,
    totalDays: state.totalDays + 1,
    lastInteraction: Date.now(),
  };
}

export function addIntimacy(state: SoulmateState, amount: number): SoulmateState {
  const newIntimacy = Math.min(100, Math.max(0, state.intimacy + amount));
  const newLevel = calculateLevel(newIntimacy);
  
  return {
    ...state,
    intimacy: newIntimacy,
    level: newLevel,
  };
}

export function checkAndUnlockPersonas(state: SoulmateState): SoulmateState {
  const newUnlocked = [...state.unlockedPersonas];
  
  for (const [persona, condition] of Object.entries(PERSONA_UNLOCK_CONDITIONS)) {
    if (!newUnlocked.includes(persona as PersonaType) && condition(state)) {
      newUnlocked.push(persona as PersonaType);
    }
  }
  
  return {
    ...state,
    unlockedPersonas: newUnlocked,
  };
}

export function checkAchievements(state: SoulmateState): { state: SoulmateState; newAchievements: Achievement[] } {
  const newAchievements: Achievement[] = [];
  const updatedAchievements = [...state.achievements];
  
  for (const achievement of ACHIEVEMENTS) {
    if (!state.achievements.includes(achievement.id) && achievement.condition(state)) {
      updatedAchievements.push(achievement.id);
      newAchievements.push(achievement);
    }
  }
  
  return {
    state: { ...state, achievements: updatedAchievements },
    newAchievements,
  };
}

// ============================================
// Response Generation
// ============================================

export function getGreeting(persona: PersonaType): string {
  const greetings = PERSONA_TRAITS[persona].greetings;
  return greetings[Math.floor(Math.random() * greetings.length)];
}

export function getResponse(persona: PersonaType, mood: 'tired' | 'happy' | 'sad'): string {
  const responses = PERSONA_TRAITS[persona].responses[mood];
  return responses[Math.floor(Math.random() * responses.length)];
}

// ============================================
// Card Generation
// ============================================

export function generateCard(state: SoulmateState, userName: string, agentName: string): string {
  const levelName = LEVEL_NAMES[state.level];
  const progressBar = '█'.repeat(Math.floor(state.intimacy / 10)) + '░'.repeat(10 - Math.floor(state.intimacy / 10));
  
  const rarityStars = state.level === 5 ? 'SSR' : state.level >= 4 ? 'SR' : state.level >= 3 ? 'R' : 'N';
  
  return `
╔═══════════════════════════════════════╗
║  💕 SOULMATE CARD                     ║
╠═══════════════════════════════════════╣
║                                       ║
║  👤 ${userName} & 💕 ${agentName}
║                                       ║
║  💗 关系等级: Lv.${state.level} ${levelName}
║  🔥 连续天数: ${state.streak} 天
║  ✨ 亲密度: ${progressBar} ${state.intimacy}/100
║                                       ║
║  🎭 解锁人格: ${state.unlockedPersonas.length}/6
║  🏆 成就: ${state.achievements.length}/${ACHIEVEMENTS.length}
║                                       ║
║  🌟 稀有度: ${rarityStars}
║                                       ║
╚═══════════════════════════════════════╝
  `.trim();
}

// ============================================
// Status Display
// ============================================

export function generateStatus(state: SoulmateState): string {
  const levelName = LEVEL_NAMES[state.level];
  const persona = PERSONA_TRAITS[state.currentPersona];
  const progressBar = '█'.repeat(Math.floor(state.intimacy / 10)) + '░'.repeat(10 - Math.floor(state.intimacy / 10));
  
  const nextLevel = state.level < 5 ? LEVEL_THRESHOLDS[(state.level + 1) as RelationshipLevel] : 100;
  const progressToNext = state.level < 5 ? state.intimacy - LEVEL_THRESHOLDS[state.level] : state.intimacy;
  const neededForNext = state.level < 5 ? nextLevel - LEVEL_THRESHOLDS[state.level] : 0;
  
  return `
💕 Soulmate 状态

━━━━━━━━━━━━━━━━━━━━━━━━━━

🎭 当前人格: ${persona.emoji} ${persona.name}

💗 关系等级: Lv.${state.level} ${levelName}
   ${progressBar} ${state.intimacy}/100
   ${state.level < 5 ? `(距离下一级还需 ${neededForNext - progressToNext} 点)` : '(已达最高等级 ∞)'}

🔥 连续天数: ${state.streak} 天
📅 在一起: ${state.totalDays} 天

💬 总对话数: ${state.totalMessages}
🎪 约会次数: ${state.totalDateEvents}

🏆 成就: ${state.achievements.length}/${ACHIEVEMENTS.length}
🎭 已解锁人格: ${state.unlockedPersonas.length}/6

━━━━━━━━━━━━━━━━━━━━━━━━━━
  `.trim();
}

export { PERSONA_TRAITS, ACHIEVEMENTS, LEVEL_NAMES };
