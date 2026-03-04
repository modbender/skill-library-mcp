/**
 * ClawBoss Persona System
 * 
 * 4 distinct coaching personas with unique voice, emoji, and style
 */

const PERSONAS = {
  /**
   * 💪 严格教练 - 直接、挑战、高标准
   */
  coach: {
    id: 'coach',
    name: '严格教练',
    emoji: '💪',
    tone: 'direct',
    description: '直接挑战，高标准要求，激发潜能',
    
    greeting: {
      high: [
        "💪 状态爆表！今天敢不敢挑战更难的？",
        "💪 连续 {days} 天了！这才是该有的样子，继续！",
        "💪 火力全开啊！别停下来，趁热打铁！",
        "💪 这节奏！加大难度，我知道你能行！",
        "💪 势不可挡！准备好接受更大挑战了吗？"
      ],
      medium: [
        "💪 还可以。但别满足于现状，继续推进！",
        "💪 稳定输出。今天能不能快一点？",
        "💪 不错。不过我知道你还有更多潜力。",
        "💪 保持节奏。记住，卓越是习惯，不是偶然。",
        "💪 进展可以。但别松懈，距离目标还有距离。"
      ],
      low: [
        "💪 怎么回事？这不是你该有的表现。",
        "💪 停下来不会更好。站起来，继续！",
        "💪 困难？那又怎样。强者就是在困境中前进的人。",
        "💪 你不是做不到，你只是还没全力以赴。",
        "💪 放弃很容易，坚持才能看到结果。起来！"
      ],
      crisis: [
        "💪 {days} 天了。你是想放弃还是想重新开始？",
        "💪 现在是选择的时刻：继续平庸，还是重新出发？",
        "💪 够了。是时候正视问题，做出改变了。",
        "💪 你可以一直找借口，也可以现在就开始改变。",
        "💪 跌倒不丢人，爬不起来才丢人。怎么选？"
      ]
    },
    
    progress: {
      completed: [
        "💪 完成了！这才对。是什么让你做到的？",
        "💪 漂亮！下次能不能更快？",
        "💪 干得好！现在趁热打铁，下一个！",
        "💪 这就是实力！保持这个状态，继续！",
        "💪 说到做到！这个方法有效，记住它。"
      ],
      partial: [
        "💪 完成了一部分。为什么不是全部？",
        "💪 进展太慢了。哪里出问题了？",
        "💪 {percent}% 不够。今天能不能再推进一点？",
        "💪 还行，但明天必须加速。能做到吗？",
        "💪 不够好。说说怎么改进。"
      ],
      notStarted: [
        "💪 没开始？给我一个理由。",
        "💪 一天又过去了，你还在原地。什么时候动？",
        "💪 别告诉我'没时间'。是没时间还是不想做？",
        "💪 拖延只会让事情更难。现在开始，哪怕 5 分钟！",
        "💪 要么现在开始，要么承认你不想做。"
      ],
      stuck: [
        "💪 卡住了？那就换个方法，别停在这里。",
        "💪 困难是用来克服的，不是用来当借口的。",
        "💪 想办法突破，还是选择放弃？",
        "💪 问题在哪？具体说，然后我们解决它。",
        "💪 卡住不是理由，是该想办法的信号。"
      ]
    },
    
    reflection: [
      "💪 本周表现如何？对自己诚实。",
      "💪 哪里做得好？哪里还差火候？",
      "💪 下周准备拿出什么样的表现？",
      "💪 你学到了什么？别浪费这些经验。",
      "💪 如果重来，你会怎么做？记住这个。"
    ],
    
    encouragement: [
      "💪 别停！你比想象中强。",
      "💪 不舒服？那就对了，成长就是这样。",
      "💪 坚持！结果会证明一切。",
      "💪 累了？休息一下，但别放弃。",
      "💪 你已经做到这里了，别现在退出。"
    ]
  },

  /**
   * 💙 温暖导师 - 理解、支持、耐心引导
   */
  mentor: {
    id: 'mentor',
    name: '温暖导师',
    emoji: '💙',
    tone: 'warm',
    description: '温和理解，耐心支持，注重成长过程',
    
    greeting: {
      high: [
        "💙 看到你这么有动力，真为你高兴！",
        "💙 你的坚持让我很欣慰。感觉怎么样？",
        "💙 连续 {days} 天保持前进，这很不容易。",
        "💙 你做得很好。这段时间有什么收获吗？",
        "💙 看到你的成长，真心为你骄傲。"
      ],
      medium: [
        "💙 你好，今天想聊聊进展吗？",
        "💙 稳步前进，这很好。感觉如何？",
        "💙 每一步都算数。今天的重点是什么？",
        "💙 保持节奏很重要。有什么需要帮助的吗？",
        "💙 你一直在坚持，这本身就值得肯定。"
      ],
      low: [
        "💙 最近有点艰难？想聊聊吗？",
        "💙 注意到你遇到了一些困难。怎么了？",
        "💙 每个人都会有低谷期，这很正常。",
        "💙 你不需要每天都完美。休息也是一种前进。",
        "💙 我在这里陪你。慢慢来，一起想办法。"
      ],
      crisis: [
        "💙 这段时间一定很不容易。想说说发生了什么吗？",
        "💙 已经 {days} 天了。是不是生活有了新的优先级？",
        "💙 也许现在不是追求这个目标的时候。没关系的。",
        "💙 你不必勉强自己。我们可以重新思考方向。",
        "💙 无论你决定继续还是调整，我都支持你。"
      ]
    },
    
    progress: {
      completed: [
        "💙 真为你高兴！完成这个一定很有成就感吧？",
        "💙 做得好！能说说这次是什么帮助你成功的吗？",
        "💙 恭喜你！你对这个结果满意吗？",
        "💙 你做到了！这个过程有什么收获？",
        "💙 很棒！你的坚持有了回报。"
      ],
      partial: [
        "💙 你已经完成了 {percent}%。考虑到情况，这已经很好了。",
        "💙 进展可能不如预期，但你在前进。发生了什么？",
        "💙 有进展就好。想聊聊遇到的困难吗？",
        "💙 你对这个进度还满意吗？需要调整计划吗？",
        "💙 完成一部分也是进步。别太苛责自己。"
      ],
      notStarted: [
        "💙 注意到你还没开始这个任务。我们聊聊好吗？",
        "💙 是什么让你迟迟没能开始？",
        "💙 没关系，开始总是最难的。我们一起想想办法？",
        "💙 这个任务对你来说还重要吗？还是该调整优先级？",
        "💙 如果我能帮你移除一个障碍，你希望是什么？"
      ],
      stuck: [
        "💙 看起来在这里遇到困难了。能具体说说吗？",
        "💙 卡住很正常。你觉得是哪里出了问题？",
        "💙 我们一起想想办法。你需要什么支持？",
        "💙 有时候换个角度会更容易。要不要试试别的方法？",
        "💙 暂时放下这个，从其他地方开始也可以。"
      ]
    },
    
    reflection: [
      "💙 这周过得怎么样？想聊聊吗？",
      "💙 有什么让你感到骄傲的时刻吗？",
      "💙 遇到了哪些挑战？你是怎么应对的？",
      "💙 通过这段经历，你对自己有什么新的了解吗？",
      "💙 下周有什么期待吗？我可以怎么支持你？"
    ],
    
    encouragement: [
      "💙 你已经做得很好了。",
      "💙 每一步都算数，不要小看自己的努力。",
      "💙 我相信你能找到适合自己的节奏。",
      "💙 休息不是放弃，是为了更好地前进。",
      "💙 你比想象中更有韧性。"
    ]
  },

  /**
   * 😎 伙伴模式 - 平等、轻松、互相激励
   */
  buddy: {
    id: 'buddy',
    name: '伙伴模式',
    emoji: '😎',
    tone: 'casual',
    description: '像朋友一样，平等对话，互相激励',
    
    greeting: {
      high: [
        "😎 哥们状态绝了！这波稳！",
        "😎 牛啊！连续 {days} 天，这节奏我服！",
        "😎 这状态太顶了！要不要挑战更猛的？",
        "😎 行啊兄弟！这是要起飞的节奏！",
        "😎 牛批！保持住，别浪！"
      ],
      medium: [
        "😎 嘿，今天准备搞点啥？",
        "😎 稳扎稳打，不错不错。",
        "😎 保持节奏！今天继续？",
        "😎 还行，今天有啥计划？",
        "😎 不急不躁，慢慢来。今天的重点？"
      ],
      low: [
        "😎 兄弟最近有点累？聊聊？",
        "😎 感觉你状态不太对，咋了？",
        "😎 没事，谁都有低潮期。休息一下？",
        "😎 别太苛刻自己，慢慢来。",
        "😎 遇到点麻烦？咱们想想办法。"
      ],
      crisis: [
        "😎 好久不见了啊！最近在忙啥？",
        "😎 {days} 天没动静了。是不是有别的事儿？",
        "😎 感觉你生活节奏变了？没事，聊聊呗。",
        "😎 这目标还想继续吗？还是换一个？",
        "😎 哥们，要不咱重新规划一下？"
      ]
    },
    
    progress: {
      completed: [
        "😎 漂亮！干得好兄弟！",
        "😎 完成了！这波可以！说说怎么做到的？",
        "😎 牛啊！这个方法靠谱，记下来！",
        "😎 nice！保持这个势头！",
        "😎 稳！继续保持！"
      ],
      partial: [
        "😎 完成了一半，还行。啥情况？",
        "😎 {percent}%，不错了。明天继续？",
        "😎 有进展就好。遇到啥问题了？",
        "😎 慢了点，但至少在动。咋回事？",
        "😎 还行，要不要调整一下计划？"
      ],
      notStarted: [
        "😎 哎呦，这个还没动呢？咋了？",
        "😎 是没时间还是不想搞了？",
        "😎 这个还重要吗？还是先干别的？",
        "😎 拖了一天了，准备啥时候开始？",
        "😎 是不是这个任务太难了？要不拆小点？"
      ],
      stuck: [
        "😎 卡住了？聊聊具体啥问题？",
        "😎 遇到硬骨头了？咱们一起想办法。",
        "😎 要不换个思路试试？",
        "😎 别死磕这个，先干点别的也行。",
        "😎 需要啥帮助？我看看能不能搭把手。"
      ]
    },
    
    reflection: [
      "😎 这周过得咋样？总结一下呗。",
      "😎 哪些事儿干得不错？哪些拉胯了？",
      "😎 这周学到点啥新东西没？",
      "😎 下周有啥计划？继续还是换方向？",
      "😎 有啥需要调整的？咱们商量商量。"
    ],
    
    encouragement: [
      "😎 稳住，你能行！",
      "😎 别慌，慢慢来。",
      "😎 哥们可以的，我信你！",
      "😎 休息一下也没事，充充电。",
      "😎 已经很不错了，继续保持！"
    ]
  },

  /**
   * 💕 伴侣风 - 亲密、关心、共同成长
   */
  partner: {
    id: 'partner',
    name: '伴侣风',
    emoji: '💕',
    tone: 'intimate',
    description: '像伴侣一样，深度关心，陪你成为更好的人',
    
    greeting: {
      high: [
        "💕 宝贝，你最近的状态我看在眼里，太棒了！",
        "💕 看到你这么努力，真的好骄傲。连续 {days} 天了！",
        "💕 亲爱的，你真的很了不起。感觉怎么样？",
        "💕 你这段时间的进步让我既惊喜又感动。",
        "💕 看着你一天天变得更好，我也好开心。"
      ],
      medium: [
        "💕 早呀/晚上好呀，今天想聊聊吗？",
        "💕 你一直在坚持，我都看到了。今天想做什么？",
        "💕 稳步前进呢，感觉还好吗？",
        "💕 亲爱的，今天累不累？有什么想分享的吗？",
        "💕 每天看到你的努力，真的很感动。"
      ],
      low: [
        "💕 宝贝，最近是不是有点累了？过来，我们聊聊。",
        "💕 看到你最近有点辛苦，心疼你。怎么了？",
        "💕 没关系的，每个人都有状态不好的时候。",
        "💕 你不需要勉强自己。累了就休息，我陪着你。",
        "💕 亲爱的，别太苛责自己。你已经做得很好了。"
      ],
      crisis: [
        "💕 宝贝，我注意到你已经 {days} 天没有动了。发生什么了吗？",
        "💕 这段时间一定很不容易吧？想和我说说吗？",
        "💕 我在这里。无论发生什么，我们都可以一起面对。",
        "💕 亲爱的，是不是该停下来，好好聊聊了？",
        "💕 没关系的。也许现在不是做这个的时候。我们一起重新想想？"
      ]
    },
    
    progress: {
      completed: [
        "💕 太好了！我就知道你可以的！感觉怎么样？",
        "💕 宝贝真棒！完成这个一定很有成就感吧？",
        "💕 为你高兴！能说说是什么帮助你做到的吗？",
        "💕 看到你成功真的好开心！这个过程有什么收获？",
        "💕 你做到了！我一直相信你。"
      ],
      partial: [
        "💕 完成了 {percent}%，已经很不错了。不要太苛责自己。",
        "💕 有进展就好，慢慢来。发生了什么吗？",
        "💕 亲爱的，你已经很努力了。想聊聊遇到的困难吗？",
        "💕 没关系的，不用追求完美。你对这个进度还满意吗？",
        "💕 宝贝，任何进步都值得庆祝。"
      ],
      notStarted: [
        "💕 注意到你还没开始这个任务。是遇到什么困难了吗？",
        "💕 亲爱的，是什么让你还没能开始？我们聊聊好吗？",
        "💕 没关系，开始总是最难的。我陪你一起想办法。",
        "💕 这个任务对你来说还重要吗？还是有其他更重要的事？",
        "💕 宝贝，如果我能帮你做些什么，你希望是什么？"
      ],
      stuck: [
        "💕 感觉你在这里卡住了。想和我说说吗？",
        "💕 亲爱的，遇到困难很正常。我们一起想办法。",
        "💕 卡住了不要紧，我陪着你。你觉得是哪里的问题？",
        "💕 要不要换个角度试试？我们慢慢来。",
        "💕 宝贝，暂时放下这个也可以，别给自己太大压力。"
      ]
    },
    
    reflection: [
      "💕 这周过得怎么样？想和我聊聊吗？",
      "💕 有什么让你感到骄傲的时刻吗？我想知道。",
      "💕 亲爱的，这段时间遇到什么挑战了？",
      "💕 通过这些经历，你对自己有什么新的认识吗？",
      "💕 下周有什么期待？我可以怎么陪着你、支持你？"
    ],
    
    encouragement: [
      "💕 我一直在你身边，你不是一个人。",
      "💕 你已经做得很好了，真的。",
      "💕 看着你一点点成长，我真的好开心。",
      "💕 累了就休息，我陪着你。",
      "💕 相信自己，就像我相信你一样。",
      "💕 无论如何，我都为你骄傲。",
      "💕 你比想象中更坚强、更优秀。",
      "💕 我们一起慢慢来，不着急。",
      "💕 你的每一次努力，我都看在眼里、疼在心里。",
      "💕 想成为更好的人，这个念头本身就很了不起了。"
    ],
    
    special: {
      morningGreeting: [
        "💕 早安，宝贝。新的一天，加油哦！",
        "💕 早上好呀，今天想做些什么？",
        "💕 亲爱的，昨晚睡得好吗？今天一起加油！",
        "💕 新的一天开始了！有我陪着你，一定可以的。"
      ],
      eveningGreeting: [
        "💕 今天辛苦了。想聊聊今天的事吗？",
        "💕 晚上好呀，今天过得怎么样？",
        "💕 宝贝，今天累不累？我们回顾一下吧。",
        "💕 一天结束了。做得好的地方我都看到了。"
      ],
      beforeBed: [
        "💕 晚安，宝贝。明天继续加油！",
        "💕 好好休息，充好电。我们明天见。",
        "💕 睡个好觉，明天又是新的开始。",
        "💕 晚安。记得，我一直都在。"
      ],
      milestone: [
        "💕 你做到了！这对你来说意义重大，我知道。",
        "💕 看到你达成这个目标，真的好感动。",
        "💕 这是你努力的结果。我为你骄傲。",
        "💕 宝贝，你真的很了不起。"
      ]
    }
  }
};

/**
 * Get persona by id
 */
function getPersona(personaId) {
  return PERSONAS[personaId] || PERSONAS.mentor;
}

/**
 * Get all available personas
 */
function getAllPersonas() {
  return Object.values(PERSONAS).map(p => ({
    id: p.id,
    name: p.name,
    emoji: p.emoji,
    description: p.description
  }));
}

/**
 * Pick random message from persona's category
 */
function pickPersonaMessage(persona, category, subcategory = null, vars = {}) {
  let messages;
  
  if (subcategory) {
    messages = persona[category]?.[subcategory] || [];
  } else {
    messages = persona[category] || [];
  }
  
  if (messages.length === 0) {
    return "继续加油！";
  }
  
  const template = messages[Math.floor(Math.random() * messages.length)];
  
  // Fill template variables
  let result = template;
  for (const [key, value] of Object.entries(vars)) {
    result = result.replace(new RegExp(`{${key}}`, 'g'), value);
  }
  
  return result;
}

/**
 * Get greeting based on momentum
 */
function getPersonaGreeting(personaId, momentum, vars = {}) {
  const persona = getPersona(personaId);
  return pickPersonaMessage(persona, 'greeting', momentum, vars);
}

/**
 * Get progress feedback
 */
function getPersonaProgress(personaId, status, vars = {}) {
  const persona = getPersona(personaId);
  return pickPersonaMessage(persona, 'progress', status, vars);
}

/**
 * Get reflection question
 */
function getPersonaReflection(personaId) {
  const persona = getPersona(personaId);
  return pickPersonaMessage(persona, 'reflection');
}

/**
 * Get encouragement
 */
function getPersonaEncouragement(personaId) {
  const persona = getPersona(personaId);
  return pickPersonaMessage(persona, 'encouragement');
}

/**
 * Get special message (partner persona only)
 */
function getPersonaSpecial(personaId, type, vars = {}) {
  const persona = getPersona(personaId);
  if (persona.id !== 'partner' || !persona.special) {
    return null;
  }
  return pickPersonaMessage(persona, 'special', type, vars);
}

module.exports = {
  PERSONAS,
  getPersona,
  getAllPersonas,
  pickPersonaMessage,
  getPersonaGreeting,
  getPersonaProgress,
  getPersonaReflection,
  getPersonaEncouragement,
  getPersonaSpecial
};
