module.exports = {
  async onCommand(ctx) {
    const memory = ctx.memory
    const userInput = ctx.input.trim()
    const step = await memory.get("et.step") || 0

    // Step 0 → Start onboarding
    if (step === 0) {
      await memory.set("et.step", 1)
      return `🇺🇸 American English Tutor | Onboarding (1/6)
请选择你的当前英语水平（CEFR）：
A2 / B1 / B2 / C1`
    }

    // Step 1 → Save level
    if (step === 1) {
      await memory.set("et.level", userInput)
      await memory.set("et.step", 2)
      return `🇺🇸 Onboarding (2/6)
请选择兴趣领域：
Workplace / Daily / Tech / Neuroscience / General Oral`
    }
    // Step 2 → Save interests
    if (step === 2) {
      await memory.set("et.interests", userInput)
      await memory.set("et.step", 3)
      return `🇺🇸 Onboarding (3/6)
请选择教学风格：
Professional / Casual / Humorous / Rigorous`
    }
export default {
  async run(ctx) {
    const memory = ctx.memory;
    const userInput = (ctx.input || "").trim();
    const step = (await memory.get("et.step")) || 0;

    // Step 0 → Start onboarding
    if (step === 0) {
      await memory.set("et.step", 1);
      return {
        content: `🇺🇸 American English Tutor | Onboarding (1/6)
请选择你的当前英语水平（CEFR）：
A2 / B1 / B2 / C1`
      };
    }

    // Step 1 → Save level
    if (step === 1) {
      await memory.set("et.level", userInput);
      await memory.set("et.step", 2);
      return {
        content: `🇺🇸 Onboarding (2/6)
请选择兴趣领域：
Workplace / Daily / Tech / Neuroscience / General Oral`
      };
    }

    // Step 2
    if (step === 2) {
      await memory.set("et.interests", userInput);
      await memory.set("et.step", 3);
      return {
        content: `🇺🇸 Onboarding (3/6)
请选择教学风格：
Professional / Casual / Humorous / Rigorous`
      };
    }

    // Step 3
    if (step === 3) {
      await memory.set("et.style", userInput);
      await memory.set("et.step", 4);
      return {
        content: `🇺🇸 Onboarding (4/6)
请选择口语/写作比例：
例如 80/20 或 50/50`
      };
    }

    // Step 4
    if (step === 4) {
      await memory.set("et.ratio", userInput);
      await memory.set("et.step", 5);
      return {
        content: `🇺🇸 Onboarding (5/6)
请输入推送时间（如 06:45 / 22:45），或输入 默认`
      };
    }

    // Step 5
    if (step === 5) {
      await memory.set("et.schedule", userInput);
      await memory.set("et.step", 6);
      return {
        content: `🇺🇸 Onboarding Complete ✅
请输入 “开始” 激活系统。`
      };
    }

    // Activated
    if (step === 6 && userInput.includes("开始")) {
      await memory.set("et.active", true);

      const level = await memory.get("et.level");
      const interests = await memory.get("et.interests");
      const style = await memory.get("et.style");

      return {
        content: `🦞 今日知识点 | Vibe Check

用户等级: ${level}
兴趣: ${interests}
风格: ${style}

✨ Vibe check!
意思：气氛测试

例句：
A: Vibe check!
B: Just catching a vibe.

系统已激活 🎉`
      };
    }

    return {
      content: "系统已启动。输入 '开始英语学习' 重新配置。"
    };
  }
};
