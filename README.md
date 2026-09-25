# Addon Settings & Filters

Nơi lưu trữ cấu hình, bộ lọc quảng cáo cho các tiện ích trình duyệt (uBlock Origin, Violentmonkey/Tampermonkey...) được quản lý và đồng bộ qua Git.

## Bộ lọc uBlock Origin (URL đăng ký)

### 1. Link jsDelivr CDN (Khuyên dùng - tốc độ cao, không trễ cache):
```text
https://cdn.jsdelivr.net/gh/quanghy-hub/addon-setting@main/filters.txt
```

### 2. Link GitHub Raw trực tiếp:
```text
https://raw.githubusercontent.com/quanghy-hub/addon-setting/main/filters.txt
```

## Hướng dẫn thêm vào uBlock Origin:
1. Mở Cài đặt uBlock Origin (Dashboard) -> tab **Danh sách bộ lọc (Filter lists)**.
2. Cuộn xuống dưới cùng -> mở phần **Nhập (Import...)**.
3. Dán 1 trong 2 URL ở trên vào.
4. Bấm **Áp dụng thay đổi (Apply changes)**.
5. *(Quan trọng)* Đối với các bộ lọc có scriptlet `trusted-`: bấm vào biểu tượng `[i]` cạnh tên danh sách vừa nhập và tích chọn **Tin cậy danh sách này (Trust this list)**.
