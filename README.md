# Addon Settings & Filters

Nơi lưu trữ cấu hình, bộ lọc quảng cáo cho các tiện ích trình duyệt (uBlock Origin, Violentmonkey/Tampermonkey...) được quản lý và tự động hóa qua Git.

---

## Danh sách bộ lọc cho uBlock Origin

### Lựa chọn 1: Bộ lọc siêu tổng hợp (All-in-One - Tự động gom & lọc trùng)
> Tự động tải từ 15 danh sách nguồn (uBlock, EasyList, AdGuard, EasyPrivacy, Malicious URL, Cookie Notices, ABPVN + Rules cá nhân), khử sạch các quy tắc trùng lặp qua GitHub Actions mỗi ngày.

- **Link jsDelivr CDN (Khuyên dùng):**
  ```text
  https://cdn.jsdelivr.net/gh/quanghy-hub/addon-setting@main/filters_all_in_one.txt
  ```
- **Link GitHub Raw trực tiếp:**
  ```text
  https://raw.githubusercontent.com/quanghy-hub/addon-setting/main/filters_all_in_one.txt
  ```

---

### Lựa chọn 2: Bộ lọc cá nhân bổ sung (Custom Filters Only)
> Chỉ chứa các quy tắc riêng do anh Huy tự bổ sung (tối ưu cho VOZ, XamVN, Phe69, Heiliao, Chợ Tốt...).

- **Link jsDelivr CDN:**
  ```text
  https://cdn.jsdelivr.net/gh/quanghy-hub/addon-setting@main/filters.txt
  ```
- **Link GitHub Raw:**
  ```text
  https://raw.githubusercontent.com/quanghy-hub/addon-setting/main/filters.txt
  ```

---

## Cơ chế tự động hóa (Automation Architecture)
- **Engine biên dịch:** Script Python `scripts/compile_filters.py` tải đa luồng, loại bỏ comment rác và deduplicate hàng trăm nghìn quy tắc trong < 3 giây.
- **GitHub Actions (`.github/workflows/update_filters.yml`):** Tự động kích hoạt hàng ngày lúc **03:00 UTC (10:00 sáng VN)** để cập nhật quy tắc mới từ các nguồn upstream, commit và push tự động vào repo mà không tốn tài nguyên máy tính cá nhân.
- **Kích hoạt thủ công:**
  - Trên GitHub: Tab **Actions** -> Chọn `Auto-Compile & Update Filters` -> bấm `Run workflow`.
  - Trên Mac: Chạy lệnh `python3 scripts/compile_filters.py`.
