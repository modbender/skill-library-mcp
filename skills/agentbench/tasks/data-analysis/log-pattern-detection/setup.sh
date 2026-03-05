#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="$1"
cd "$WORKSPACE"

git init -q
git config user.email "bench@agentbench.local"
git config user.name "AgentBench"

# ── topology.yaml ─────────────────────────────────────────────────────────────
cat > topology.yaml << 'TOPOLOGY_EOF'
services:
  service-a:
    name: "API Gateway"
    depends_on: [service-b, service-c]
  service-b:
    name: "Order Processor"
    depends_on: [service-d, service-e]
  service-c:
    name: "Notification Service"
    depends_on: []
  service-d:
    name: "Payment Provider"
    depends_on: []
  service-e:
    name: "Inventory Service"
    depends_on: []
TOPOLOGY_EOF

# ── sla.yaml ──────────────────────────────────────────────────────────────────
cat > sla.yaml << 'SLA_EOF'
response_time_ms:
  service-a: 500
  service-b: 300
  service-c: 200
  service-d: 1000
  service-e: 200
error_rate_threshold: 0.05
SLA_EOF

# ── Log files ─────────────────────────────────────────────────────────────────
mkdir -p logs

# ============================================================================
# service-d.log — Payment Provider (ROOT CAUSE)
# ~120 lines. Database connection pool exhaustion starting at 10:30.
# ============================================================================
cat > logs/service-d.log << 'SERVICE_D_EOF'
[2025-03-15 10:00:12.334] [INFO] [req-d001] Payment check completed (duration_ms=210)
[2025-03-15 10:00:45.112] [INFO] [req-d002] Payment authorization successful for order ORD-8812 (duration_ms=340)
[2025-03-15 10:01:23.891] [INFO] [req-d003] Payment check completed (duration_ms=185)
[2025-03-15 10:02:07.443] [INFO] [req-d004] Refund processed for order ORD-8801 (duration_ms=290)
[2025-03-15 10:03:15.667] [INFO] [req-d005] Payment authorization successful for order ORD-8815 (duration_ms=410)
[2025-03-15 10:04:52.119] [INFO] [req-d006] Payment check completed (duration_ms=198)
[2025-03-15 10:05:33.782] [INFO] [req-d007] Balance inquiry completed (duration_ms=145)
[2025-03-15 10:07:01.445] [INFO] [req-d008] Payment authorization successful for order ORD-8820 (duration_ms=520)
[2025-03-15 10:08:22.901] [INFO] [req-d009] Payment check completed (duration_ms=310)
[2025-03-15 10:09:45.332] [INFO] [req-d010] Payment authorization successful for order ORD-8823 (duration_ms=380)
[2025-03-15 10:11:12.554] [INFO] [req-d011] Refund processed for order ORD-8809 (duration_ms=445)
[2025-03-15 10:12:40.891] [INFO] [req-d012] Payment check completed (duration_ms=260)
[2025-03-15 10:14:05.223] [INFO] [req-d013] Payment authorization successful for order ORD-8830 (duration_ms=390)
[2025-03-15 10:15:33.667] [INFO] [req-d014] Balance inquiry completed (duration_ms=175)
[2025-03-15 10:17:01.119] [INFO] [req-d015] Payment check completed (duration_ms=305)
[2025-03-15 10:18:45.443] [INFO] [req-d016] Payment authorization successful for order ORD-8835 (duration_ms=480)
[2025-03-15 10:20:12.778] [INFO] [req-d017] Payment check completed (duration_ms=225)
[2025-03-15 10:22:01.901] [INFO] [req-d018] Payment authorization successful for order ORD-8840 (duration_ms=560)
[2025-03-15 10:24:15.334] [INFO] [req-d019] Refund processed for order ORD-8828 (duration_ms=340)
[2025-03-15 10:26:30.112] [INFO] [req-d020] Payment check completed (duration_ms=290)
[2025-03-15 10:28:05.556] [INFO] [req-d021] Payment authorization successful for order ORD-8845 (duration_ms=610)
[2025-03-15 10:29:33.891] [INFO] [req-d022] Balance inquiry completed (duration_ms=195)
[2025-03-15 10:30:02.445] [WARN] [req-d023] Database connection pool utilization at 85% (17/20 connections in use)
[2025-03-15 10:30:15.112] [INFO] [req-d023] Payment authorization successful for order ORD-8848 (duration_ms=780)
[2025-03-15 10:30:45.667] [WARN] [req-d024] Slow query detected: payment_transactions lookup took 1200ms
[2025-03-15 10:31:02.334] [WARN] [req-d024] Database connection pool utilization at 90% (18/20 connections in use)
[2025-03-15 10:31:18.891] [INFO] [req-d024] Payment check completed (duration_ms=1350)
[2025-03-15 10:31:45.223] [WARN] [req-d025] Slow query detected: payment_transactions lookup took 1580ms
[2025-03-15 10:32:10.556] [WARN] [req-d025] Database connection pool utilization at 95% (19/20 connections in use)
[2025-03-15 10:32:30.112] [INFO] [req-d025] Payment authorization successful for order ORD-8851 (duration_ms=1820)
[2025-03-15 10:33:01.445] [WARN] [req-d026] Slow query detected: payment_ledger join took 2100ms
[2025-03-15 10:33:22.778] [WARN] [req-d026] Database connection pool fully exhausted (20/20 connections in use), new requests queued
[2025-03-15 10:33:55.901] [INFO] [req-d026] Payment check completed (duration_ms=2450)
[2025-03-15 10:34:20.334] [WARN] [req-d027] Slow query detected: payment_transactions lookup took 2300ms
[2025-03-15 10:34:45.112] [WARN] [req-d027] Waiting for database connection from pool (waited 1200ms)
[2025-03-15 10:35:10.667] [INFO] [req-d027] Payment authorization successful for order ORD-8854 (duration_ms=2780)
[2025-03-15 10:36:02.891] [WARN] [req-d028] Slow query detected: payment_ledger join took 2650ms
[2025-03-15 10:36:40.223] [WARN] [req-d028] Waiting for database connection from pool (waited 2100ms)
[2025-03-15 10:37:05.556] [INFO] [req-d028] Payment check completed (duration_ms=3100)
[2025-03-15 10:38:15.112] [WARN] [req-d029] Slow query detected: payment_transactions lookup took 2900ms
[2025-03-15 10:39:00.445] [WARN] [req-d029] Waiting for database connection from pool (waited 2800ms)
[2025-03-15 10:39:30.778] [INFO] [req-d029] Refund processed for order ORD-8841 (duration_ms=2950)
[2025-03-15 10:40:45.901] [WARN] [req-d030] Slow query detected: payment_ledger join took 3200ms
[2025-03-15 10:41:20.334] [WARN] [req-d030] Waiting for database connection from pool (waited 3100ms)
[2025-03-15 10:42:00.112] [INFO] [req-d030] Payment authorization successful for order ORD-8858 (duration_ms=3400)
[2025-03-15 10:43:15.445] [WARN] [req-d031] Slow query detected: payment_transactions lookup took 3500ms
[2025-03-15 10:44:00.778] [WARN] [req-d031] Waiting for database connection from pool (waited 3600ms)
[2025-03-15 10:44:30.112] [WARN] [req-d031] Query nearing timeout threshold: payment_ledger join at 4200ms
[2025-03-15 10:45:02.334] [ERROR] [req-d031] Connection timeout after 5000ms — unable to acquire database connection
[2025-03-15 10:45:15.667] [ERROR] [req-d032] Connection timeout after 5000ms — unable to acquire database connection
[2025-03-15 10:45:33.112] [INFO] [req-d033] Payment check completed (duration_ms=3800)
[2025-03-15 10:46:01.445] [ERROR] [req-d034] Connection timeout after 5000ms — unable to acquire database connection
[2025-03-15 10:46:25.778] [ERROR] [req-d035] Connection timeout after 5000ms — unable to acquire database connection
[2025-03-15 10:47:10.112] [INFO] [req-d036] Payment authorization successful for order ORD-8862 (duration_ms=4200)
[2025-03-15 10:47:45.445] [ERROR] [req-d037] Connection timeout after 5000ms — unable to acquire database connection
[2025-03-15 10:48:15.778] [ERROR] [req-d038] Connection timeout after 5000ms — unable to acquire database connection
[2025-03-15 10:48:50.112] [ERROR] [req-d039] Connection timeout after 5000ms — unable to acquire database connection
[2025-03-15 10:49:30.445] [INFO] [req-d040] Payment check completed (duration_ms=4500)
[2025-03-15 10:50:05.778] [ERROR] [req-d041] Connection timeout after 5000ms — unable to acquire database connection
[2025-03-15 10:50:40.112] [ERROR] [req-d042] Connection timeout after 5000ms — unable to acquire database connection
[2025-03-15 10:51:20.445] [WARN] [req-d043] Database connection pool fully exhausted, 8 requests queued
[2025-03-15 10:51:55.778] [ERROR] [req-d043] Connection timeout after 5000ms — unable to acquire database connection
[2025-03-15 10:52:30.112] [ERROR] [req-d044] Connection timeout after 5000ms — unable to acquire database connection
[2025-03-15 10:53:15.445] [INFO] [req-d045] Payment authorization successful for order ORD-8870 (duration_ms=4800)
[2025-03-15 10:54:00.778] [ERROR] [req-d046] Connection timeout after 5000ms — unable to acquire database connection
[2025-03-15 10:55:10.112] [ERROR] [req-d047] Connection timeout after 5000ms — unable to acquire database connection
[2025-03-15 10:56:30.445] [ERROR] [req-d048] Connection timeout after 5000ms — unable to acquire database connection
[2025-03-15 10:58:00.778] [ERROR] [req-d049] Connection timeout after 5000ms — unable to acquire database connection
[2025-03-15 10:59:15.112] [ERROR] [req-d050] Connection refused — database server not accepting new connections
[2025-03-15 11:00:30.445] [ERROR] [req-d051] Connection timeout after 5000ms — unable to acquire database connection
[2025-03-15 11:01:15.778] [ERROR] [req-d052] Connection refused — database server not accepting new connections
[2025-03-15 11:02:45.112] [ERROR] [req-d053] Connection timeout after 5000ms — unable to acquire database connection
[2025-03-15 11:03:30.445] [ERROR] [req-d054] Connection refused — database server not accepting new connections
[2025-03-15 11:04:50.778] [ERROR] [req-d055] Connection timeout after 5000ms — unable to acquire database connection
[2025-03-15 11:06:15.112] [ERROR] [req-d056] Connection refused — database server not accepting new connections
[2025-03-15 11:08:00.445] [ERROR] [req-d057] Connection timeout after 5000ms — unable to acquire database connection
[2025-03-15 11:10:30.778] [ERROR] [req-d058] Connection refused — database server not accepting new connections
[2025-03-15 11:13:00.112] [ERROR] [req-d059] Connection timeout after 5000ms — unable to acquire database connection
[2025-03-15 11:16:00.445] [ERROR] [req-d060] Connection refused — database server not accepting new connections
[2025-03-15 11:20:00.778] [WARN] [system] Health check failing — database connectivity lost
[2025-03-15 11:25:00.112] [ERROR] [req-d061] Connection refused — database server not accepting new connections
[2025-03-15 11:30:00.445] [WARN] [system] Health check failing — database connectivity lost
[2025-03-15 11:40:00.778] [ERROR] [req-d062] Connection refused — database server not accepting new connections
[2025-03-15 11:50:00.112] [WARN] [system] Health check failing — database connectivity lost, 0 active connections in pool
SERVICE_D_EOF

# ============================================================================
# service-b.log — Order Processor (CASCADING from service-d)
# ~120 lines. Retry storms start at 10:45, failures by 11:00.
# ============================================================================
cat > logs/service-b.log << 'SERVICE_B_EOF'
[2025-03-15 10:00:05.221] [INFO] [req-b001] Order ORD-8812 received, processing (duration_ms=85)
[2025-03-15 10:00:35.443] [INFO] [req-b001] Called service-d for payment authorization (duration_ms=340)
[2025-03-15 10:00:36.112] [INFO] [req-b001] Called service-e for inventory check (duration_ms=65)
[2025-03-15 10:00:36.334] [INFO] [req-b001] Order ORD-8812 processed successfully (total_duration_ms=130)
[2025-03-15 10:02:01.556] [INFO] [req-b002] Order ORD-8815 received, processing (duration_ms=72)
[2025-03-15 10:02:22.778] [INFO] [req-b002] Called service-d for payment authorization (duration_ms=410)
[2025-03-15 10:02:23.112] [INFO] [req-b002] Called service-e for inventory check (duration_ms=55)
[2025-03-15 10:02:23.334] [INFO] [req-b002] Order ORD-8815 processed successfully (total_duration_ms=115)
[2025-03-15 10:05:10.445] [INFO] [req-b003] Order ORD-8820 received, processing (duration_ms=90)
[2025-03-15 10:05:41.667] [INFO] [req-b003] Called service-d for payment authorization (duration_ms=520)
[2025-03-15 10:05:42.112] [INFO] [req-b003] Called service-e for inventory check (duration_ms=48)
[2025-03-15 10:05:42.334] [INFO] [req-b003] Order ORD-8820 processed successfully (total_duration_ms=125)
[2025-03-15 10:08:15.556] [INFO] [req-b004] Order ORD-8823 received, processing (duration_ms=68)
[2025-03-15 10:08:40.778] [INFO] [req-b004] Called service-d for payment authorization (duration_ms=380)
[2025-03-15 10:08:41.112] [INFO] [req-b004] Called service-e for inventory check (duration_ms=52)
[2025-03-15 10:08:41.334] [INFO] [req-b004] Order ORD-8823 processed successfully (total_duration_ms=108)
[2025-03-15 10:12:30.445] [INFO] [req-b005] Order ORD-8830 received, processing (duration_ms=75)
[2025-03-15 10:12:55.667] [INFO] [req-b005] Called service-d for payment authorization (duration_ms=390)
[2025-03-15 10:12:56.112] [INFO] [req-b005] Called service-e for inventory check (duration_ms=60)
[2025-03-15 10:12:56.334] [INFO] [req-b005] Order ORD-8830 processed successfully (total_duration_ms=122)
[2025-03-15 10:17:45.556] [INFO] [req-b006] Order ORD-8835 received, processing (duration_ms=82)
[2025-03-15 10:18:15.778] [INFO] [req-b006] Called service-d for payment authorization (duration_ms=480)
[2025-03-15 10:18:16.112] [INFO] [req-b006] Called service-e for inventory check (duration_ms=45)
[2025-03-15 10:18:16.334] [INFO] [req-b006] Order ORD-8835 processed successfully (total_duration_ms=118)
[2025-03-15 10:22:00.445] [INFO] [req-b007] Order ORD-8840 received, processing (duration_ms=78)
[2025-03-15 10:22:35.667] [INFO] [req-b007] Called service-d for payment authorization (duration_ms=560)
[2025-03-15 10:22:36.112] [INFO] [req-b007] Called service-e for inventory check (duration_ms=50)
[2025-03-15 10:22:36.334] [INFO] [req-b007] Order ORD-8840 processed successfully (total_duration_ms=135)
[2025-03-15 10:28:00.556] [INFO] [req-b008] Order ORD-8845 received, processing (duration_ms=88)
[2025-03-15 10:28:38.778] [INFO] [req-b008] Called service-d for payment authorization (duration_ms=610)
[2025-03-15 10:28:39.112] [INFO] [req-b008] Called service-e for inventory check (duration_ms=58)
[2025-03-15 10:28:39.334] [INFO] [req-b008] Order ORD-8845 processed successfully (total_duration_ms=145)
[2025-03-15 10:32:15.445] [INFO] [req-b009] Order ORD-8848 received, processing (duration_ms=95)
[2025-03-15 10:33:10.667] [INFO] [req-b009] Called service-d for payment authorization (duration_ms=1820)
[2025-03-15 10:33:11.112] [INFO] [req-b009] Called service-e for inventory check (duration_ms=55)
[2025-03-15 10:33:11.445] [WARN] [req-b009] Order ORD-8848 processing slow (total_duration_ms=255), service-d response degraded
[2025-03-15 10:37:00.556] [INFO] [req-b010] Order ORD-8854 received, processing (duration_ms=80)
[2025-03-15 10:39:50.778] [INFO] [req-b010] Called service-d for payment authorization (duration_ms=2780)
[2025-03-15 10:39:51.112] [INFO] [req-b010] Called service-e for inventory check (duration_ms=48)
[2025-03-15 10:39:51.445] [WARN] [req-b010] Order ORD-8854 processing slow (total_duration_ms=290), service-d response degraded
[2025-03-15 10:42:00.556] [INFO] [req-b011] Order ORD-8858 received, processing (duration_ms=72)
[2025-03-15 10:45:25.778] [INFO] [req-b011] Called service-d for payment authorization (duration_ms=3400)
[2025-03-15 10:45:26.112] [INFO] [req-b011] Called service-e for inventory check (duration_ms=52)
[2025-03-15 10:45:26.445] [WARN] [req-b011] Order ORD-8858 processing extremely slow (total_duration_ms=385), service-d latency critical
[2025-03-15 10:45:40.556] [INFO] [req-b012] Order ORD-8860 received, processing (duration_ms=68)
[2025-03-15 10:45:50.778] [WARN] [req-b012] service-d call timed out after 5000ms, retrying (attempt 1/3)
[2025-03-15 10:46:05.112] [WARN] [req-b012] Retrying request to service-d (attempt 2/3)
[2025-03-15 10:46:20.445] [WARN] [req-b012] Retrying request to service-d (attempt 3/3)
[2025-03-15 10:46:35.778] [ERROR] [req-b012] service-d call failed after 3 retries — payment authorization unavailable
[2025-03-15 10:46:36.112] [ERROR] [req-b012] Order ORD-8860 failed: payment service unavailable (total_duration_ms=5568)
[2025-03-15 10:47:00.334] [INFO] [req-b013] Order ORD-8862 received, processing (duration_ms=75)
[2025-03-15 10:47:10.556] [WARN] [req-b013] service-d call timed out after 5000ms, retrying (attempt 1/3)
[2025-03-15 10:47:25.778] [WARN] [req-b013] Retrying request to service-d (attempt 2/3)
[2025-03-15 10:47:40.112] [INFO] [req-b013] Called service-d for payment authorization (duration_ms=4200)
[2025-03-15 10:47:40.445] [INFO] [req-b013] Called service-e for inventory check (duration_ms=55)
[2025-03-15 10:47:40.778] [WARN] [req-b013] Order ORD-8862 completed after retry (total_duration_ms=4075)
[2025-03-15 10:48:05.112] [INFO] [req-b014] Order ORD-8864 received, processing (duration_ms=82)
[2025-03-15 10:48:15.334] [WARN] [req-b014] service-d call timed out after 5000ms, retrying (attempt 1/3)
[2025-03-15 10:48:30.556] [WARN] [req-b014] Retrying request to service-d (attempt 2/3)
[2025-03-15 10:48:45.778] [WARN] [req-b014] Retrying request to service-d (attempt 3/3)
[2025-03-15 10:49:00.112] [ERROR] [req-b014] service-d call failed after 3 retries — payment authorization unavailable
[2025-03-15 10:49:00.445] [ERROR] [req-b014] Order ORD-8864 failed: payment service unavailable (total_duration_ms=5518)
[2025-03-15 10:49:30.667] [INFO] [req-b015] Order ORD-8866 received, processing (duration_ms=70)
[2025-03-15 10:49:40.891] [WARN] [req-b015] service-d call timed out after 5000ms, retrying (attempt 1/3)
[2025-03-15 10:49:55.112] [WARN] [req-b015] Retrying request to service-d (attempt 2/3)
[2025-03-15 10:50:10.334] [WARN] [req-b015] Retrying request to service-d (attempt 3/3)
[2025-03-15 10:50:25.556] [ERROR] [req-b015] service-d call failed after 3 retries — payment authorization unavailable
[2025-03-15 10:50:25.778] [ERROR] [req-b015] Order ORD-8866 failed: payment service unavailable (total_duration_ms=5508)
[2025-03-15 10:51:00.112] [INFO] [req-b016] Order ORD-8868 received, processing (duration_ms=65)
[2025-03-15 10:51:10.334] [WARN] [req-b016] service-d call timed out after 5000ms, retrying (attempt 1/3)
[2025-03-15 10:51:25.556] [WARN] [req-b016] Retrying request to service-d (attempt 2/3)
[2025-03-15 10:51:40.778] [WARN] [req-b016] Retrying request to service-d (attempt 3/3)
[2025-03-15 10:51:55.112] [ERROR] [req-b016] service-d call failed after 3 retries — payment authorization unavailable
[2025-03-15 10:51:55.334] [ERROR] [req-b016] Order ORD-8868 failed: payment service unavailable (total_duration_ms=5535)
[2025-03-15 10:52:30.556] [WARN] [system] Error rate for service-d calls at 60% over last 5 minutes
[2025-03-15 10:53:00.778] [INFO] [req-b017] Order ORD-8870 received, processing (duration_ms=78)
[2025-03-15 10:53:10.112] [WARN] [req-b017] service-d call timed out after 5000ms, retrying (attempt 1/3)
[2025-03-15 10:53:25.334] [WARN] [req-b017] Retrying request to service-d (attempt 2/3)
[2025-03-15 10:53:40.556] [INFO] [req-b017] Called service-d for payment authorization (duration_ms=4800)
[2025-03-15 10:53:40.778] [INFO] [req-b017] Called service-e for inventory check (duration_ms=50)
[2025-03-15 10:53:41.112] [WARN] [req-b017] Order ORD-8870 completed after retry (total_duration_ms=4162)
[2025-03-15 10:55:00.334] [INFO] [req-b018] Order ORD-8873 received, processing (duration_ms=70)
[2025-03-15 10:55:10.556] [WARN] [req-b018] service-d call timed out after 5000ms, retrying (attempt 1/3)
[2025-03-15 10:55:25.778] [WARN] [req-b018] Retrying request to service-d (attempt 2/3)
[2025-03-15 10:55:40.112] [WARN] [req-b018] Retrying request to service-d (attempt 3/3)
[2025-03-15 10:55:55.334] [ERROR] [req-b018] service-d call failed after 3 retries — payment authorization unavailable
[2025-03-15 10:55:55.556] [ERROR] [req-b018] Order ORD-8873 failed: payment service unavailable (total_duration_ms=5555)
[2025-03-15 10:57:00.778] [INFO] [req-b019] Order ORD-8876 received, processing (duration_ms=80)
[2025-03-15 10:57:10.112] [WARN] [req-b019] service-d call timed out after 5000ms, retrying (attempt 1/3)
[2025-03-15 10:57:25.334] [WARN] [req-b019] Retrying request to service-d (attempt 2/3)
[2025-03-15 10:57:40.556] [WARN] [req-b019] Retrying request to service-d (attempt 3/3)
[2025-03-15 10:57:55.778] [ERROR] [req-b019] service-d call failed after 3 retries — payment authorization unavailable
[2025-03-15 10:57:56.112] [ERROR] [req-b019] Order ORD-8876 failed: payment service unavailable (total_duration_ms=5612)
[2025-03-15 10:59:00.334] [WARN] [system] Error rate for service-d calls at 75% over last 5 minutes
[2025-03-15 11:00:10.556] [INFO] [req-b020] Order ORD-8880 received, processing (duration_ms=72)
[2025-03-15 11:00:20.778] [WARN] [req-b020] service-d call timed out after 5000ms, retrying (attempt 1/3)
[2025-03-15 11:00:35.112] [WARN] [req-b020] Retrying request to service-d (attempt 2/3)
[2025-03-15 11:00:50.334] [WARN] [req-b020] Retrying request to service-d (attempt 3/3)
[2025-03-15 11:01:05.556] [ERROR] [req-b020] service-d call failed after 3 retries — connection refused by service-d
[2025-03-15 11:01:05.778] [ERROR] [req-b020] Order ORD-8880 failed: payment service unavailable (total_duration_ms=5506)
[2025-03-15 11:03:00.112] [INFO] [req-b021] Order ORD-8883 received, processing (duration_ms=68)
[2025-03-15 11:03:10.334] [WARN] [req-b021] service-d call timed out after 5000ms, retrying (attempt 1/3)
[2025-03-15 11:03:25.556] [WARN] [req-b021] Retrying request to service-d (attempt 2/3)
[2025-03-15 11:03:40.778] [WARN] [req-b021] Retrying request to service-d (attempt 3/3)
[2025-03-15 11:03:55.112] [ERROR] [req-b021] service-d call failed after 3 retries — connection refused by service-d
[2025-03-15 11:03:55.334] [ERROR] [req-b021] Order ORD-8883 failed: payment service unavailable (total_duration_ms=5532)
[2025-03-15 11:06:00.556] [INFO] [req-b022] Order ORD-8886 received, processing (duration_ms=75)
[2025-03-15 11:06:10.778] [WARN] [req-b022] service-d call failed immediately — connection refused by service-d
[2025-03-15 11:06:20.112] [WARN] [req-b022] Retrying request to service-d (attempt 2/3)
[2025-03-15 11:06:30.334] [WARN] [req-b022] Retrying request to service-d (attempt 3/3)
[2025-03-15 11:06:40.556] [ERROR] [req-b022] service-d call failed after 3 retries — connection refused by service-d
[2025-03-15 11:06:40.778] [ERROR] [req-b022] Order ORD-8886 failed: payment service unavailable (total_duration_ms=4078)
[2025-03-15 11:10:00.112] [WARN] [system] Error rate for service-d calls at 90% over last 10 minutes — all orders requiring payment are failing
[2025-03-15 11:10:30.334] [INFO] [req-b023] Order ORD-8890 received, processing (duration_ms=70)
[2025-03-15 11:10:40.556] [WARN] [req-b023] service-d call failed immediately — connection refused by service-d
[2025-03-15 11:10:50.778] [WARN] [req-b023] Retrying request to service-d (attempt 2/3)
[2025-03-15 11:11:00.112] [WARN] [req-b023] Retrying request to service-d (attempt 3/3)
[2025-03-15 11:11:10.334] [ERROR] [req-b023] service-d call failed after 3 retries — connection refused by service-d
[2025-03-15 11:11:10.556] [ERROR] [req-b023] Order ORD-8890 failed: payment service unavailable (total_duration_ms=4026)
[2025-03-15 11:15:00.778] [INFO] [req-b024] Order ORD-8895 received, processing (duration_ms=65)
[2025-03-15 11:15:10.112] [WARN] [req-b024] service-d call failed immediately — connection refused by service-d
[2025-03-15 11:15:20.334] [WARN] [req-b024] Retrying request to service-d (attempt 2/3)
[2025-03-15 11:15:30.556] [WARN] [req-b024] Retrying request to service-d (attempt 3/3)
[2025-03-15 11:15:40.778] [ERROR] [req-b024] service-d call failed after 3 retries — connection refused by service-d
[2025-03-15 11:15:41.112] [ERROR] [req-b024] Order ORD-8895 failed: payment service unavailable (total_duration_ms=4047)
[2025-03-15 11:20:00.334] [WARN] [system] Service-b response times averaged 4200ms over last 15 minutes (SLA: 300ms)
[2025-03-15 11:25:00.556] [INFO] [req-b025] Order ORD-8900 received, processing (duration_ms=72)
[2025-03-15 11:25:10.778] [WARN] [req-b025] service-d call failed immediately — connection refused by service-d
[2025-03-15 11:25:20.112] [WARN] [req-b025] Retrying request to service-d (attempt 2/3)
[2025-03-15 11:25:30.334] [WARN] [req-b025] Retrying request to service-d (attempt 3/3)
[2025-03-15 11:25:40.556] [ERROR] [req-b025] service-d call failed after 3 retries — connection refused by service-d
[2025-03-15 11:25:40.778] [ERROR] [req-b025] Order ORD-8900 failed: payment service unavailable (total_duration_ms=4006)
[2025-03-15 11:30:00.112] [WARN] [system] Error rate for service-d calls at 95% — recommending circuit breaker activation
[2025-03-15 11:40:00.334] [WARN] [system] Service-b effectively degraded — all payment-dependent operations failing
[2025-03-15 11:50:00.556] [WARN] [system] Continued degradation, service-d unreachable, 28 orders failed in last hour
SERVICE_B_EOF

# ============================================================================
# service-a.log — API Gateway (DOWNSTREAM EFFECT from service-b)
# ~110 lines. Slow responses from 11:00, SLA breaches by 11:15.
# ============================================================================
cat > logs/service-a.log << 'SERVICE_A_EOF'
[2025-03-15 10:00:01.112] [INFO] [req-a001] GET /api/orders/ORD-8810 — 200 OK (duration_ms=145)
[2025-03-15 10:00:30.334] [INFO] [req-a002] POST /api/orders — 201 Created (duration_ms=210)
[2025-03-15 10:01:15.556] [INFO] [req-a003] GET /api/products/list — 200 OK (duration_ms=95)
[2025-03-15 10:02:00.778] [INFO] [req-a004] POST /api/orders — 201 Created (duration_ms=185)
[2025-03-15 10:03:30.112] [INFO] [req-a005] GET /api/orders/ORD-8815 — 200 OK (duration_ms=130)
[2025-03-15 10:05:00.334] [INFO] [req-a006] POST /api/orders — 201 Created (duration_ms=225)
[2025-03-15 10:06:15.556] [INFO] [req-a007] GET /api/products/list — 200 OK (duration_ms=88)
[2025-03-15 10:08:00.778] [INFO] [req-a008] POST /api/orders — 201 Created (duration_ms=195)
[2025-03-15 10:10:30.112] [INFO] [req-a009] GET /api/notifications/status — 200 OK (duration_ms=110)
[2025-03-15 10:12:00.334] [INFO] [req-a010] POST /api/orders — 201 Created (duration_ms=205)
[2025-03-15 10:14:30.556] [INFO] [req-a011] GET /api/orders/ORD-8825 — 200 OK (duration_ms=135)
[2025-03-15 10:16:00.778] [INFO] [req-a012] POST /api/orders — 201 Created (duration_ms=190)
[2025-03-15 10:18:15.112] [INFO] [req-a013] GET /api/products/list — 200 OK (duration_ms=92)
[2025-03-15 10:20:00.334] [INFO] [req-a014] POST /api/orders — 201 Created (duration_ms=215)
[2025-03-15 10:22:30.556] [INFO] [req-a015] GET /api/orders/ORD-8835 — 200 OK (duration_ms=140)
[2025-03-15 10:25:00.778] [INFO] [req-a016] POST /api/orders — 201 Created (duration_ms=198)
[2025-03-15 10:28:00.112] [INFO] [req-a017] POST /api/orders — 201 Created (duration_ms=230)
[2025-03-15 10:30:30.334] [INFO] [req-a018] GET /api/notifications/status — 200 OK (duration_ms=105)
[2025-03-15 10:33:00.556] [INFO] [req-a019] POST /api/orders — 201 Created (duration_ms=245)
[2025-03-15 10:36:00.778] [INFO] [req-a020] GET /api/orders/ORD-8848 — 200 OK (duration_ms=155)
[2025-03-15 10:39:00.112] [INFO] [req-a021] POST /api/orders — 201 Created (duration_ms=280)
[2025-03-15 10:42:00.334] [INFO] [req-a022] POST /api/orders — 201 Created (duration_ms=310)
[2025-03-15 10:45:00.556] [INFO] [req-a023] GET /api/products/list — 200 OK (duration_ms=98)
[2025-03-15 10:48:00.778] [INFO] [req-a024] POST /api/orders — 201 Created (duration_ms=350)
[2025-03-15 10:50:00.112] [INFO] [req-a025] POST /api/orders — 201 Created (duration_ms=380)
[2025-03-15 10:52:00.334] [INFO] [req-a026] GET /api/notifications/status — 200 OK (duration_ms=115)
[2025-03-15 10:55:00.556] [INFO] [req-a027] POST /api/orders — 201 Created (duration_ms=420)
[2025-03-15 10:57:00.778] [INFO] [req-a028] POST /api/orders — 201 Created (duration_ms=460)
[2025-03-15 10:59:00.112] [INFO] [req-a029] GET /api/orders/ORD-8870 — 200 OK (duration_ms=175)
[2025-03-15 11:00:15.334] [INFO] [req-a030] POST /api/orders — routed to service-b (duration_ms=520)
[2025-03-15 11:00:45.556] [WARN] [req-a030] Slow upstream response from service-b (520ms), approaching SLA threshold
[2025-03-15 11:01:30.778] [INFO] [req-a031] POST /api/orders — routed to service-b (duration_ms=680)
[2025-03-15 11:01:45.112] [WARN] [req-a031] Slow upstream response from service-b (680ms), SLA threshold exceeded
[2025-03-15 11:02:30.334] [INFO] [req-a032] GET /api/products/list — 200 OK (duration_ms=95)
[2025-03-15 11:03:15.556] [INFO] [req-a033] POST /api/orders — routed to service-b (duration_ms=850)
[2025-03-15 11:03:30.778] [WARN] [req-a033] Slow upstream response from service-b (850ms), SLA threshold exceeded
[2025-03-15 11:04:30.112] [INFO] [req-a034] GET /api/notifications/status — 200 OK (duration_ms=108)
[2025-03-15 11:05:15.334] [INFO] [req-a035] POST /api/orders — routed to service-b (duration_ms=1100)
[2025-03-15 11:05:30.556] [WARN] [req-a035] Slow upstream response from service-b (1100ms), significant SLA breach
[2025-03-15 11:06:45.778] [INFO] [req-a036] POST /api/orders — routed to service-b (duration_ms=1350)
[2025-03-15 11:07:00.112] [WARN] [req-a036] Slow upstream response from service-b (1350ms), significant SLA breach
[2025-03-15 11:08:15.334] [INFO] [req-a037] POST /api/orders — routed to service-b (duration_ms=1500)
[2025-03-15 11:08:30.556] [WARN] [req-a037] Slow upstream response from service-b (1500ms), significant SLA breach
[2025-03-15 11:09:00.778] [INFO] [req-a038] GET /api/products/list — 200 OK (duration_ms=90)
[2025-03-15 11:10:30.112] [INFO] [req-a039] POST /api/orders — routed to service-b (duration_ms=1800)
[2025-03-15 11:10:45.334] [WARN] [req-a039] Slow upstream response from service-b (1800ms), critical SLA breach
[2025-03-15 11:11:30.556] [INFO] [req-a040] POST /api/orders — routed to service-b (duration_ms=2100)
[2025-03-15 11:11:45.778] [WARN] [req-a040] Slow upstream response from service-b (2100ms), critical SLA breach
[2025-03-15 11:13:00.112] [INFO] [req-a041] POST /api/orders — routed to service-b (duration_ms=4200)
[2025-03-15 11:13:15.334] [ERROR] [req-a041] Request exceeded gateway timeout — upstream service-b did not respond within 5000ms
[2025-03-15 11:13:15.556] [ERROR] [req-a041] Returning 504 Gateway Timeout to client
[2025-03-15 11:14:00.778] [INFO] [req-a042] POST /api/orders — routed to service-b (duration_ms=4500)
[2025-03-15 11:14:15.112] [ERROR] [req-a042] Request exceeded gateway timeout — upstream service-b did not respond within 5000ms
[2025-03-15 11:14:15.334] [ERROR] [req-a042] Returning 504 Gateway Timeout to client
[2025-03-15 11:15:00.556] [WARN] [system] SLA breach detected: service-a p95 response time 2100ms (SLA: 500ms) over last 15 minutes
[2025-03-15 11:15:30.778] [INFO] [req-a043] POST /api/orders — routed to service-b (duration_ms=4800)
[2025-03-15 11:15:45.112] [ERROR] [req-a043] Request exceeded gateway timeout — upstream service-b did not respond within 5000ms
[2025-03-15 11:15:45.334] [ERROR] [req-a043] Returning 504 Gateway Timeout to client
[2025-03-15 11:16:30.556] [INFO] [req-a044] GET /api/products/list — 200 OK (duration_ms=92)
[2025-03-15 11:17:15.778] [INFO] [req-a045] POST /api/orders — routed to service-b (duration_ms=4100)
[2025-03-15 11:17:30.112] [ERROR] [req-a045] Request exceeded gateway timeout — upstream service-b did not respond within 5000ms
[2025-03-15 11:17:30.334] [ERROR] [req-a045] Returning 504 Gateway Timeout to client
[2025-03-15 11:18:15.556] [INFO] [req-a046] GET /api/notifications/status — 200 OK (duration_ms=112)
[2025-03-15 11:19:00.778] [INFO] [req-a047] POST /api/orders — routed to service-b (duration_ms=4600)
[2025-03-15 11:19:15.112] [ERROR] [req-a047] Request exceeded gateway timeout — upstream service-b did not respond within 5000ms
[2025-03-15 11:19:15.334] [ERROR] [req-a047] Returning 504 Gateway Timeout to client
[2025-03-15 11:20:00.556] [WARN] [system] SLA breach sustained: service-a error rate 35% over last 10 minutes (threshold: 5%)
[2025-03-15 11:21:00.778] [INFO] [req-a048] POST /api/orders — routed to service-b (duration_ms=4300)
[2025-03-15 11:21:15.112] [ERROR] [req-a048] Request exceeded gateway timeout — upstream service-b did not respond within 5000ms
[2025-03-15 11:21:15.334] [ERROR] [req-a048] Returning 504 Gateway Timeout to client
[2025-03-15 11:23:00.556] [INFO] [req-a049] POST /api/orders — routed to service-b (duration_ms=4700)
[2025-03-15 11:23:15.778] [ERROR] [req-a049] Request exceeded gateway timeout — upstream service-b did not respond within 5000ms
[2025-03-15 11:23:16.112] [ERROR] [req-a049] Returning 504 Gateway Timeout to client
[2025-03-15 11:25:00.334] [WARN] [system] SLA breach critical: service-a p99 response time 4800ms, error rate 42%
[2025-03-15 11:26:00.556] [INFO] [req-a050] POST /api/orders — routed to service-b (duration_ms=4900)
[2025-03-15 11:26:15.778] [ERROR] [req-a050] Request exceeded gateway timeout — upstream service-b did not respond within 5000ms
[2025-03-15 11:26:16.112] [ERROR] [req-a050] Returning 504 Gateway Timeout to client
[2025-03-15 11:28:00.334] [INFO] [req-a051] POST /api/orders — routed to service-b (duration_ms=4500)
[2025-03-15 11:28:15.556] [ERROR] [req-a051] Request exceeded gateway timeout — upstream service-b did not respond within 5000ms
[2025-03-15 11:28:15.778] [ERROR] [req-a051] Returning 504 Gateway Timeout to client
[2025-03-15 11:30:00.112] [WARN] [system] Circuit breaker tripped for service-b — too many consecutive failures (12 in last 5 minutes)
[2025-03-15 11:30:00.334] [WARN] [system] All POST /api/orders requests will be rejected with 503 Service Unavailable
[2025-03-15 11:30:30.556] [INFO] [req-a052] POST /api/orders — 503 Service Unavailable (circuit breaker open for service-b) (duration_ms=5)
[2025-03-15 11:31:15.778] [INFO] [req-a053] GET /api/products/list — 200 OK (duration_ms=88)
[2025-03-15 11:32:00.112] [INFO] [req-a054] POST /api/orders — 503 Service Unavailable (circuit breaker open for service-b) (duration_ms=3)
[2025-03-15 11:33:30.334] [INFO] [req-a055] GET /api/notifications/status — 200 OK (duration_ms=105)
[2025-03-15 11:35:00.556] [INFO] [req-a056] POST /api/orders — 503 Service Unavailable (circuit breaker open for service-b) (duration_ms=4)
[2025-03-15 11:37:00.778] [INFO] [req-a057] GET /api/products/list — 200 OK (duration_ms=91)
[2025-03-15 11:40:00.112] [WARN] [system] Circuit breaker half-open — attempting probe request to service-b
[2025-03-15 11:40:05.334] [ERROR] [system] Probe request to service-b failed — circuit breaker re-tripped
[2025-03-15 11:40:05.556] [WARN] [system] Circuit breaker remains open for service-b
[2025-03-15 11:45:00.778] [INFO] [req-a058] POST /api/orders — 503 Service Unavailable (circuit breaker open for service-b) (duration_ms=3)
[2025-03-15 11:50:00.112] [WARN] [system] Circuit breaker half-open — attempting probe request to service-b
[2025-03-15 11:50:05.334] [ERROR] [system] Probe request to service-b failed — circuit breaker re-tripped
[2025-03-15 11:50:05.556] [WARN] [system] Service-a order processing completely unavailable for 20+ minutes
SERVICE_A_EOF

# ============================================================================
# service-c.log — Notification Service (MOSTLY HEALTHY)
# ~40 lines. Normal throughout, minor queue backup after 11:00.
# ============================================================================
cat > logs/service-c.log << 'SERVICE_C_EOF'
[2025-03-15 10:00:08.112] [INFO] [req-c001] Email notification sent for order ORD-8810 (duration_ms=85)
[2025-03-15 10:01:30.334] [INFO] [req-c002] SMS notification sent for order ORD-8812 (duration_ms=120)
[2025-03-15 10:03:45.556] [INFO] [req-c003] Email notification sent for order ORD-8815 (duration_ms=78)
[2025-03-15 10:06:00.778] [INFO] [req-c004] Push notification sent for order ORD-8820 (duration_ms=65)
[2025-03-15 10:09:15.112] [INFO] [req-c005] Email notification sent for order ORD-8823 (duration_ms=92)
[2025-03-15 10:12:30.334] [INFO] [req-c006] SMS notification sent for order ORD-8830 (duration_ms=110)
[2025-03-15 10:15:45.556] [INFO] [req-c007] Email notification sent for order ORD-8833 (duration_ms=88)
[2025-03-15 10:19:00.778] [INFO] [req-c008] Push notification sent for order ORD-8835 (duration_ms=72)
[2025-03-15 10:22:15.112] [INFO] [req-c009] Email notification sent for order ORD-8840 (duration_ms=95)
[2025-03-15 10:25:30.334] [INFO] [req-c010] SMS notification sent for order ORD-8842 (duration_ms=105)
[2025-03-15 10:28:45.556] [INFO] [req-c011] Email notification sent for order ORD-8845 (duration_ms=82)
[2025-03-15 10:32:00.778] [INFO] [req-c012] Push notification sent for order ORD-8848 (duration_ms=68)
[2025-03-15 10:35:15.112] [INFO] [req-c013] Email notification sent for order ORD-8850 (duration_ms=90)
[2025-03-15 10:38:30.334] [INFO] [req-c014] SMS notification sent for order ORD-8853 (duration_ms=115)
[2025-03-15 10:42:00.556] [INFO] [req-c015] Email notification sent for order ORD-8855 (duration_ms=78)
[2025-03-15 10:45:15.778] [INFO] [req-c016] Push notification sent for order ORD-8858 (duration_ms=70)
[2025-03-15 10:48:30.112] [INFO] [req-c017] Email notification sent for order ORD-8860 (duration_ms=88)
[2025-03-15 10:52:00.334] [INFO] [req-c018] SMS notification sent for order ORD-8863 (duration_ms=102)
[2025-03-15 10:55:30.556] [INFO] [req-c019] Email notification sent for order ORD-8865 (duration_ms=82)
[2025-03-15 10:58:45.778] [INFO] [req-c020] Push notification sent for order ORD-8868 (duration_ms=75)
[2025-03-15 11:02:00.112] [INFO] [req-c021] Email notification sent for order ORD-8870 (duration_ms=90)
[2025-03-15 11:05:30.334] [INFO] [req-c022] SMS notification sent for order ORD-8872 (duration_ms=108)
[2025-03-15 11:09:00.556] [INFO] [req-c023] Email notification queued (duration_ms=95)
[2025-03-15 11:12:00.778] [WARN] [system] Notification queue depth increased to 15 (normal: <5) — fewer order confirmations arriving from service-a
[2025-03-15 11:15:30.112] [INFO] [req-c024] Email notification sent for order ORD-8875 (duration_ms=85)
[2025-03-15 11:18:00.334] [WARN] [system] Notification queue depth at 22 — order confirmation rate dropped significantly
[2025-03-15 11:22:00.556] [INFO] [req-c025] Push notification sent for failed order alert ORD-8880 (duration_ms=72)
[2025-03-15 11:25:30.778] [INFO] [req-c026] Email notification sent for failed order alert ORD-8883 (duration_ms=88)
[2025-03-15 11:28:00.112] [WARN] [system] Sending failure notification emails — 8 orders failed in last 30 minutes
[2025-03-15 11:30:30.334] [INFO] [req-c027] Batch failure notification sent to operations team (duration_ms=145)
[2025-03-15 11:35:00.556] [INFO] [req-c028] Email notification sent for system alert (duration_ms=82)
[2025-03-15 11:40:00.778] [INFO] [req-c029] Push notification sent for system alert (duration_ms=68)
[2025-03-15 11:45:30.112] [INFO] [req-c030] Email notification sent for escalation alert (duration_ms=95)
[2025-03-15 11:50:00.334] [INFO] [req-c031] Batch failure notification sent to operations team (duration_ms=130)
SERVICE_C_EOF

# ============================================================================
# service-e.log — Inventory Service (COMPLETELY HEALTHY)
# ~35 lines. Normal throughout, all responses under 100ms.
# ============================================================================
cat > logs/service-e.log << 'SERVICE_E_EOF'
[2025-03-15 10:00:06.445] [INFO] [req-e001] Inventory check for SKU-4401: 142 units available (duration_ms=35)
[2025-03-15 10:00:36.667] [INFO] [req-e002] Stock reserved for order ORD-8812: 3 units of SKU-4401 (duration_ms=42)
[2025-03-15 10:02:23.891] [INFO] [req-e003] Stock reserved for order ORD-8815: 1 unit of SKU-4405 (duration_ms=38)
[2025-03-15 10:05:42.112] [INFO] [req-e004] Stock reserved for order ORD-8820: 5 units of SKU-4410 (duration_ms=45)
[2025-03-15 10:08:41.334] [INFO] [req-e005] Stock reserved for order ORD-8823: 2 units of SKU-4412 (duration_ms=40)
[2025-03-15 10:12:56.556] [INFO] [req-e006] Stock reserved for order ORD-8830: 1 unit of SKU-4418 (duration_ms=36)
[2025-03-15 10:15:10.778] [INFO] [req-e007] Inventory check for SKU-4420: 88 units available (duration_ms=32)
[2025-03-15 10:18:16.112] [INFO] [req-e008] Stock reserved for order ORD-8835: 4 units of SKU-4420 (duration_ms=48)
[2025-03-15 10:22:36.334] [INFO] [req-e009] Stock reserved for order ORD-8840: 2 units of SKU-4425 (duration_ms=41)
[2025-03-15 10:25:00.556] [INFO] [req-e010] Inventory check for SKU-4428: 210 units available (duration_ms=30)
[2025-03-15 10:28:39.778] [INFO] [req-e011] Stock reserved for order ORD-8845: 3 units of SKU-4428 (duration_ms=44)
[2025-03-15 10:33:11.112] [INFO] [req-e012] Stock reserved for order ORD-8848: 1 unit of SKU-4432 (duration_ms=37)
[2025-03-15 10:39:51.334] [INFO] [req-e013] Stock reserved for order ORD-8854: 2 units of SKU-4435 (duration_ms=43)
[2025-03-15 10:45:26.556] [INFO] [req-e014] Stock reserved for order ORD-8858: 1 unit of SKU-4440 (duration_ms=39)
[2025-03-15 10:47:40.778] [INFO] [req-e015] Stock reserved for order ORD-8862: 3 units of SKU-4442 (duration_ms=46)
[2025-03-15 10:53:41.112] [INFO] [req-e016] Stock reserved for order ORD-8870: 2 units of SKU-4448 (duration_ms=40)
[2025-03-15 10:58:00.334] [INFO] [req-e017] Inventory check for SKU-4450: 175 units available (duration_ms=33)
[2025-03-15 11:03:00.556] [INFO] [req-e018] Inventory check for SKU-4455: 63 units available (duration_ms=35)
[2025-03-15 11:08:00.778] [INFO] [req-e019] Inventory check for SKU-4460: 92 units available (duration_ms=31)
[2025-03-15 11:13:00.112] [INFO] [req-e020] Inventory check for SKU-4465: 148 units available (duration_ms=38)
[2025-03-15 11:18:00.334] [INFO] [req-e021] Inventory check for SKU-4468: 55 units available (duration_ms=34)
[2025-03-15 11:23:00.556] [INFO] [req-e022] Inventory check for SKU-4472: 201 units available (duration_ms=29)
[2025-03-15 11:28:00.778] [INFO] [req-e023] Inventory check for SKU-4475: 87 units available (duration_ms=42)
[2025-03-15 11:33:00.112] [INFO] [req-e024] Inventory check for SKU-4480: 134 units available (duration_ms=36)
[2025-03-15 11:38:00.334] [INFO] [req-e025] Inventory check for SKU-4485: 66 units available (duration_ms=33)
[2025-03-15 11:43:00.556] [INFO] [req-e026] Inventory check for SKU-4490: 112 units available (duration_ms=37)
[2025-03-15 11:48:00.778] [INFO] [req-e027] Inventory check for SKU-4495: 79 units available (duration_ms=35)
SERVICE_E_EOF

git add -A
git commit -q -m "Add service logs, topology, and SLA definitions for incident analysis"
