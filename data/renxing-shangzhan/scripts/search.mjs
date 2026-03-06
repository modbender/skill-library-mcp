#!/usr/bin/env node

const triggers = {
  DESIRE: {
    name: "欲望",
    triggers: ["贪婪", "虚荣", "色欲", "权力欲", "好奇心", "自由欲", "效能感"]
  },
  FEAR: {
    name: "恐惧",
    triggers: ["生存焦虑", "损失厌恶", "社交孤立", "后果恐惧", "贫穷焦虑"]
  },
  BIOLOGICAL: {
    name: "生物性",
    triggers: ["领地意识", "部落性", "狩猎本能", "等级序列", "社交梳毛", "采集本能", "生物节律"]
  },
  MORAL: {
    name: "道德/利他",
    triggers: ["道德高地", "公平本能", "感恩亏欠", "牺牲感"]
  },
  EXISTENTIAL: {
    name: "存在/意义",
    triggers: ["意义追寻", "传承留名", "自我实现", "超越感"]
  },
  AESTHETIC: {
    name: "美学/秩序",
    triggers: ["秩序感", "极致美学", "对称平衡", "叙事美学"]
  },
  SOCIAL: {
    name: "社交",
    triggers: ["互惠心理", "攀比嫉妒", "归属感", "获得认同", "八卦差值"]
  },
  COGNITIVE: {
    name: "认知",
    triggers: ["认知省力", "锚定效应", "权威崇拜", "证实偏差", "稀缺性"]
  },
  WEAKNESS: {
    name: "弱点",
    triggers: ["懒惰", "沉没成本", "即时满足", "晕轮效应", "从众心理", "盲目乐观"]
  }
};

const args = process.argv.slice(2);

if (args.length === 0) {
  console.log("=== 人性商战手册 ===\n");
  console.log("用法: search.js <关键词>");
  console.log("用法: search.js --list");
  console.log("用法: search.js --category <分类>");
  console.log("\n分类: DESIRE, FEAR, BIOLOGICAL, MORAL, EXISTENTIAL, AESTHETIC, SOCIAL, COGNITIVE, WEAKNESS");
  process.exit(0);
}

if (args[0] === "--list") {
  console.log("=== 人性诱因完整列表 ===\n");
  for (const [cat, info] of Object.entries(triggers)) {
    console.log(`【${info.name} (${cat})】`);
    console.log("  " + info.triggers.join("、"));
    console.log("");
  }
  process.exit(0);
}

if (args[0] === "--category" && args[1]) {
  const cat = args[1].toUpperCase();
  if (triggers[cat]) {
    console.log(`【${triggers[cat].name} (${cat})】`);
    console.log(triggers[cat].triggers.join("\n"));
  } else {
    console.log("未知分类，可用: " + Object.keys(triggers).join(", "));
  }
  process.exit(0);
}

const keyword = args.join(" ").toLowerCase();
console.log(`搜索: "${keyword}"\n`);

for (const [cat, info] of Object.entries(triggers)) {
  const matched = info.triggers.filter(t => t.toLowerCase().includes(keyword));
  if (matched.length > 0) {
    console.log(`【${info.name} (${cat})】`);
    console.log("  " + matched.join("、"));
    console.log("");
  }
}
