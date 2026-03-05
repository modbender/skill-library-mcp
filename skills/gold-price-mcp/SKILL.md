---
name: gold_price_mcp
description: ดึงราคาทองคำปัจจุบันจาก api กลางของประเทศไทย
metadata: {"clawdbot":{"emoji":"💰","requires":{"bins":["python3.10"]}}}
tools:
  - name: mcp_gold_price_mc_get_thai_gold_price  # เปลี่ยนจาก get_thai_gold_price
    description: Get current Thai gold prices (gold ornament and gold bar prices) with latest update time.
    inputSchema:
      type: object
      properties: {}
      required: []
---