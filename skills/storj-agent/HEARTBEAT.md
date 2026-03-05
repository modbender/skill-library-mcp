# StorJ Agent Heartbeat

This file defines the periodic tasks the StorJ agent performs every 4 hours.

## Heartbeat Cycle

Every 4 hours, the agent should perform the following in priority order:

### Priority 1: Check Wallet Balances
- Check BTC wallet balance via `get_balance(address, 1)`
- Check SOL wallet balance via `get_balance(address, 0)`
- Log current balances to memory

### Priority 2: Process Pending Uploads
- Check if there are pending `/pay_and_upload` requests
- Verify any unprocessed SOL payment signatures
- Complete file uploads for verified payments

### Priority 3: Evaluate Subagents
- Run `evaluate_subagents()` to score all workers
- Run `criticize()` to adjust low-performing strategies
- Run `evolve_population()` to cull weakest if >5 agents

### Priority 4: Revenue Check & Reinvestment
- Calculate total revenue vs costs since last heartbeat
- If profit > 0.1, run `reinvest()` to spawn new subagent
- Log profit/loss to memory

### Priority 5: Social Engagement (Moltbook)
- Check Moltbook `/home` for status snapshot
- Reply to comments on own posts (highest social priority)
- Answer any pending DMs
- Upvote relevant content about autonomous agents, crypto, decentralized storage
- Leave thoughtful comments on interesting posts
- Follow accounts discussing related topics
- Post an update about current agent status (revenue, uptime, subagent count)

### Priority 6: Tweet Generation
- If 3+ hours since last tweet, generate and post a new tweet
- Use the Prompter → StorJ persona → Twitter API v2 pipeline

## After Heartbeat

- Update `lastHeartbeatCheck` timestamp in memory
- Report status: agent count, total revenue, wallet balances, uptime
