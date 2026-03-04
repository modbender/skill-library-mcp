export function buildQuestionnaire() {
  return {
    questions: [
      {
        id: "horizon",
        prompt: "您的预期持有周期？",
        options: [
          { id: "short", label: "短期（<1个月）" },
          { id: "mid", label: "中期（1-6个月）" },
          { id: "long", label: "长期（>6个月）" },
        ],
      },
      {
        id: "risk",
        prompt: "您能接受的风险水平？",
        options: [
          { id: "low", label: "低风险（回撤敏感）" },
          { id: "mid", label: "中等风险（均衡）" },
          { id: "high", label: "高风险（追求弹性）" },
        ],
      },
      {
        id: "style",
        prompt: "您偏好的投资风格？",
        options: [
          { id: "value", label: "价值防守" },
          { id: "balanced", label: "均衡配置" },
          { id: "growth", label: "成长进攻" },
          { id: "trading", label: "短线交易" },
        ],
      },
      {
        id: "actionable",
        prompt: "是否需要可执行买卖规则？",
        options: [
          { id: "false", label: "仅研究观点" },
          { id: "true", label: "给出可执行建议（含风控）" },
        ],
      },
    ],
    defaultStyle: "balanced",
    instructions: "请回答上述偏好后重试，或直接传入 --horizon/--risk/--style/--actionable 参数。",
  };
}

export function parsePreferences(args = {}) {
  const hasAny =
    args.horizon != null ||
    args.risk != null ||
    args.style != null ||
    typeof args.actionable === "boolean";
  return {
    hasAny,
    horizon: args.horizon || null,
    risk: args.risk || null,
    style: args.style || null,
    actionable: Boolean(args.actionable),
  };
}

