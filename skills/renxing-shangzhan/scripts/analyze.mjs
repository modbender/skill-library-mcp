#!/usr/bin/env node

// 人性商战手册 - AI分析引擎

const triggers = {
  DESIRE: {
    name: "欲望",
    triggers: {
      "贪婪": { logic: "追求利益最大化，永不满足", case: "拼多多百亿补贴、赌场、彩票" },
      "虚荣": { logic: "通过外在认可获得自我价值感", case: "奢侈品、限量款、排行榜" },
      "色欲": { logic: "对异性/美好事物的追求", case: "医美、健身、社交APP" },
      "权力欲": { logic: "控制欲和支配欲", case: "会员等级、特权服务" },
      "好奇心": { logic: "对新事物的探索欲", case: "盲盒、悬念营销" },
      "自由欲": { logic: "摆脱约束的渴望", case: "自由职业、定制服务" },
      "效能感": { logic: "追求效率和成就感", case: "效率APP、快捷服务" }
    }
  },
  FEAR: {
    name: "恐惧",
    triggers: {
      "生存焦虑": { logic: "担心被淘汰或无法生存", case: "知识付费、职场竞争" },
      "损失厌恶": { logic: "失去的痛苦大于获得的快乐", case: "限时折扣、过期作废" },
      "社交孤立": { logic: "担心被群体排斥", case: "社群会员、圈子文化" },
      "后果恐惧": { logic: "担心负面结果", case: "保险、健康产品" },
      "贫穷焦虑": { logic: "对贫困的恐惧", case: "理财、副业培训" }
    }
  },
  BIOLOGICAL: {
    name: "生物性",
    triggers: {
      "领地意识": { logic: "占有欲和保护欲", case: "房产、私人管家" },
      "部落性": { logic: "族群认同感", case: "粉丝经济，品牌忠诚度" },
      "等级序列": { logic: "追求更高地位", case: "VIP制度、排行榜" },
      "社交梳毛": { logic: "社交互动需求", case: "社交网络、社群" }
    }
  },
  MORAL: {
    name: "道德",
    triggers: {
      "道德高地": { logic: "站在道德制高点", case: "公益营销、环保产品" },
      "公平本能": { logic: "追求公正对待", case: "差评制度、评价体系" },
      "感恩亏欠": { logic: "接受帮助后想回报", case: "试用装、小礼品" }
    }
  },
  EXISTENTIAL: {
    name: "存在",
    triggers: {
      "意义追寻": { logic: "寻找人生价值和意义", case: "知识付费、成长社群" },
      "传承留名": { logic: "想留下痕迹", case: "NFT、纪念品" },
      "自我实现": { logic: "追求个人成长", case: "培训、教练服务" }
    }
  },
  SOCIAL: {
    name: "社交",
    triggers: {
      "互惠心理": { logic: "礼尚往来", case: "邀请好友得奖励" },
      "攀比嫉妒": { logic: "与他人比较", case: "排行榜、晒单" },
      "归属感": { logic: "渴望被接纳", case: "会员社群、粉丝团" }
    }
  },
  COGNITIVE: {
    name: "认知",
    triggers: {
      "锚定效应": { logic: "参考点影响决策", case: "原价999现价99" },
      "权威崇拜": { logic: "相信专家背书", case: "明星代言、专家推荐" },
      "稀缺性": { logic: "越少越珍贵", case: "限量发售、限时供应" }
    }
  },
  WEAKNESS: {
    name: "弱点",
    triggers: {
      "懒惰": { logic: "追求省时省力", case: "一键下单、上门服务" },
      "沉没成本": { logic: "已投入不想放弃", case: "会员积分、连续签到" },
      "即时满足": { logic: "想要立即看到结果", case: "秒到账、即时反馈" },
      "从众心理": { logic: "跟随大众选择", case: "热销榜单、销量第一" }
    }
  }
};

// 商业模式关键词映射
const businessKeywords = {
  "拼多多": ["贪婪", "损失厌恶", "沉没成本", "互惠心理", "从众心理"],
  "京东": ["效率感", "品质保证", "次日达"],
  "淘宝": ["选择多样", "价格比较", "从众心理"],
  "抖音": ["好奇心", "即时满足", "算法推荐", "社交孤立"],
  "快手": ["好奇心", "土味内容", "社交"],
  "小红书": ["虚荣", "攀比嫉妒", "种草", "美学"],
  "微信": ["社交", "归属感", "效率"],
  "美团": ["懒惰", "效率", "本地生活"],
  "滴滴": ["懒惰", "效率", "安全"],
  "支付宝": ["效率", "安全", "信用"],
  "保险": ["后果恐惧", "生存焦虑", "贫穷焦虑"],
  "奢侈品": ["虚荣", "等级序列", "稀缺性"],
  "盲盒": ["好奇心", "即时满足", "沉没成本"],
  "知识付费": ["生存焦虑", "知识焦虑", "自我实现"],
  "健身": ["自我实现", "社交", "健康"],
  "医美": ["虚荣", "色欲", "社交孤立"],
  "奶茶": ["社交", "从众", "即时满足"],
  "咖啡": ["社交", "效能感", "习惯"],
  "会员": ["沉没成本", "损失厌恶", "归属感"],
  "积分": ["沉没成本", "贪婪", "损失厌恶"],
  "砍一刀": ["贪婪", "沉没成本", "互惠心理", "从众心理"],
  "限量": ["稀缺性", "虚荣", "攀比嫉妒"],
  "排行榜": ["攀比嫉妒", "虚荣", "等级序列"],
  "邀请": ["互惠心理", "贪婪", "社交"],
  "社群": ["归属感", "社交", "部落性"]
};

// 目标人群画像库
const audienceProfiles = {
  "儿童": { age: "0-12", fears: ["生存焦虑"], desires: ["好奇心", "效能感"], weaknesses: ["即时满足"] },
  "青少年": { age: "13-18", fears: ["社交孤立", "后果恐惧"], desires: ["虚荣", "权力欲", "自由欲"], weaknesses: ["从众心理", "即时满足"] },
  "中青年男性": { age: "25-45", fears: ["生存焦虑", "贫穷焦虑", "后果恐惧"], desires: ["权力欲", "效能感", "色欲"], weaknesses: ["懒惰", "沉没成本"] },
  "中青年女性": { age: "25-45", fears: ["社交孤立", "后果恐惧", "生存焦虑"], desires: ["虚荣", "色欲", "自我实现"], weaknesses: ["从众心理", "即时满足"] },
  "银发族": { age: "50+", fears: ["生存焦虑", "后果恐惧", "社交孤立"], desires: ["传承留名", "健康", "归属感"], weaknesses: ["沉没成本", "权威崇拜"] },
  "大学生": { age: "18-24", fears: ["生存焦虑", "贫穷焦虑", "社交孤立"], desires: ["好奇心", "自由欲", "自我实现"], weaknesses: ["从众心理", "即时满足"] },
  "职场人": { age: "22-50", fears: ["生存焦虑", "贫穷焦虑", "后果恐惧"], desires: ["权力欲", "效能感", "自我实现"], weaknesses: ["懒惰", "沉没成本"] },
  "全职妈妈": { age: "25-40", fears: ["社交孤立", "生存焦虑", "后果恐惧"], desires: ["虚荣", "归属感", "自我实现"], weaknesses: ["从众心理", "即时满足"] },
  "创业者": { age: "25-45", fears: ["生存焦虑", "贫穷焦虑", "后果恐惧"], desires: ["权力欲", "自我实现", "自由欲"], weaknesses: ["沉没成本", "贪婪"] },
  "单身": { age: "20-40", fears: ["社交孤立", "生存焦虑"], desires: ["色欲", "好奇心", "自由欲"], weaknesses: ["即时满足", "从众心理"] }
};

const args = process.argv.slice(2);

// 商业模式分析
if (args[0] === "--analyze" && args[1]) {
  const business = args.slice(1).join(" ");
  console.log(`\n🔍 分析商业模式: ${business}\n`);
  console.log("=".repeat(50));
  
  const matched = [];
  const businessLower = business.toLowerCase();
  
  for (const [keyword, triggerList] of Object.entries(businessKeywords)) {
    if (businessLower.includes(keyword)) {
      for (const t of triggerList) {
        for (const [cat, info] of Object.entries(triggers)) {
          if (info.triggers[t]) {
            matched.push({ cat: info.name, name: t, ...info.triggers[t] });
          }
        }
      }
    }
  }
  
  const unique = matched.filter((v,i,a)=>a.findIndex(t=>(t.name===v.name))===i);
  
  if (unique.length > 0) {
    console.log("\n【涉及的人性诱因】");
    unique.forEach((m, i) => {
      console.log(`\n${i+1}. ${m.name} (${m.cat})`);
      console.log(`   底层逻辑: ${m.logic}`);
      console.log(`   经典案例: ${m.case}`);
    });
  } else {
    console.log("\n请提供更具体的商业模式描述");
  }
  process.exit(0);
}

// 人性组合模拟
if (args[0] === "--fusion" && args[1]) {
  const triggerNames = args.slice(1);
  
  console.log(`\n🎯 人性组合实验室`);
  console.log(`输入诱因: ${triggerNames.join(" + ")}\n`);
  console.log("=".repeat(50));
  
  const found = [];
  for (const name of triggerNames) {
    for (const [cat, info] of Object.entries(triggers)) {
      if (info.triggers[name]) {
        found.push({ name, cat: info.name, ...info.triggers[name] });
        break;
      }
    }
  }
  
  if (found.length === 0) {
    console.log("未找到匹配的诱因");
    process.exit(1);
  }
  
  console.log("\n【商业流程逻辑链】");
  console.log("触发 → 需求 → 行动 → 复购 → 传播");
  
  console.log("\n【诱因组合威力评估】");
  const power = Math.min(found.length * 33, 100);
  console.log(`综合威力: ${"█".repeat(Math.floor(power/10))}${"░".repeat(10-Math.floor(power/10))} ${power}%`);
  console.log(`协同效应: ${found.length > 1 ? "强烈（多维触发）" : "单一"}`);
  
  console.log("\n【可执行市场策略】");
  found.forEach((f, i) => {
    console.log(`\n策略${i+1}: 利用${f.name}`);
    console.log(`  底层逻辑: ${f.logic}`);
    console.log(`  落地方法: ${f.case}`);
  });
  
  process.exit(0);
}

// AI商业顾问
if (args[0] === "--advisor" || args[0] === "-a") {
  const idea = args.slice(1).join(" ");
  
  console.log(`\n🤖 AI人性商战顾问`);
  console.log(`商业想法: ${idea}\n`);
  console.log("=".repeat(50));
  
  // 智能分析 - 基于关键词推断目标人群和诱因
  const ideaLower = idea.toLowerCase();
  let targetAudience = "中青年";
  let matchedTriggers = [];
  
  // 推断目标人群
  if (ideaLower.includes("大学生") || ideaLower.includes("校园") || ideaLower.includes("考研") || ideaLower.includes("考公")) {
    targetAudience = "大学生";
  } else if (ideaLower.includes("妈妈") || ideaLower.includes("育儿") || ideaLower.includes("宝宝") || ideaLower.includes("母婴")) {
    targetAudience = "全职妈妈";
  } else if (ideaLower.includes("老人") || ideaLower.includes("养老") || ideaLower.includes("健康")) {
    targetAudience = "银发族";
  } else if (ideaLower.includes("单身") || ideaLower.includes("脱单") || ideaLower.includes("相亲")) {
    targetAudience = "单身";
  } else if (ideaLower.includes("创业") || ideaLower.includes("老板") || ideaLower.includes("企业")) {
    targetAudience = "创业者";
  } else if (ideaLower.includes("职场") || ideaLower.includes("升职") || ideaLower.includes("加薪")) {
    targetAudience = "职场人";
  }
  
  // 推断人性诱因
  for (const [keyword, triggerList] of Object.entries(businessKeywords)) {
    if (ideaLower.includes(keyword)) {
      matchedTriggers.push(...triggerList);
    }
  }
  
  // 特定关键词匹配
  if (ideaLower.includes("便宜") || ideaLower.includes("优惠") || ideaLower.includes("折扣") || ideaLower.includes("省钱")) {
    matchedTriggers.push("贪婪", "损失厌恶");
  }
  if (ideaLower.includes("高端") || ideaLower.includes("限量") || ideaLower.includes("奢侈") || ideaLower.includes("身份")) {
    matchedTriggers.push("虚荣", "稀缺性", "等级序列");
  }
  if (ideaLower.includes("快") || ideaLower.includes("便捷") || ideaLower.includes("一键") || ideaLower.includes("省事")) {
    matchedTriggers.push("懒惰", "效能感");
  }
  if (ideaLower.includes("社交") || ideaLower.includes("交友") || ideaLower.includes("社区") || ideaLower.includes("群")) {
    matchedTriggers.push("社交梳毛", "归属感", "攀比嫉妒");
  }
  if (ideaLower.includes("焦虑") || ideaLower.includes("担心") || ideaLower.includes("害怕")) {
    matchedTriggers.push("生存焦虑", "后果恐惧");
  }
  if (ideaLower.includes("成长") || ideaLower.includes("学习") || ideaLower.includes("提升")) {
    matchedTriggers.push("自我实现", "效能感");
  }
  if (ideaLower.includes("限量") || ideaLower.includes("稀缺") || ideaLower.includes("抢")) {
    matchedTriggers.push("稀缺性", "从众心理");
  }
  if (ideaLower.includes("会员") || ideaLower.includes("积分") || ideaLower.includes("等级")) {
    matchedTriggers.push("沉没成本", "等级序列");
  }
  
  matchedTriggers = [...new Set(matchedTriggers)];
  
  // 获取目标人群画像
  let audience = audienceProfiles[targetAudience];
  if (!audience) {
    audience = { age: "25-45", fears: ["生存焦虑", "后果恐惧"], desires: ["虚荣", "自我实现"], weaknesses: ["从众心理", "即时满足"] };
  }
  
  console.log("\n【1. 目标人群心理弱点分析】");
  console.log(`目标人群: ${targetAudience} (${audience.age}岁)`);
  console.log(`核心恐惧: ${audience.fears.join("、")}`);
  console.log(`核心欲望: ${audience.desires.join("、")}`);
  console.log(`人性弱点: ${audience.weaknesses.join("、")}`);
  
  if (matchedTriggers.length > 0) {
    console.log(`\n当前商业想法匹配的诱因: ${matchedTriggers.join("、")}`);
    const allTriggers = [...new Set([...matchedTriggers, ...audience.fears, ...audience.desires, ...audience.weaknesses])];
    console.log(`推荐利用的组合: ${allTriggers.slice(0, 3).join(" + ")}`);
  }
  
  console.log("\n【2. 获利路径可视化】");
  console.log("┌─────────────────────────────────────────────────────┐");
  console.log("│  🎯 触达用户 → 💡 激发需求 → 💰 引导付费 → 🔄 促成复购 → 📢 自动传播  │");
  console.log("└─────────────────────────────────────────────────────┘");
  console.log("\n路径1: 恐惧驱动型");
  console.log("  唤醒焦虑 → 推出解决方案 → 限时优惠 → 损失厌恶 → 复购");
  console.log("\n路径2: 欲望驱动型");
  console.log("  展示美好结果 → 激发欲望 → 社交证明 → 虚荣满足 → 传播");
  console.log("\n路径3: 弱点驱动型");
  console.log("  降低行动门槛 → 即时反馈 → 沉没成本 → 习惯养成");
  
  console.log("\n【3. 战略建议与实施方案】");
  console.log("\n📌 核心战略建议:");
  console.log(`   1. 聚焦${targetAudience}的${audience.fears[0]}和${audience.desires[0]}`);
  console.log("   2. 首单采用「损失厌恶+贪婪」组合");
  console.log("   3. 复购采用「沉没成本+归属感」组合");
  
  console.log("\n📌 实施方案:");
  console.log("   【引流期】");
  console.log("   - 制造稀缺: 限时限量 + 社交证明");
  console.log("   - 内容营销: 对标焦虑 + 解决方案");
  console.log("   ");
  console.log("   【转化期】");
  console.log("   - 首单优惠: 锚定效应 + 损失厌恶");
  console.log("   - 社交裂变: 互惠心理 + 攀比嫉妒");
  console.log("   ");
  console.log("   【复购期】");
  console.log("   - 会员体系: 沉没成本 + 等级序列");
  console.log("   - 社群运营: 归属感 + 社交梳毛");
  
  console.log("\n📌 关键指标:");
  console.log("   - 获客成本 < 30元");
  console.log("   - 首单转化率 > 15%");
  console.log("   - 30天复购率 > 25%");
  console.log("   - 用户推荐率 > 0.3");
  
  process.exit(0);
}

// 帮助
console.log(`
=== 人性商战手册 🎯 ===

用法:
  analyze <商业模式>    分析商业模式涉及的人性诱因
  fusion <诱因1> <诱因2>...  人性组合实验室
  advisor <商业想法>   AI商战顾问（深度解构）

示例:
  node analyze.mjs --analyze 拼多多
  node analyze.mjs --fusion 贪婪 沉没成本 互惠心理
  node analyze.mjs --advisor 一个帮助大学生找兼职的APP
  node analyze.mjs -a 做便宜又好用的护肤品牌
`);
