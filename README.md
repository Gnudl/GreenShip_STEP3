# GreenShip – STEP 2

Nhóm Hải Thần: Đặng Long Ngũ, Nguyễn Trần Như Nguyệt, Nguyễn Phương Thùy.

## Mục tiêu
Chuẩn bị dữ liệu thật và xây dựng hàm evaluate_route() độc lập với COA/RIME. Đánh giá 3 tuyến thủ công, có ít nhất 10 kiểm thử và minh chứng kết quả.

## Cấu trúc
- config/: kịch bản, cấu hình tàu và giả định đã thống nhất (Ngũ).
- data/raw/: dữ liệu thời tiết gốc, không sửa trực tiếp (Nguyệt).
- data/processed/: dữ liệu đã chuẩn hóa UTC, đơn vị và phạm vi (Nguyệt).
- data/land/: polygon đất/biển và thông tin nguồn (Thùy).
- data/routes/: 3 tuyến thủ công dạng JSON/GeoJSON (Ngũ và Thùy).
- data/source_register.csv: danh mục nguồn dữ liệu, metadata và điều kiện sử dụng.
- src/: weather.py (Nguyệt), route_geometry.py và evaluator.py (Ngũ), constraints.py (Thùy); sẽ tạo khi triển khai từng nhiệm vụ.
- tests/: kiểm thử evaluator, hình học, dữ liệu và ràng buộc (Thùy, cả nhóm kiểm tra chéo).
- outputs/maps/: bản đồ vùng dữ liệu và 3 tuyến.
- outputs/evaluations/: JSON kết quả, chi tiết từng đoạn và bảng so sánh.
- outputs/tests/: log kiểm thử thực tế.
- screenshots/: ảnh bằng chứng truy cập, đọc và kiểm tra dữ liệu.
- reports/: báo cáo STEP 2, bảng kiểm và ghi nhận hạn chế.

## Trình tự thực hiện
1. Khóa kịch bản và kiểm tra dữ liệu thật.
2. Chuẩn hóa dữ liệu, xây dựng weather_at().
3. Biểu diễn tuyến, kiểm tra hình học và ràng buộc.
4. Xây dựng evaluate_route() và đối chiếu tính tay.
5. Chạy kiểm thử, xuất bản đồ/kết quả và hoàn thiện báo cáo.

## Trạng thái hiện tại — 24/10/2026
- Đã tải và đọc được dữ liệu ERA5 gió, ERA5 sóng, Copernicus Marine dòng chảy và Natural Earth Land 5.1.1.
- Đã hoàn thành `data/source_register.csv` với bốn nguồn và kiểm tra các tệp cục bộ.
- Đã khóa hợp đồng dữ liệu ban đầu trong `config/scenario.yaml`; hai điểm tiếp cận cảng và mini-case đều không nằm trên đất theo Natural Earth.
- Đã tạo `config/ship.json`. Các thông số vận hành hiện là giả định của toy model và chưa được dùng để công bố mức phát thải thực tế.
- `src/inspect_data.py` tạo `outputs/data_audit.csv`, `outputs/data_audit.json` và ảnh bằng chứng đọc dữ liệu.
- `src/map_domain.py` tạo bản đồ vùng dữ liệu và kết quả kiểm tra land mask cho các điểm mô hình.

Việc tiếp theo là chuẩn hóa dữ liệu vào `data/processed/`, xây dựng `weather_at()` và kiểm tra ba truy vấn độc lập. Không đánh dấu hoàn thành STEP 2 khi chưa đủ 16 tiêu chí nghiệm thu.

## Chạy phần dữ liệu và weather lookup

Từ thư mục gốc dự án:

```powershell
python -m pip install -r requirements.txt
python .\src\inspect_data.py
python .\src\normalize_data.py
python .\src\check_weather.py
python -m pytest .\tests\test_weather.py -q
```

`normalize_data.py` giữ nguyên `NaN`, chuẩn hóa tên trục thời gian thành `time`, sắp xếp tọa độ và lưu dữ liệu vào `data/processed/`. Hàm `weather_at()` dùng nearest neighbour có kiểm tra miền không gian và thời gian trước khi truy vấn. Gió và sóng là bắt buộc; dòng chảy là tùy chọn.

Hình sinh tự động nằm trong `outputs/`. Thư mục `screenshots/` chỉ dùng cho ảnh nhóm tự chụp Terminal hoặc giao diện làm bằng chứng.
