---
name: tra-cuu-phat-nguoi-vn
description: Tra cứu phạt nguội phương tiện tại Việt Nam. Use when user asks to check traffic fines in VN by license plate (ô tô/xe máy), especially via VNeTraffic-style lookup and CSGT cross-check guidance.
---

# Tra cứu phạt nguội VN

Tra cứu nhanh bằng endpoint của VNeTraffic, sau đó hướng dẫn đối chiếu nguồn chính thống (CSGT/Đăng kiểm) khi cần xác nhận.

## Chạy tra cứu nhanh

Dùng script:

```bash
node scripts/check_vnetraffic.mjs --plate <BIENSO> --type <oto|xemay|xemaydien> [--phone <SODT>]
```

Ví dụ:

```bash
node scripts/check_vnetraffic.mjs --plate 51K12345 --type oto
```

Quy tắc nhập biển số:
- Chuẩn hóa về chữ hoa.
- Bỏ dấu `-` và `.` trước khi gửi API.
- Ví dụ: `51K-123.45` -> `51K12345`.

## Diễn giải kết quả

- Nếu có lỗi vi phạm (`totalViolations > 0`):
  - Tóm tắt: tổng số lỗi, số chưa xử phạt, số đã xử phạt.
  - Liệt kê: thời gian, địa điểm, trạng thái, đơn vị xử lý, nơi nộp phạt.
- Nếu không có lỗi hoặc không có dữ liệu:
  - Báo rõ là chưa thấy dữ liệu trên nguồn tra cứu trung gian.
  - Khuyến nghị đối chiếu lại trên cổng chính thống.

## Cảnh báo độ tin cậy

- `vnetraffic.org` là nguồn trung gian, không phải cổng nhà nước chính thức.
- Luôn nói rõ: kết luận chính thức nên đối chiếu tại:
  - https://www.csgt.vn (Tra cứu phạt nguội)
  - Cổng tra cứu của Cục Đăng Kiểm (khi phù hợp)

## Fallback khi không thể tự động hóa

Nếu endpoint lỗi, timeout, hoặc trang chính thống yêu cầu CAPTCHA:
1. Xin user chụp màn hình kết quả tra cứu.
2. Đọc/diễn giải giúp user các trường quan trọng.
3. Nhắc bước xử lý tiếp theo ngắn gọn, không dọa, không suy diễn.
