# BÁO CÁO TIẾN ĐỘ VÀ KẾT QUẢ THỰC NGHIỆM CHI TIẾT – GREENSHIP STEP 2
**Cơ quan / Đơn vị:** Đề tài Nghiên cứu Khoa học Sinh viên GreenShip  
**Tên nhóm:** Nhóm Hải Thần (Đặng Long Ngũ, Nguyễn Trần Như Nguyệt, Nguyễn Phương Thùy)  
**Thời điểm xuất báo cáo:** 2026-11-13 (UTC)  
**Tiến độ tổng thể:** **100% HOÀN THÀNH STEP 2** (Sẵn sàng nghiệm thu chuyển sang STEP 3)  

---

## PHẦN 1: BÁO CÁO TIẾN ĐỘ THỰC HIỆN DỰ ÁN (PROGRESS REPORT)

| Bước thực hiện | Nội dung trọng tâm | Người phụ trách | Trạng thái | Tiến độ |
|---|---|---|---|:---:|
| **Bước 1** | Khóa kịch bản và kiểm tra dữ liệu thật | Ngũ, Nguyệt | **HOÀN THÀNH** | 100% |
| **Bước 2** | Chuẩn hóa dữ liệu, xây dựng `weather_at()` | Nguyệt | **HOÀN THÀNH** | 100% |
| **Bước 3** | Biểu diễn tuyến, kiểm tra hình học và ràng buộc | Ngũ, Thùy | **HOÀN THÀNH** | 100% |
| **Bước 4** | Xây dựng `evaluate_route()` và đối chiếu tính tay | Ngũ, Thùy | **HOÀN THÀNH** | 100% |
| **Bước 5** | Chạy kiểm thử, xuất bản đồ/kết quả, hoàn thiện báo cáo | Cả nhóm | **HOÀN THÀNH** | 100% |

---

## PHẦN 2: CHI TIẾT NHỮNG GÌ NHÓM ĐÃ LÀM ĐƯỢC (WORK ACCOMPLISHED)

### 1. Khóa Kịch bản và Phân công Trách nhiệm
- **Tuyến kịch bản chính:** Hải Phòng (20.6667°N, 106.8333°E) → Cái Mép–Thị Vải (10.4200°N, 107.0800°E). Toạ độ là điểm tiếp cận ngoài khơi (approach points), đã kiểm tra không nằm trên đất liền theo Natural Earth Land.
- **Thời điểm khởi hành:** `2024-10-10T00:00:00Z` (tương đương 07:00 ngày 10/10/2024 giờ Việt Nam).
- **Miền dữ liệu (Bounding Box):** `[105°E - 111°E, 9°N - 22°N]`, hệ quy chiếu WGS84 (EPSG:4326).
- **Tàu mẫu giả định:** Handysize 40,000 DWT, Tốc độ qua nước STW = 12 kn, Công suất máy chính = 5,000 kW, SFOC = 190 g/kWh, Nhiên liệu HFO với hệ số phát thải $C_F = 3.114\text{ tCO}_2/\text{t-fuel}$.

### 2. Thu thập và Xử lý 4 Nguồn Dữ liệu Thật
Nhóm đã tải, kiểm tra tính toàn vẹn và lập danh mục nguồn tại `data/source_register.csv`:
1. **Gió ERA5 (`u10`, `v10`):** 120 bước thời gian (1 giờ/bước), lưới $0.25^\circ$ ($53 \times 25$ ô), 159,000 ô dữ liệu, 0% missing.
2. **Sóng ERA5 (`swh`):** 120 bước thời gian, lưới $0.5^\circ$ ($27 \times 13$ ô), 42,120 ô dữ liệu, chiều cao sóng có ý nghĩa.
3. **Dòng chảy Copernicus Marine (`uo`, `vo`):** 5 ngày (trung bình ngày), lưới $1/12^\circ$ ($157 \times 72$ ô), lớp mặt $0.494\text{ m}$, 56,520 ô dữ liệu.
4. **Đất liền Natural Earth Land 5.1.1:** Shapefile tỷ lệ 1:10 triệu, dùng cho thuật toán kiểm tra giao cắt đa giác mặt đất.

### 3. Xây dựng Hàm Tra cứu Thời tiết Minh bạch `weather_at()`
- Tự động kiểm tra phạm vi không gian (bbox) và thời gian trước khi truy vấn.
- Nguyên tắc xử lý ô thiếu: Giữ nguyên NaN, tuyệt đối không thay thế bằng 0.
- Với sóng gần bờ: Áp dụng cơ chế fallback tìm ô biển hợp lệ gần nhất trong phạm vi $\le 30\text{ NM}$, có ghi nhật ký truy vết.

### 4. Xây dựng Hình học Tuyến và Kiểm định Cắt Đất
- Tính toán khoảng cách theo trắc địa WGS84 geodesic (`geopy` / ellipsoidal distance).
- Tự động chia nhỏ tuyến thành các đoạn lấy mẫu với bước tối đa $\le 5\text{ NM}$.
- Kiểm tra giao cắt đất liền theo từng đoạn thẳng thay vì chỉ kiểm tra các điểm waypoint.

### 5. Xây dựng Hàm Đánh giá Thống nhất `evaluate_route()`
- Hàm đánh giá thuần túy, tất định (deterministic), không dùng số ngẫu nhiên, độc lập hoàn toàn với thuật toán COA–RIME.
- Tích hợp ảnh hưởng của dòng chảy dọc tuyến vào tốc độ qua đất: $\text{SOG} = \text{STW} + u_{\text{along}}$.
- Tính toán thời gian, tiêu thụ nhiên liệu và ước tính phát thải $\text{CO}_2$ theo từng bước mẫu và tích lũy toàn tuyến.
- Định nghĩa hàm thích nghi (fitness): $\text{fitness} = \text{fuel\_t}$ cho tuyến khả thi; tuyến vi phạm điều kiện ràng buộc cứng có $\text{fitness} = \text{None}$.

---

## PHẦN 3: KẾT QUẢ THU ĐƯỢC THẬT CHI TIẾT (EMPIRICAL RESULTS)

### 1. Bảng So sánh Kết quả Đánh giá 3 Tuyến Thủ công
Toàn bộ 3 tuyến được đánh giá bằng cùng một hàm `evaluate_route()` với kịch bản xuất phát `2024-10-10T00:00:00Z`:

| Tuyến | Tên tuyến | Khoảng cách (NM) | Thời gian (giờ) | Nhiên liệu (tấn) | $\text{CO}_2$ ước tính (tấn) | Khả thi | Vi phạm cứng | Vi phạm mềm | Fitness | Ghi chú kết quả |
|:---:|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---|
| **R01** | Coastal baseline candidate | 779.602 | 62.689 | 59.555 | 185.453 | **CÓ** | 0 | 0 | **59.555** | Tuyến thử khả thi; chưa phải tuyến tối ưu. |
| **R02** | Deliberate land-crossing test | 631.375 | 52.372 | 49.753 | 154.932 | **KHÔNG** | 91 | 0 | **—** | Tuyến thử không khả thi; không dùng để so sánh lợi ích. |
| **R03** | Offshore alternative candidate | 822.731 | 68.036 | 64.634 | 201.271 | **CÓ** | 0 | 1 | **64.634** | Tuyến thử khả thi; chưa phải tuyến tối ưu. |

### 2. Phân tích Chi tiết Kết quả Từng Tuyến
1. **Tuyến R01 (Coastal baseline candidate – Tuyến ven bờ):**
   - Chiều dài: **779.602 NM**, Thời gian hành trình: **62.689 giờ** (~2.61 ngày).
   - Tiêu thụ nhiên liệu: **59.555 tấn**, Ước tính $\text{CO}_2$: **185.453 tấn**.
   - Trạng thái: **Khả thi (Feasible = True)**, không có vi phạm cứng hay mềm. Đóng vai trò là tuyến cơ sở tham chiếu (baseline candidate) cho STEP 2.
2. **Tuyến R02 (Deliberate land-crossing test – Tuyến kiểm thử cắt đất):**
   - Chiều dài: 631.375 NM, Thời gian tính toán: 52.372 giờ, Nhiên liệu: 49.753 tấn.
   - Trạng thái: **Không khả thi (Feasible = False)**, bị từ chối với **91 vi phạm cứng** (1 vi phạm `LAND_CROSSING` do cắt qua đất liền miền Trung và 90 vi phạm `MANDATORY_WEATHER_INVALID` do toạ độ trên đất không có dữ liệu biển).
   - Fitness: **None** (loại bỏ khỏi so sánh, không dùng số liệu này để suy diễn tiết kiệm).
3. **Tuyến R03 (Offshore alternative candidate – Tuyến ngoài khơi):**
   - Chiều dài: **822.731 NM**, Thời gian hành trình: **68.036 giờ** (~2.83 ngày).
   - Tiêu thụ nhiên liệu: **64.634 tấn**, Ước tính $\text{CO}_2$: **201.271 tấn**.
   - Trạng thái: **Khả thi (Feasible = True)**, ghi nhận **1 vi phạm mềm** `EXCESSIVE_DETOUR` do chiều dài vượt ngưỡng 1.05 lần tuyến tham chiếu R01 ($822.731 / 779.602 = 1.0553 > 1.05$).

### 3. Đối chiếu Tính tay (Hand Calculation Validation)
- **Trường hợp kiểm thử 100 NM ngoài biển:** Khoảng cách $D = 100.0\text{ NM}$, Tốc độ $V = 10.0\text{ kn}$, Công suất $P = 1,000\text{ kW}$, $\text{SFOC} = 200\text{ g/kWh}$, $C_F = 3.114\text{ tCO}_2/\text{t-fuel}$.
  * Thời gian: $T = 100.0 / 10.0 = 10.000\text{ giờ}$.
  * Nhiên liệu: $Fuel = 1,000 \times 200 \times 10.0 / 1,000,000 = 2.000\text{ tấn}$.
  * $\text{CO}_2$: $CO_2 = 2.000 \times 3.114 = 6.228\text{ tấn}$.
- **Kết quả từ bộ test `test_evaluator.py::test_vi_du_tinh_tay_100_nm`:** Khớp chính xác $100\%$ với sai số tuyệt đối $< 10^{-6}$.

---

## PHẦN 4: ĐÁNH GIÁ CHUYÊN SÂU STEP 5
Mục tiêu STEP 5 trong kế hoạch: *'Chạy kiểm thử, xuất bản đồ/kết quả và hoàn thiện báo cáo'*. Nhóm đã hoàn thành xuất sắc:

### 1. Kết quả Chạy Bộ Kiểm thử Toàn diện (Pytest)
- **Tổng số test cases:** **36 / 36 PASSED** (Thời gian chạy: ~35.8s).
- **Yêu cầu của STEP 2:** Tối thiểu $\ge 10$ tests. Thực tế đạt: **36 tests** (vượt yêu cầu $360\%$).
- **Phân bổ các nhóm kiểm thử:**
  * `test_route_geometry.py` (10 tests): Kiểm tra 3 tuyến, toạ độ WGS84, chia đoạn $\le 5$ NM, kiểm tra cắt đất.
  * `test_weather.py` (5 tests): Kiểm tra truy vấn biển, ngoài biên không gian, ngoài biên thời gian, ô missing.
  * `test_constraints.py` (6 tests): Kiểm tra phân loại vi phạm hard/soft, cắt đất, đường vòng, thiếu dữ liệu.
  * `test_evaluator.py` (9 tests): Tính tay, tính tất định, từ chối cắt đất, dòng chảy thuận/nghịch, kiểm tra đơn vị.
  * `test_result_table.py` (2 tests): Giữ nguyên tuyến infeasible, không tuyên bố tối ưu sớm.
  * `test_ai_agent_reviewer.py` (3 tests): Kiểm định cấu trúc thư mục, vòng lặp mô phỏng và 16 tiêu chí.
- **Minh chứng nhật ký:** Đã lưu tại `outputs/test_results.txt`.

### 2. Danh mục Sản phẩm Đầu ra Hoàn chỉnh
1. `outputs/maps/map_domain.png`: Bản đồ miền bao dữ liệu khí tượng và 2 điểm tiếp cận cảng.
2. `outputs/maps/manual_routes.png`: Bản đồ trực quan hóa 3 tuyến thủ công R01, R02, R03 trên nền địa hình.
3. `outputs/tables/route_results.csv`: Bảng số liệu tổng hợp định dạng CSV dùng cho phân tích số học.
4. `outputs/tables/route_results.png`: Hình bảng số liệu định dạng PNG độ phân giải cao phục vụ chèn vào tài liệu.
5. `outputs/evaluation_results.json`: Báo cáo JSON chi tiết từng segment, từng interval, và tham số mô hình.
6. `outputs/data_audit.json` & `outputs/data_audit_table.png`: Bảng kiểm toán kích thước và độ toàn vẹn của 4 tệp dữ liệu.
7. `reports/ai_agent_reviewer_report.md` & `reports/ai_agent_progress_report.md`: Báo cáo thẩm định độc lập và báo cáo tiến độ chi tiết.

### 3. Bảng Tự Đánh giá 16 Tiêu chí Nghiệm thu STEP 2 (Mục K Báo cáo)

| STT | Tiêu chí nghiệm thu STEP 2 | Kết quả | Minh chứng kỹ thuật |
|:---:|---|:---:|---|
| **01** | Khóa cặp cảng, departure UTC, phạm vi thời tiết, tàu mẫu | **☑ ĐẠT** | `config/scenario.yaml`, `config/ship.json` |
| **02** | Tải và mở được file thời tiết thật và bộ land polygon | **☑ ĐẠT** | `data/processed/*.nc`, `data/land/`, `screenshots/` |
| **03** | Có source_register đầy đủ metadata, URL, version, units | **☑ ĐẠT** | `data/source_register.csv` |
| **04** | Có `weather_at()` xử lý missing/out-of-range minh bạch | **☑ ĐẠT** | `src/weather.py` |
| **05** | Biểu diễn được ít nhất 03 tuyến thủ công dạng waypoint | **☑ ĐẠT** | `data/routes/manual_routes.json` |
| **06** | Tính khoảng cách geodesic NM, kiểm tra theo segment | **☑ ĐẠT** | `src/route_geometry.py` |
| **07** | Phân loại đúng hard/soft constraints, vi phạm có ý nghĩa | **☑ ĐẠT** | `src/constraints.py` |
| **08** | Thông số tàu + SFOC/CF ghi rõ nguồn hoặc giả định rõ ràng | **☑ ĐẠT** | `config/ship.json` (`model_assumption`) |
| **09** | `evaluate_route()` tất định, ổn định, phân rã segment | **☑ ĐẠT** | `src/evaluator.py` |
| **10** | Tính time, fuel, CO2 có kiểm tra đơn vị chặt chẽ | **☑ ĐẠT** | `src/evaluator.py` |
| **11** | Baseline không gọi Rhumb Line là ngắn nhất; dùng chung evaluator | **☑ ĐẠT** | Kịch bản khóa R01 làm baseline thủ công |
| **12** | Có >= 10 tests gồm thiếu dữ liệu & cắt đất; lưu kết quả | **☑ ĐẠT** | **36 tests PASS**, lưu `outputs/test_results.txt` |
| **13** | Có ví dụ tính tay 100 NM và đối chiếu bằng code | **☑ ĐẠT** | `tests/test_evaluator.py::test_vi_du_tinh_tay_100_nm` |
| **14** | Có bản đồ 3 tuyến và bảng kết quả không suy diễn tiết kiệm | **☑ ĐẠT** | `outputs/maps/manual_routes.png`, `outputs/tables/route_results.csv` |
| **15** | Có README, cấu trúc dự án, hướng dẫn chạy và nêu giới hạn | **☑ ĐẠT** | `README.md`, `reports/scenario_decisions.md` |
| **16** | Đủ minh chứng giải thích luồng dữ liệu và lỗi minh họa | **☑ ĐẠT** | Biểu mẫu docx, báo cáo, nhật ký kiểm thử |

---

## PHẦN 5: KẾT LUẬN VÀ KIẾN NGHỊ CHUYỂN BƯỚC (STEP 3)
1. **Đánh giá chung:** Toàn bộ mục tiêu kỹ thuật của STEP 2 đã hoàn thành trọn vẹn, vượt chỉ tiêu về số lượng kiểm thử và độ hoàn thiện dữ liệu.
2. **Đề nghị của nhóm:** Chính thức đề nghị nghiệm thu hoàn thành **STEP 2** và chuyển giao hàm `evaluate_route()` sang **STEP 3** để phục vụ việc tối ưu hóa lộ trình bằng thuật toán lai Crayfish–RIME.
