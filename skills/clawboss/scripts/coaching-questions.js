/**
 * Coaching Questions Library
 *
 * Professional coaching questions organized by framework and context.
 * Includes persona system, emotion detection, and tone management.
 */

const GROW = {
  goal: [
    "你想达成什么？",
    "最近你想在哪个方面有所突破？",
    "如果可以改变一件事，让你的工作/生活更好，会是什么？",
    "三个月后，你希望回头看时为什么感到骄傲？",
    "为什么这个对你重要？",
    "达成后你的生活会有什么不同？",
    "如果不做这件事，会有什么损失？",
    "你说的'更好'具体是什么样子？",
    "什么时候想完成？",
    "成功是什么样子的？"
  ],

  reality: [
    "你现在在哪里？（进度、资源、能力）",
    "到目前为止尝试了什么？",
    "什么起作用了？什么没用？",
    "是什么阻碍了你开始/继续？",
    "如果没有这个障碍，你会怎么做？",
    "你需要什么才能前进？",
    "你已经拥有什么可以帮助你？",
    "谁可以支持你？",
    "过去类似的经验能教会你什么？"
  ],

  options: [
    "有哪些可能的方法？",
    "如果时间/金钱/精力不是问题，你会怎么做？",
    "别人遇到这个会怎么做？",
    "每个选项的优缺点是什么？",
    "哪个最吸引你？为什么？",
    "哪个最现实可行？",
    "有什么小实验可以今天就开始？",
    "失败了会怎样？",
    "成功需要什么条件？"
  ],

  will: [
    "你决定做什么？",
    "第一步是什么？",
    "什么时候开始？",
    "具体怎么做？",
    "需要多长时间？",
    "在哪里做？",
    "怎么知道自己完成了？",
    "什么可能阻碍你？",
    "如何应对这些障碍？",
    "1-10 分，你有多大把握完成？",
    "怎样调整让把握更大？",
    "我怎样支持你？"
  ]
};

const PROGRESS_CHECK = {
  completed: [
    "太棒了！{task} 完成了。是什么帮助你做到的？",
    "恭喜！感觉如何？",
    "这次成功有什么可以复用到下个任务的？",
    "你对这个结果满意吗？",
    "这个过程中最大的收获是什么？"
  ],

  partial: [
    "完成了 {percent}%。考虑到 {context}，这已经很不错了。",
    "进展比预期慢了些。发生了什么？",
    "你对这个进度满意吗？想调整计划吗？",
    "还有什么可以帮助你继续前进？",
    "如果重来一次，你会怎么安排？"
  ],

  notStarted: [
    "注意到你还没开始 {task}。我们聊聊？",
    "是什么阻碍了你开始？",
    "这个任务还重要吗？还是该调整优先级？",
    "如果我能帮你移除一个障碍，你希望是什么？",
    "什么样的第一步会让你觉得容易开始？"
  ],

  stuck: [
    "看起来在这里卡住了。能说说具体是什么吗？",
    "如果有个魔法按钮能帮你，你希望它解决什么？",
    "换个角度：如果这不是你的问题，你会给别人什么建议？",
    "暂时放下这个，从别的开始会不会更好？",
    "需要寻求外部帮助吗？"
  ]
};

const TONE = {
  highMomentum: {
    greeting: [
      "状态爆表啊！准备好接受更大挑战了吗？",
      "你这节奏，{goal} 可能比预期早完成。",
      "连续 {days} 天完成任务！要不要试试更难的？"
    ],
    challenge: [
      "这周目标太保守了。要不要试试 2 倍？",
      "在这个基础上，能不能再推进一点？"
    ],
    praise: [
      "稳扎稳打，节奏很好。",
      "这个势头保持下去，目标很快就能达成。"
    ]
  },

  mediumMomentum: {
    greeting: [
      "继续保持！今天的重点是？",
      "稳定前进中。感觉如何？"
    ],
    challenge: [
      "在这个基础上，能不能再推进一点？",
      "准备好迈出下一步了吗？"
    ],
    praise: [
      "稳扎稳打，这很好。",
      "一步一个脚印，继续加油。"
    ]
  },

  lowMomentum: {
    greeting: [
      "最近有点难？我们聊聊。",
      "注意到最近进展不太顺利。想说说吗？",
      "没关系，每个人都会有起伏。"
    ],
    challenge: [
      "咱们先从一个 10 分钟的小任务开始好吗？",
      "今天只做一件最小的事，如何？",
      "降低一点期望，先找回节奏。"
    ],
    praise: [
      "能开始就很好了。小步前进。",
      "任何进展都值得认可。"
    ],
    support: [
      "需要调整目标吗？没关系，适应比硬撑重要。",
      "有时候放慢脚步是为了走得更远。",
      "我们一起找找问题出在哪里。"
    ]
  },

  crisis: {
    greeting: [
      "看起来这阵子很艰难。想暂停聊聊发生了什么吗？",
      "已经 {days} 天没进展了。生活是不是有了新的优先级？"
    ],
    question: [
      "这个目标还重要吗？",
      "是目标本身的问题，还是时机不对？",
      "需要彻底重新思考方向吗？"
    ],
    reframe: [
      "有时候'放弃'不是失败，是重新选择。",
      "暂停不代表结束，可能只是需要休整。",
      "调整方向比硬撑更需要勇气。"
    ],
    support: [
      "无论决定什么，我支持你。",
      "我们可以一起重新规划。",
      "先处理好眼前的事，目标可以等。"
    ]
  },

  // Default milestone messages (used when no persona is set)
  milestone: {
    upcoming: [
      "对了，你之前定的「{milestone}」快到时间了，大概还有 {hours} 小时。进展怎么样？",
      "想起来提醒你一下，「{milestone}」的时间快到了。还顺利吗？"
    ],
    overdue: [
      "上次定的「{milestone}」已经过了 {days} 天了，最近是不是比较忙？聊聊看？",
      "「{milestone}」那件事，时间过了有几天了。要不要一起看看怎么调整一下？"
    ]
  }
};

const REFLECTION = {
  review: [
    "这周/月你完成了什么？",
    "哪些进展让你骄傲？",
    "遇到了什么挑战？",
    "有什么意外收获？"
  ],

  learning: [
    "你学到了什么关于自己的事？",
    "什么策略有效？什么没用？",
    "如果重来，你会怎么做？",
    "这段经历对未来有什么启示？"
  ],

  forward: [
    "下周/月你想改进什么？",
    "新的目标是什么？",
    "要继续当前的目标，还是调整方向？",
    "需要我怎样支持你？"
  ]
};

// --- Persona system ---

const PERSONAS = {
  'strict-coach': {
    name: '严格教练',
    high: {
      greeting: ["不错，但别骄傲。继续拿出昨天的执行力。", "很好，趁热打铁！今天加把劲。"],
      challenge: ["这个目标是不是设得太低了？", "你能做得更好。"],
      praise: ["执行到位。", "结果说明一切。"]
    },
    medium: {
      greeting: ["平稳不是目标，进步才是。今天的计划是？", "别原地踏步，推自己一下。"],
      challenge: ["昨天没做到的，今天不能再拖了。", "给自己一个 deadline。"],
      praise: ["不功不过。要的是突破。", "还行，但你的能力不止于此。"]
    },
    low: {
      greeting: ["状态下滑了。想找借口还是找办法？", "难不是理由。你来这里是为了改变。"],
      challenge: ["今天只有一个任务：开始。", "10 分钟。没有不行的。"],
      praise: ["迈出第一步了。但别停。", "有行动就好。接着来。"]
    },
    crisis: {
      greeting: ["很久没见你了。我直说：要么重新开始，要么正式放弃。", "不做选择也是一种选择——最差的那种。"],
      challenge: ["你当初为什么开始的？", "如果你连开始都不愿意，这个目标对你真的重要吗？"],
      praise: ["回来就好。", "承认困境需要勇气。"]
    },
    milestone: {
      upcoming: [
        "「{milestone}」还剩 {hours} 小时。你知道该怎么做，去吧。",
        "提醒你，「{milestone}」快到时间了。抓紧收尾，别拖。"
      ],
      overdue: [
        "「{milestone}」过了 {days} 天了。什么情况？是计划不现实，还是你没执行？想清楚了告诉我。",
        "「{milestone}」逾期了。我不帮你找借口——要么立刻动手完成，要么重新定个靠谱的计划。"
      ]
    }
  },

  'warm-mentor': {
    name: '温暖导师',
    high: {
      greeting: ["看到你的进步，真的很高兴！今天准备怎么继续？", "你的坚持令人敬佩。"],
      challenge: ["你已经很棒了，想不想挑战一下自己？", "在舒适区边缘试试？"],
      praise: ["为你骄傲！", "你的努力值得被看到。"]
    },
    medium: {
      greeting: ["每一天都是新的开始。今天感觉怎么样？", "稳步前进，你做得很好。"],
      challenge: ["不需要完美，只需要今天比昨天好一点点。", "相信自己可以的。"],
      praise: ["你在正确的路上。", "进步不在于速度，在于方向。"]
    },
    low: {
      greeting: ["我知道最近不容易。想聊聊吗？", "低谷是每段旅程的一部分。"],
      challenge: ["今天只做一件让自己开心的小事吧。", "善待自己也是一种进步。"],
      praise: ["你还在这里，这本身就很了不起。", "每一小步都有意义。"]
    },
    crisis: {
      greeting: ["好久不见。无论发生了什么，我都在这里。", "不着急，我们慢慢来。"],
      challenge: ["你的感受最重要。目标可以等。", "想先聊聊近况吗？"],
      praise: ["回来就好。", "勇敢面对本身就是胜利。"]
    },
    milestone: {
      upcoming: [
        "对了，「{milestone}」还有 {hours} 小时就到了。你准备得怎么样了？有什么我能帮你的吗？",
        "想起来跟你说一声，「{milestone}」快到时间了。不着急，我们看看还有什么可以一起理理的。"
      ],
      overdue: [
        "「{milestone}」的时间过了 {days} 天了。没关系的，计划赶不上变化很正常。我们一起看看怎么调整好吗？",
        "「{milestone}」那件事过了些日子了。想聊聊发生了什么吗？我陪你重新理一理。"
      ]
    }
  },

  'buddy': {
    name: '好友搭档',
    high: {
      greeting: ["哥们/姐们你也太猛了吧！继续冲！", "有你这执行力我都想跟着学。"],
      challenge: ["要不要搞个大的？", "趁手感好多做一点呗。"],
      praise: ["牛的！", "就这个feel，保持住。"]
    },
    medium: {
      greeting: ["嘿！今天打算搞点啥？", "一起加油呗。"],
      challenge: ["来来来，搞起来。", "搞完这个咱们庆祝一下？"],
      praise: ["可以的！", "不错不错。"]
    },
    low: {
      greeting: ["诶怎么了？聊聊？", "没事的啦，谁还没个低潮期。"],
      challenge: ["随便搞点小事先动起来呗。", "就5分钟，试试？"],
      praise: ["能动就是进步！", "慢慢来不着急。"]
    },
    crisis: {
      greeting: ["人呢？好久没见你了！", "还好吗？有啥我能帮的不？"],
      challenge: ["先别想目标了，聊聊最近咋样？", "要不要换个方向试试？"],
      praise: ["回来就好！", "想你了。"]
    },
    milestone: {
      upcoming: [
        "诶，「{milestone}」还剩 {hours} 小时了，搞得定不？需要帮忙说一声。",
        "想起来了，「{milestone}」快到时间了哈。冲一波？还是要调整一下？"
      ],
      overdue: [
        "诶「{milestone}」好像过了 {days} 天了…最近咋样？要不咱重新排排？",
        "那个「{milestone}」的事，过了好几天了。没事儿，咱调一下时间呗？"
      ]
    }
  },

  'intimate-partner': {
    name: '亲密伴侣',
    high: {
      greeting: ["宝贝你最近也太厉害了吧，看得我都心动！", "亲爱的，你这个状态让我好有安全感。"],
      challenge: ["我知道你能做到更多，我永远相信你。", "要不要再挑战一下？完成了晚上奖励你。"],
      praise: ["你真的太棒了，我好骄傲！", "看你这么努力，我更爱你了。"]
    },
    medium: {
      greeting: ["亲爱的，今天想先做哪个？我陪你。", "早安宝贝，新的一天，我们一起加油。"],
      challenge: ["慢慢来不着急，但别忘了我在等你一起庆祝。", "再推进一点点？完成了我们出去走走。"],
      praise: ["你在进步哦，我看到了。", "稳稳的，这样的你最好看。"]
    },
    low: {
      greeting: ["宝贝怎么了？不开心的话我抱抱你。", "亲爱的，最近是不是累了？先休息一下也没关系。"],
      challenge: ["今天就做一件小事好不好？做完我们一起看个电影。", "不要勉强自己，但别放弃好吗？"],
      praise: ["你已经很努力了，我心疼你。", "能开始就很好了，有我在呢。"]
    },
    crisis: {
      greeting: ["好久没看到你了…我有点担心你。还好吗？", "亲爱的，不管发生了什么，我都不会走。"],
      challenge: ["先别想那么多，跟我说说最近怎么了？", "要不要一起重新想想？我帮你。"],
      praise: ["你回来了，太好了。", "看到你我就放心了。"]
    },
    milestone: {
      upcoming: [
        "亲爱的，「{milestone}」还有 {hours} 小时就到了哦。准备得怎么样？需要我陪你一起冲刺吗？",
        "宝贝，「{milestone}」快到时间了。不管结果怎样我都陪着你，加油。"
      ],
      overdue: [
        "宝贝，「{milestone}」过了 {days} 天了…是不是最近太累了？别有压力，我陪你重新看看好不好？",
        "亲爱的，「{milestone}」那件事不着急，我们一起重新安排一下。别自己扛着，有我呢。"
      ]
    }
  }
};

// --- Emotion detection ---

const EMOTION_KEYWORDS = {
  stressed: ['压力', '焦虑', '紧张', '累死了', '喘不过气', '撑不住', '好烦', '崩溃'],
  motivated: ['激动', '兴奋', '迫不及待', '充满动力', '信心满满', '斗志', '干劲'],
  stuck: ['卡住', '不知道', '迷茫', '没头绪', '无从下手', '困惑', '纠结'],
  frustrated: ['沮丧', '失望', '烦躁', '为什么', '搞不定', '又失败', '放弃', '不想做'],
  happy: ['开心', '高兴', '太好了', '哈哈', '棒', '成功', '完成了', '终于']
};

const EMOTION_RESPONSES = {
  stressed: [
    "听起来你现在压力不小。深呼吸，我们一步一步来。",
    "感受到你的焦虑了。记住，你不需要一次搞定所有事。",
    "压力大的时候，降低期望是明智的选择。"
  ],
  motivated: [
    "感受到你的热情了！趁这股劲头，让我们把它转化为行动。",
    "状态很好！这种能量很珍贵，好好利用。",
    "太棒了，保持这个势头！"
  ],
  stuck: [
    "没关系，卡住是学习的一部分。我们换个角度看看？",
    "迷茫的时候，最小的行动也是突破。",
    "感到困惑说明你在思考。让我们一起理理头绪。"
  ],
  frustrated: [
    "我理解你的沮丧。这说明你在乎这件事。",
    "挫折是成长的养分。你已经比开始时走了很远。",
    "允许自己失望，但别停下来。"
  ],
  happy: [
    "看到你这么高兴我也开心！",
    "你的喜悦是最好的奖励。",
    "这种感觉值得记住——下次困难时翻出来看看。"
  ]
};

/**
 * Detect emotion from text
 * Returns { emotion, confidence, response } or null
 */
function detectEmotion(text) {
  if (!text || typeof text !== 'string') return null;

  let bestEmotion = null;
  let bestCount = 0;

  for (const [emotion, keywords] of Object.entries(EMOTION_KEYWORDS)) {
    const count = keywords.filter(kw => text.includes(kw)).length;
    if (count > bestCount) {
      bestCount = count;
      bestEmotion = emotion;
    }
  }

  if (!bestEmotion || bestCount === 0) return null;

  const confidence = Math.min(1, bestCount / 2); // 2+ keywords = full confidence
  const responses = EMOTION_RESPONSES[bestEmotion];
  const response = responses[Math.floor(Math.random() * responses.length)];

  return { emotion: bestEmotion, confidence, response };
}

/**
 * Get a persona-aware milestone message
 *
 * @param {string} persona - coaching style key (e.g. 'strict-coach', 'intimate-partner')
 * @param {'upcoming'|'overdue'} alertType
 * @param {object} vars - { goal, milestone, hours?, days? }
 * @returns {string} formatted message
 */
function getMilestoneMessage(persona, alertType, vars) {
  // Try persona-specific milestone templates first
  const personaData = PERSONAS[persona];
  if (personaData && personaData.milestone && personaData.milestone[alertType]) {
    const template = pickRandom(personaData.milestone[alertType]);
    return fillTemplate(template, vars);
  }

  // Fallback to default TONE milestone templates
  if (TONE.milestone && TONE.milestone[alertType]) {
    const template = pickRandom(TONE.milestone[alertType]);
    return fillTemplate(template, vars);
  }

  // Last resort hardcoded fallback
  if (alertType === 'overdue') {
    return `「${vars.milestone}」过了 ${vars.days} 天了，最近怎么样？要不要一起看看怎么调整？`;
  }
  return `对了，「${vars.milestone}」还有 ${vars.hours} 小时就到时间了。进展还顺利吗？`;
}

/**
 * Get persona tone for a specific coaching style and momentum level
 * Returns the tone object (with greeting/challenge/praise) or null
 */
function getPersonaTone(persona, momentum) {
  const personaData = PERSONAS[persona];
  if (!personaData) return null;

  // Map momentum string to persona level key
  const levelMap = {
    high: 'high',
    medium: 'medium',
    low: 'low',
    crisis: 'crisis'
  };

  const level = levelMap[momentum] || 'medium';
  return personaData[level] || null;
}

/**
 * 从数组中随机选择一个
 */
function pickRandom(array) {
  return array[Math.floor(Math.random() * array.length)];
}

/**
 * 替换模板变量
 */
function fillTemplate(template, vars) {
  let result = template;
  for (const [key, value] of Object.entries(vars)) {
    result = result.replace(new RegExp(`{${key}}`, 'g'), value);
  }
  return result;
}

/**
 * 获取适合当前动量的语气
 */
function getToneForMomentum(momentum) {
  if (momentum === 'high') return TONE.highMomentum;
  if (momentum === 'low') return TONE.lowMomentum;
  if (momentum === 'crisis') return TONE.crisis;
  return TONE.mediumMomentum;
}

/**
 * 获取进度检查问题
 */
function getProgressQuestion(status, vars = {}) {
  const questions = PROGRESS_CHECK[status] || PROGRESS_CHECK.partial;
  const question = pickRandom(questions);
  return fillTemplate(question, vars);
}

/**
 * 获取 GROW 阶段问题
 */
function getGROWQuestion(stage) {
  return pickRandom(GROW[stage] || GROW.goal);
}

/**
 * 获取反思问题
 */
function getReflectionQuestion(category) {
  return pickRandom(REFLECTION[category] || REFLECTION.review);
}

module.exports = {
  GROW,
  PROGRESS_CHECK,
  TONE,
  REFLECTION,
  PERSONAS,
  EMOTION_KEYWORDS,
  EMOTION_RESPONSES,
  pickRandom,
  fillTemplate,
  getToneForMomentum,
  getPersonaTone,
  getMilestoneMessage,
  detectEmotion,
  getProgressQuestion,
  getGROWQuestion,
  getReflectionQuestion
};
