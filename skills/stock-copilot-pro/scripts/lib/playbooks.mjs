function withCommonFields(style, fitFor, actionable) {
  return {
    style,
    fitFor,
    actionable: Boolean(actionable),
    watchlist: ["营收同比", "净利润同比", "经营现金流", "估值分位", "量价趋势", "事件催化兑现度"],
  };
}

export function buildPlaybooks(context, preferences = {}) {
  const { valuationFrame, chaseRisk, scorecard } = context;
  const mos = valuationFrame?.intrinsic?.marginOfSafety;
  const riskLevel = preferences.risk || "mid";

  const valueDefensive = {
    ...withCommonFields("value_defensive", "回撤敏感、偏长期配置", preferences.actionable),
    entryTriggers: [
      `安全边际 ${mos == null ? "待确认" : `${mos.toFixed(1)}%`} 且估值不高于行业中位`,
      "基本面关键指标无明显恶化",
    ],
    positionSizing: riskLevel === "low" ? "首仓 15%，最多 40%" : "首仓 20%，最多 50%",
    exitPlan: {
      takeProfit: "估值显著高估或达到目标收益区间时分批止盈",
      stopLoss: "单笔 -10% 或基本面证伪",
      timeStop: "6-12个月逻辑未兑现则重新评估",
      fundamentalInvalidation: "营收/利润连续恶化且现金流转负",
    },
    riskControls: ["避免满仓单一标的", "财务杠杆高时降低仓位", "事件驱动高波动期谨慎加仓"],
  };

  const balanced = {
    ...withCommonFields("balanced", "中期持有、风险收益均衡", preferences.actionable),
    entryTriggers: ["估值处于合理区间", "趋势确认且非极端追高", `追高风险: ${chaseRisk?.risk || "unknown"}`],
    positionSizing: "首仓 25%-30%，最多 60%",
    exitPlan: {
      takeProfit: "达到目标收益后分批减仓",
      stopLoss: "单笔 -8% 至 -10%",
      timeStop: "3-6个月未达预期则调整",
      fundamentalInvalidation: "核心驱动因子失效",
    },
    riskControls: ["至少分两批建仓", "趋势转弱时先降杠杆", "消息面冲击日降低操作频率"],
  };

  const growthAggressive = {
    ...withCommonFields("growth_aggressive", "波动容忍高、追求超额收益", preferences.actionable),
    entryTriggers: ["增长指标改善", "主题催化明确", "趋势放量上行"],
    positionSizing: riskLevel === "high" ? "首仓 30%，最多 70%" : "首仓 20%，最多 60%",
    exitPlan: {
      takeProfit: "趋势转弱或催化兑现后减仓",
      stopLoss: "动态止损，通常 -7% 至 -9%",
      timeStop: "1-3个月验证增长持续性",
      fundamentalInvalidation: "增长预期明显下修",
    },
    riskControls: ["单一主题仓位上限 30%", "避免高位连续加仓", "高波动期增加止损纪律"],
  };

  const tradingSwing = {
    ...withCommonFields("trading_swing", "短线/事件交易", preferences.actionable),
    entryTriggers: ["事件催化触发", "量价配合", "交易回踩型中等待回踩确认"],
    positionSizing: "单笔 <= 10%，总交易仓位 <= 40%",
    exitPlan: {
      takeProfit: "快进快出，分批止盈",
      stopLoss: "单笔 -5% 至 -7% 严格执行",
      timeStop: "5-20个交易日",
      fundamentalInvalidation: "事件证伪或热度快速衰退",
    },
    riskControls: ["不隔夜重仓赌消息", "事件后首日避免情绪化追高", "连续亏损暂停交易复盘"],
  };

  const all = [valueDefensive, balanced, growthAggressive, tradingSwing];
  const styleMap = {
    value: "value_defensive",
    balanced: "balanced",
    growth: "growth_aggressive",
    trading: "trading_swing",
    value_defensive: "value_defensive",
    growth_aggressive: "growth_aggressive",
  };
  const preferred = styleMap[preferences.style] || "balanced";
  const recommended = all.find((x) => x.style === preferred) || balanced;
  return {
    recommendedStyle: recommended.style,
    recommendedReason: `当前综合评分 ${scorecard?.composite ?? "N/A"}，估值结论 ${valuationFrame?.verdict || "N/A"}，更匹配 ${recommended.style}`,
    playbooks: all,
  };
}

