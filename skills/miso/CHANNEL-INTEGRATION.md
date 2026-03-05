# CHANNEL-INTEGRATION.md
# Channel Auto-Posting Specification

## Overview

Auto-post mission start/complete notifications to @MIYABI_CHANNEL (chatId: -1003700344593).

- **Independent from DM Mission Control**: Separate posting logic for channel
- **Noise reduction**: Only start and complete notifications

---

## 1. Posting Triggers

| Event | Post | Content |
|-------|------|---------|
| Mission start | ✅ | 🚀 Start notification |
| Mission complete | ✅ | ✅ Completion report (Key Insights only) |
| Error | ❌ | Do not post |
| In progress | ❌ | Do not post |

---

## 2. Post Templates (Final)

### Mission Start Notification

```
🚀 𝗠𝗜𝗦𝗦𝗜𝗢𝗡 𝗦𝗧𝗔𝗥𝗧𝗘𝗗
——————————————————
📋 {mission_description}
🧩 {agent_count} agents deployed
——————————————————
🌸 ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴍɪʏᴀʙɪ
```

### Mission Complete Report

```
✅ 𝗠𝗜𝗦𝗦𝗜𝗢𝗡 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘
——————————————————
📋 {mission_description}
⏱ {total_time} ∣ 🧩 {agent_count} agents

↳ 💡 𝗞𝗘𝗬 𝗜𝗡𝗦𝗜𝗚𝗛𝗧𝗦
——————————————————
1. {insight_1}
2. {insight_2}
3. {insight_3}
——————————————————
🌸 ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴍɪʏᴀʙɪ
```

**Variable Definitions:**

| Variable | Description | Example |
|----------|-------------|---------|
| `{mission_description}` | Brief mission description | "Weekly report generation" |
| `{agent_count}` | Number of deployed agents | "3" |
| `{total_time}` | Total elapsed time | "2m 34s" |
| `{insight_1..3}` | Key Insights (max 3) | "Achieved 20% cost reduction" |

---

## 3. Privacy Rules

| Item | Channel Output |
|------|----------------|
| 💰 Cost information | ❌ Never show |
| Agent names | ✅ OK to show |
| Error details | ❌ Never show |
| Approval gates | ❌ DM only |

---

## 4. Implementation

### Posting Function Calls

```typescript
// Start notification
await message({
  action: "send",
  channel: "telegram",
  target: "-1003700344593",
  message: formatMissionStart({
    description: mission.description,
    agentCount: agents.length,
  }),
});

// Completion report
await message({
  action: "send",
  channel: "telegram",
  target: "-1003700344593",
  message: formatMissionComplete({
    description: mission.description,
    agentCount: agents.length,
    totalTime: formatDuration(mission.endTime - mission.startTime),
    insights: extractKeyInsights(mission.result).slice(0, 3),
  }),
});
```

### Key Insights Extraction (Helper)

```typescript
function extractKeyInsights(result: MissionResult): string[] {
  // Extract important points from deliverables
  // - Major achievements
  // - Quantitative improvements/reductions
  // - Technical novelty
  // Limited to max 3 items
}
```

---

## 5. Implementation Checklist

- [ ] Add channel post to mission start hook
- [ ] Add channel post to mission complete hook
- [ ] Implement Key Insights extraction function
- [ ] Apply privacy rules (no cost display)
- [ ] Error handling (notify DM if channel post fails)
- [ ] Test: Verify actual post to @MIYABI_CHANNEL

---

## 6. Appendix: Target Channel Info

- **Channel name:** @MIYABI_CHANNEL
- **chatId:** -1003700344593
- **Purpose:** Team-facing notification channel
- **Policy:** Noise reduction priority
