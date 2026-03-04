---
name: futa-tracker
description: Track FUTA Express (Phương Trang) package delivery status using their public API. Use when the user wants to track/tra cứu đơn hàng, kiện hàng from FUTA Express, FUTA Express, or Phương Trang Express. Requires a tracking code (mã vận đơn) to query.
---

# Futa Tracker

## Overview

This skill enables tracking of FUTA Express (Phương Trang) package delivery status via their public API.

## API Endpoint

```
https://api.futaexpress.vn/bo-operation/f1/full-bill-by-code-public/<tracking_code>
```

## Tracking Workflow

1. Extract tracking code from user input
2. Use `web_fetch` to call the API
3. Parse the JSON response
4. Present detailed tracking information
5. **CRITICAL**: Keep all values in original Vietnamese - DO NOT translate

## Response Structure

Key fields in the response:
- `data.barcode` - Mã vận đơn
- `data.from_fullname` / `data.from_phone` - Người gửi
- `data.to_fullname` / `data.to_phone` - Người nhận
- `data.from_department_name` - Điểm gửi
- `data.to_department_name` - Điểm đến
- `data.service_type_name` - Loại dịch vụ
- `data.pay_type` - Hình thức thanh toán
- `data.package_total` - Số kiện
- `data.totalcost` - Tổng chi phí
- `data.addcost` - Phụ phí
- `data.status_bill` - Trạng thái đơn hàng
- `data.note` - Ghi chú
- `data.packages[]` - Chi tiết từng kiện hàng
  - `package_description` - Mô tả hàng
  - `receive_fullname` / `receive_phone` / `receive_identity` - Người nhận thực tế
  - `receive_time` - Thời gian nhận hàng
  - `arrival_time` - Thời gian đến nơi
  - `go_time` - Thời gian xuất phát
  - `arrival_note` - Ghi chú đến nơi
- `data.services[]` - Dịch vụ thêm
  - `add_service_name` - Tên dịch vụ
  - `value` - Giá dịch vụ
- `data.trackings[]` - Lịch sử (thường trùng với packages data)

## Output Format

Present information in this order:

```
📦 FUTA Express - Tra cứu vận đơn: <barcode>

👤 Người gửi: <from_fullname>
   📞 <from_phone>
   🏢 Điểm gửi: <from_department_name>

👤 Người nhận: <to_fullname>
   📞 <to_phone>
   🏢 Điểm đến: <to_department_name>

📋 Thông tin đơn hàng:
   • Loại dịch vụ: <service_type_name>
   • Hình thức thanh toán: <pay_type>
   • Số kiện: <package_total>
   • Tổng chi phí: <totalcost>đ (cước chính: <cost_main>đ + phụ: <addcost>đ)
   • Trạng thái: <status_bill>

📦 Chi tiết hàng hóa:
   • <packages[*].package_description>
   Ghi chú vận chuyển: <packages[*].arrival_note>

🔐 Người nhận thực tế (nếu đã giao):
   • Tên: <packages[*].receive_fullname>
   • SĐT: <packages[*].receive_phone>
   • CMND/CCCD: <packages[*].receive_identity>
   • Thời gian nhận: <packages[*].receive_time>

📝 Ghi chú đơn hàng: <note>

📍 Lịch sử vận chuyển:
| Thời gian | Trạng thái | Chi tiết |
|-----------|------------|----------|
| <time> | <status> | <details> |

🛎️ Dịch vụ thêm:
   • <add_service_name>: <value>đ
```

## Important Rules

- **NEVER translate Vietnamese values** - status names, department names, everything stays in Vietnamese
- Format currency with periods (e.g., 350.000đ)
- Hide partial phone/ID info if present (masked with X or shown as is from API)
- Show timestamps in readable format (YYYY-MM-DD HH:MM)
- Display all meaningful data from the response

## Error Handling

- If `data.bill_id` is 0: Tracking code not found
- If `data.packages` is empty: No package details available
- Always show the full response data even if some fields are empty
