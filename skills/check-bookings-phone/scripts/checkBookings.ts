import { agentFromAdbDevice } from "@midscene/android";

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

const CTRIP_MAIN_ACTIVITY = "ctrip.android.view/ctrip.business.splash.CtripSplashActivity";

// 解析命令行参数：--from 2026-05-01 --to 2026-05-05
function parseArgs() {
  const args = process.argv.slice(2);
  let fromStr = "2026-05-01";
  let toStr = "2026-05-05";

  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--from" && args[i + 1]) fromStr = args[++i];
    else if (args[i] === "--to" && args[i + 1]) toStr = args[++i];
  }

  const from = parseDate(fromStr);
  const to = parseDate(toStr);
  if (!from || !to) {
    console.error("日期格式错误，请使用 YYYY-MM-DD，例如: --from 2026-05-01 --to 2026-05-05");
    process.exit(1);
  }

  // 生成所有日期列表
  const dates: { year: number; month: number; day: number }[] = [];
  const cur = new Date(from.year, from.month - 1, from.day);
  const end = new Date(to.year, to.month - 1, to.day);
  while (cur <= end) {
    dates.push({ year: cur.getFullYear(), month: cur.getMonth() + 1, day: cur.getDate() });
    cur.setDate(cur.getDate() + 1);
  }

  // 按月份分组
  const monthGroups = new Map<string, { year: number; month: number; days: number[] }>();
  for (const d of dates) {
    const key = `${d.year}年${d.month}月`;
    if (!monthGroups.has(key)) {
      monthGroups.set(key, { year: d.year, month: d.month, days: [] });
    }
    monthGroups.get(key)!.days.push(d.day);
  }

  // 中文描述，如 "2026年5月1日-5日" 或 "2026年4月28日-2026年5月2日"
  const fromLabel = `${from.year}年${from.month}月${from.day}日`;
  const toLabel = from.year === to.year && from.month === to.month
    ? `${to.day}日`
    : `${to.year}年${to.month}月${to.day}日`;
  const rangeLabel = `${fromLabel}-${toLabel}`;

  return { dates, monthGroups, rangeLabel };
}

function parseDate(s: string) {
  const m = s.match(/^(\d{4})-(\d{1,2})-(\d{1,2})$/);
  if (!m) return null;
  return { year: parseInt(m[1]), month: parseInt(m[2]), day: parseInt(m[3]) };
}

const { dates: TARGET_DATES, monthGroups: MONTH_GROUPS, rangeLabel: RANGE_LABEL } = parseArgs();
console.log(`目标日期: ${RANGE_LABEL}（共${TARGET_DATES.length}天，跨${MONTH_GROUPS.size}个月）`);

interface DateStatus {
  date: string;
  status: string;
}

interface OrderResult {
  orderIndex: number;
  orderName: string;
  dateStatuses: DateStatus[];
}

interface TimingEntry {
  screen: string;
  durationMs: number;
}

const timings: TimingEntry[] = [];

function startTimer(): () => number {
  const start = Date.now();
  return () => Date.now() - start;
}

function logScreen(screen: string, durationMs: number) {
  timings.push({ screen, durationMs });
  console.log(`  [计时] ${screen}: ${(durationMs / 1000).toFixed(1)}s`);
}

type Agent = Awaited<ReturnType<typeof agentFromAdbDevice>>;

async function main() {
  const totalTimer = startTimer();

  const agent = await agentFromAdbDevice(undefined, {
    aiActionContext:
      "当前操作携程旅行app。如果出现权限弹窗、用户协议等弹窗，点击同意/允许。如果出现登录弹窗，关闭它。界面语言为中文。",
  });
  console.log("设备已连接");

  try {
    // 第1屏：导航到"我的"页面
    let timer = startTimer();
    await navigateToMyPage(agent);
    await sleep(500);
    logScreen("第1屏 → 我的页面", timer());

    // 第1屏 → 第2屏：点击"全部订单"
    timer = startTimer();
    console.log("点击「全部订单」...");
    await agent.aiTap("全部订单");
    await sleep(500);
    logScreen("第1屏 → 第2屏（全部订单）", timer());

    // 第2屏 → 第3屏：点击"未使用 预售订单"
    timer = startTimer();
    console.log("点击「未使用 预售订单」...");
    await agent.aiTap("未使用 预售订单");
    await sleep(500);
    await agent.aiWaitFor('页面顶部显示"未使用 预售订单"相关文字', {
      timeoutMs: 3000,
    });
    logScreen("第2屏 → 第3屏（未使用预售订单列表）", timer());
    console.log("已进入未使用预售订单列表");

    // 第3屏：查询订单总数（只查数量，比查名称快）
    timer = startTimer();
    console.log("查询订单数量...");
    const totalOrders = await agent.aiQuery<number>(
      'number, 当前页面有多少个"在线预约"按钮？返回数量'
    );
    logScreen("第3屏 查询订单数量", timer());
    console.log(`共发现 ${totalOrders || 0} 个订单`);

    if (!totalOrders || totalOrders === 0) {
      console.log("未找到任何订单");
    }

    const results: OrderResult[] = [];

    for (let orderIndex = 0; orderIndex < (totalOrders || 0); orderIndex++) {
      console.log(`\n--- 处理第 ${orderIndex + 1}/${totalOrders} 个订单 ---`);

      // 第3屏 → 第4屏：点击"在线预约"
      timer = startTimer();
      if (orderIndex === 0) {
        await agent.aiTap("在线预约");
      } else {
        await agent.aiAction(`点击页面上第${orderIndex + 1}个"在线预约"按钮`);
      }
      await sleep(500);
      logScreen(`订单${orderIndex + 1} 第3屏 → 第4屏（在线预约）`, timer());

      // 第4屏：获取订单名称并点击"立即预约"
      let orderName = `订单${orderIndex + 1}`;
      try {
        const name = await agent.aiQuery<string>('string, 当前页面的酒店名称或订单名称');
        if (name) orderName = name;
      } catch {}

      timer = startTimer();
      console.log(`订单名称: ${orderName}`);
      console.log("点击「立即预约」...");
      await agent.aiTap("立即预约");
      await sleep(500);
      logScreen(`订单${orderIndex + 1} 第4屏 → 第5屏（立即预约）`, timer());

      // 第5屏：按月份滚动并提取日期状态
      const allDateStatuses: DateStatus[] = [];
      for (const [monthKey, group] of MONTH_GROUPS) {
        timer = startTimer();
        console.log(`滚动到${monthKey}...`);
        await scrollToTargetMonth(agent, monthKey);
        await sleep(500);
        logScreen(`订单${orderIndex + 1} 第5屏 滚动到${monthKey}`, timer());

        timer = startTimer();
        const daysStr = group.days.join("、");
        console.log(`提取${monthKey}${daysStr}日的日期状态...`);
        const statuses = await agent.aiQuery<DateStatus[]>(
          `{date: string, status: string}[], 在日历中找到${monthKey}${group.days[0]}日到${monthKey}${group.days[group.days.length - 1]}日，返回每个日期数字及其下方的文字。date格式如"${group.month}月${group.days[0]}日"，status是日期数字下面的小字，例如"补200"、"补100"、"可约"、"约满"等。如果日期下面没有文字则status为"无"`
        );
        logScreen(`订单${orderIndex + 1} 第5屏 提取${monthKey}日期状态`, timer());
        if (Array.isArray(statuses)) allDateStatuses.push(...statuses);
      }
      const dateStatuses = allDateStatuses;

      const result: OrderResult = {
        orderIndex: orderIndex + 1,
        orderName,
        dateStatuses: dateStatuses || [],
      };
      results.push(result);

      console.log(`订单: ${orderName}`);
      for (const ds of result.dateStatuses) {
        console.log(`  ${ds.date}: ${ds.status}`);
      }

      // 第5屏 → 第4屏：关闭日期选择器
      timer = startTimer();
      console.log("关闭日期选择器...");
      try {
        await agent.aiTap("日期选择弹窗左上角的关闭按钮x");
        await sleep(500);
      } catch {
        await agent.back();
        await sleep(500);
      }
      logScreen(`订单${orderIndex + 1} 第5屏 → 第4屏（关闭日期）`, timer());

      // 第4屏 → 第3屏：返回订单列表
      timer = startTimer();
      console.log("返回订单列表...");
      await agent.back();
      await sleep(500);

      try {
        await agent.aiWaitFor('页面顶部显示"未使用 预售订单"相关文字', {
          timeoutMs: 3000,
        });
      } catch {
        console.warn("未检测到订单列表页，尝试重新进入...");
        await agent.aiTap("未使用 预售订单");
        await sleep(500);
      }
      logScreen(`订单${orderIndex + 1} 第4屏 → 第3屏（返回列表）`, timer());
    }

    // 打印汇总结果
    console.log("\n========== 汇总结果 ==========");
    for (const r of results) {
      console.log(`\n订单 ${r.orderIndex}: ${r.orderName}`);
      for (const ds of r.dateStatuses) {
        console.log(`  ${ds.date}: ${ds.status}`);
      }
    }
    console.log("\n==============================");

    // 打印计时汇总
    const totalMs = totalTimer();
    console.log("\n========== 耗时统计 ==========");
    for (const t of timings) {
      console.log(`  ${t.screen}: ${(t.durationMs / 1000).toFixed(1)}s`);
    }
    console.log(`\n  总耗时: ${(totalMs / 1000).toFixed(1)}s`);
    console.log("==============================");
  } catch (error) {
    console.error("执行出错:", error);
  }
}

async function navigateToMyPage(agent: Agent) {
  try {
    await agent.aiWaitFor('页面底部有"我的"tab且处于选中状态，或者页面显示了"全部订单"入口', {
      timeoutMs: 3000,
    });
    console.log("已在「我的」页面");
    return;
  } catch {
    // 不在"我的"页面
  }

  console.log("启动携程旅行app...");
  await agent.launch(CTRIP_MAIN_ACTIVITY);
  await sleep(3000);

  console.log("点击底部「我的」tab...");
  await agent.aiTap("我的");
  await sleep(500);
}

async function scrollToTargetMonth(agent: Agent, targetMonth: string) {
  const maxScrollAttempts = 15;
  const swipeCmd = "input swipe 540 1800 540 1200 300";

  for (let i = 0; i < maxScrollAttempts; i++) {
    try {
      await agent.aiWaitFor(`日历上可以看到"${targetMonth}"`, {
        timeoutMs: 3000,
      });
      console.log(`已找到 ${targetMonth}`);
      return;
    } catch {
      console.log(`  未找到 ${targetMonth}，滑动第 ${i + 1} 次...`);
      await agent.runAdbShell(swipeCmd);
      await sleep(500);
    }
  }
  console.warn(`警告: 滚动${maxScrollAttempts}次后仍未找到 ${targetMonth}`);
}

main().then(() => process.exit(0)).catch(() => process.exit(1));
