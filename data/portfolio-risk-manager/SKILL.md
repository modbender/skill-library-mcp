---
name: portfolio-risk-manager
description: Thiết lập kỷ luật quản trị danh mục (IPS mini) + position sizing theo risk budgeting cho nhà đầu tư cổ phiếu (không margin), biến khuyến nghị thành “có điều kiện” (trigger/invalidation/horizon/confidence), giảm overtrading và giúp daily/weekly/monthly nhất quán.
metadata: {"openclaw":{"emoji":"🛡️"}}
disable-model-invocation: false
---

# Portfolio Risk Manager (No-Margin, No Sector Preference)

## Skill này để làm gì
Skill này đóng vai trò **“hiến pháp danh mục” (IPS mini)** và **risk budgeting** để:
- Giữ kỷ luật (không bị tin tức kéo tay).
- Tránh rủi ro tập trung (1 mã kéo sập danh mục).
- Chuẩn hoá khuyến nghị thành **thiên hướng có điều kiện** (không lệnh tuyệt đối).
- Tái cân bằng bằng dòng tiền nạp thêm (ví dụ 10 triệu/tháng) thay vì xoay vòng quá mức.

## Phạm vi (Scope)
- Nhà đầu tư cổ phiếu Việt Nam.
- **Không margin/đòn bẩy**.
- **Không yêu cầu chọn ngành cụ thể** (ưu tiên đa dạng hóa tự nhiên).
- Watchlist do user xác nhận (`ACTIVE_WATCHLIST`).

## Không làm gì (Non-goals)
- Không đưa lệnh mua/bán tuyệt đối kiểu “mua ngay/cắt ngay”.
- Không đề xuất margin, phái sinh.
- Không tự thay `ACTIVE_WATCHLIST` (chỉ tạo *draft* đề xuất).

## Input contract
Tối thiểu cần:
- `ACTIVE_WATCHLIST`: danh sách ticker user chốt.
- `MONTHLY_CASH_INFLOW_VND`: số tiền nạp thêm mỗi tháng (vd: 10000000).

Nếu có thì dùng thêm (tốt hơn):
- `HOLDINGS` hiện tại (ticker, weight%, cost_basis nếu user có).
- `RISK_PROFILE`: horizon (ngắn/trung/dài), `max_drawdown_pct`.
- `CONFIDENCE_MAP`: confidence theo ticker từ `equity-valuation-framework` / orchestrator.

Nếu thiếu `HOLDINGS/weights`:
- Phải xuất policy chung + nêu rõ dữ liệu cần user bổ sung.

## Output format (bắt buộc)
Xuất đúng 5 khối sau:

### 1) IPS mini
- Objective
- Horizon
- Max drawdown mục tiêu
- 6–10 rules (kỷ luật)

### 2) Sizing policy (khung tỷ trọng)
Mặc định gợi ý (có thể chỉnh khi user nói khác):
- `max_single_name_weight_pct`: 10–12%
- `starter_position_pct`: 2–3% (thăm dò)
- `add_on_step_pct`: 1–3%/lần khi trigger xác nhận
- `cash_buffer_pct`: 5%
- Leverage: 0%

### 3) Per-ticker risk plan (theo watchlist)
Với mỗi mã:
- Horizon
- Trigger **ADD** (điều kiện tăng thăm dò/tăng tỷ trọng)
- Trigger **REDUCE** (điều kiện giảm rủi ro)
- **Invalidation** (điều kiện thesis sai → phải giảm/cắt)
- Confidence + data gaps

### 4) Rebalance plan
- Cadence: monthly review + drift threshold
- Drift threshold gợi ý: 5% (hoặc theo user)
- Ưu tiên dùng cashflow mới để rebalance trước khi bán/mua xoay vòng

### 5) Checklist kỳ tới
3–8 mục: trigger quan trọng, dữ liệu cần xác nhận, sự kiện cần theo dõi.

## Guardrails
- Single source of truth: luôn dùng `ACTIVE_WATCHLIST`, không tự đổi.
- Không lệnh tuyệt đối; chỉ “thiên hướng + điều kiện + invalidation + confidence”.
- Khi confidence thấp / thiếu dữ liệu: ưu tiên starter size + nêu rõ gaps.
- Tách Fact vs Interpretation.

## Workflow (cách làm)
1) Tạo IPS mini theo thông tin user (không margin).
2) Thiết lập sizing policy (cap, starter, add-on, cash buffer).
3) Map watchlist → triggers/invalidation (dựa trên outputs macro/news/valuation nếu có).
4) Chốt rebalance plan (time + threshold; dùng cashflow mới).
5) Xuất checklist + gaps.
