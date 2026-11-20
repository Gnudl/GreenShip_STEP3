# GreenShip – Hệ Thống Tối Ưu Lộ Trình Hàng Hải Xanh Thích Ứng Thời Tiết

> **Đề tài NCKH Sinh viên:** Tối ưu lộ trình hàng hải xanh thích ứng thời tiết sử dụng thuật toán lai Crayfish–RIME  
> **Nhóm thực hiện (Nhóm Hải Thần):**
> - **Đặng Long Ngũ** (Trưởng nhóm – Kiến trúc hệ thống, Mô hình đánh giá `evaluator.py`, Tích hợp thuật toán)
> - **Nguyễn Trần Như Nguyệt** (Xử lý dữ liệu khí tượng hải văn NetCDF, Mô hình thời tiết `weather.py`, Thuật toán COA)
> - **Nguyễn Phương Thùy** (Mô hình hình học & Ràng buộc an toàn hàng hải `constraints.py`, Thuật toán RIME, Kiểm thử Benchmark)

---

## 📌 Giới thiệu Dự án

Dự án **GreenShip** hướng tới giải quyết bài toán tối ưu hóa đa mục tiêu trong vận tải biển: **giảm thiểu tiêu thụ nhiên liệu**, **cắt giảm phát thải khí nhà kính (CO₂)** và **bảo đảm an toàn tuyệt đối** trước các điều kiện sóng gió khắc nghiệt bằng cách ứng dụng thuật toán tối ưu hóa thông minh bầy đàn (Bio-inspired & Physics-based Metaheuristics).

Dự án được chia theo các giai đoạn nghiên cứu khoa học nghiêm ngặt:
- **STEP 1 & STEP 2:** Chuẩn hóa dữ liệu viễn thám thực địa (ERA5 gió/sóng, CMEMS dòng chảy, Natural Earth đất liền) và xây dựng bộ đánh giá lộ trình độc lập (`evaluate_route()`).
- **STEP 3:** Tái hiện nguyên bản, kiểm chứng toán học độc lập hai thuật toán **COA (Crayfish Optimization Algorithm)** và **RIME (Physics-based Rime Ice Algorithm)** trên các hàm benchmark chuẩn; chuẩn hóa giao diện tối ưu hóa thống nhất.
- **STEP 4 & Kế tiếp:** Thiết kế giải thuật lai **Crayfish–RIME (Hybrid)**, tích hợp adapter với bài toán hải trình tàu biển thực tế.

---

## 📂 Cấu trúc Thư mục Dự án Chuẩn hóa

```text
GreenShip/
├── benchmarks/              # Các hàm tối ưu chuẩn toán học (Sphere, Rastrigin, Rosenbrock)
│   ├── __init__.py
│   └── functions.py
├── config/                  # Cấu hình kịch bản mô phỏng và thông số tàu
│   ├── scenario.yaml        # Kịch bản hải trình & tọa độ cảng
│   ├── step2_scenario.yaml  # Kịch bản STEP 2 đã khóa
│   └── ship.json            # Thông số kỹ thuật tàu mẫu (DWT, SFOC, Power)
├── data/                    # Dữ liệu khí tượng hải văn và mã nguồn gốc
│   ├── raw/                 # Dữ liệu gốc NetCDF ERA5/CMEMS & mã nguồn gốc COA, RIME
│   │   ├── COA/             # Mã nguồn MATLAB nguyên bản Jia et al. (2023)
│   │   └── RIME/            # Mã nguồn MATLAB nguyên bản Su et al. (2023)
│   ├── processed/           # Dữ liệu thời tiết đã chuẩn hóa lưới tọa độ và thời gian
│   ├── land/                # Đa giác đường bờ và đất liền Natural Earth (ne_10m_land)
│   ├── routes/              # Các tuyến hải trình cơ sở (R01, R02, R03)
│   └── source_register.csv  # Danh mục nguồn dữ liệu & điều kiện bản quyền
├── outputs/                 # Kết quả thực nghiệm và trực quan hóa
│   ├── step2/               # Bảng biểu kiểm toán dữ liệu và đánh giá tuyến STEP 2
│   ├── step3/               # Dữ liệu thống kê benchmark CSV và biểu đồ hội tụ
│   ├── maps/                # Bản đồ trực quan hóa hải trình và trường sóng gió
│   └── tables/              # Bảng tổng hợp so sánh các chỉ số tiêu thụ/phát thải
├── reports/                 # Báo cáo khoa học và tài liệu nghiệm thu
│   ├── step3/               # Báo cáo chính thức Word STEP 3 (Nhóm Hải Thần)
│   └── screenshots/         # Ảnh chụp bằng chứng kiểm thử thực tế
├── scripts/                 # Kịch bản thực thi và công cụ hỗ trợ
│   ├── run_benchmarks.py    # Script chạy ma trận 3 hàm x 2 thuật toán x 10 seeds
│   └── tools/               # Các công cụ tạo báo cáo và tiền xử lý
├── src/                     # Mã nguồn lõi của hệ thống
│   ├── evaluator.py         # Hàm đánh giá lộ trình (tiêu hao nhiên liệu, thời gian, phạt an toàn)
│   ├── weather.py           # Động cơ nội suy thời tiết thời gian thực
│   ├── constraints.py       # Kiểm tra an toàn sóng gió và tránh cạn đất liền
│   ├── route_geometry.py    # Tính toán trắc địa học (Great Circle, khoảng cách, hải lý)
│   └── optimizers/          # Các thuật toán tối ưu hóa độc lập
│       ├── common.py        # Giao diện optimize(...) chung & bộ đếm FE
│       ├── coa.py           # Thuật toán COA nguyên bản (Jia et al., 2023)
│       └── rime.py          # Thuật toán RIME nguyên bản (Su et al., 2023)
├── tests/                   # Bộ kiểm thử tự động (Pytest Unit Tests)
│   ├── test_benchmarks.py   # Kiểm thử giá trị chuẩn các hàm toán học
│   ├── test_coa.py          # Kiểm thử toán tử và tính tất định của COA
│   ├── test_rime.py         # Kiểm thử toán tử và tính tất định của RIME
│   ├── test_step2_regression.py # Kiểm thử hồi quy mô hình tàu và ETA
│   └── test_*.py            # Các kiểm thử hình học, thời tiết và ràng buộc
├── conftest.py              # Cấu hình môi trường pytest
├── pytest.ini               # Cấu hình đường dẫn module kiểm thử
├── requirements.txt         # Danh mục thư viện Python yêu cầu
└── README.md                # Tài liệu hướng dẫn dự án
```

---

## 🚀 Hướng dẫn Cài đặt & Chạy Thực nghiệm

### 1. Yêu cầu Môi trường
- **Hệ điều hành:** Windows 10/11, Linux hoặc macOS.
- **Python:** Phiên bản 3.10 trở lên.

### 2. Cài đặt Thư viện
Mở Terminal/PowerShell tại thư mục gốc dự án và cài đặt:
```bash
pip install -r requirements.txt
```

### 3. Chạy Toàn bộ Kiểm thử Tự động (Unit Tests)
Dự án được bảo vệ nghiêm ngặt bằng bộ 13 ca kiểm thử tự động độc lập:
```bash
pytest tests/ -v
```
*Kết quả chuẩn: 13/13 ca kiểm thử PASSED hoàn toàn.*

### 4. Chạy Thực nghiệm So sánh Benchmark COA và RIME (STEP 3)
Chạy kịch bản ma trận 3 hàm ($\text{Sphere, Rastrigin, Rosenbrock}$) $\times$ 2 thuật toán ($\text{COA, RIME}$) $\times$ 10 random seeds ($\text{max\_fe}=3.000$):
```bash
python scripts/run_benchmarks.py
```
Kết quả thống kê `mean`, `std`, `min`, `median`, `max` và biểu đồ đường cong hội tụ sẽ được tự động xuất ra thư mục `outputs/step3/`.

---

## 📊 Tóm tắt Thuật toán (COA & RIME)

### 1. Thuật toán COA (Crayfish Optimization Algorithm)
* **Tác giả:** Heming Jia, Honghua Rao, Changsheng Wen, Seyedali Mirjalili (*Artificial Intelligence Review*, Springer, 2023).
* **Bản chất:** Mô phỏng sinh thái tôm hùm đất điều tiết theo nhiệt độ mô phỏng $temp \in [20, 35]^\circ\text{C}$:
  - **Trời nóng ($temp > 30^\circ\text{C}$):** Tránh nóng vào hang hoặc cạnh tranh giành hang $\to$ **Thăm dò diện rộng (Exploration)**.
  - **Trời mát ($temp \le 30^\circ\text{C}$):** Kiếm ăn (tiến tới gắp mồi nhỏ hoặc xé mồi lớn bằng hàm lượng giác) $\to$ **Khai thác sâu (Exploitation)**.

### 2. Thuật toán RIME (Physics-based Rime Ice Optimization)
* **Tác giả:** Hang Su, Dong Zhao, Ali Asghar Heidari et al. (*Neurocomputing*, Elsevier, 2023).
* **Bản chất:** Mô phỏng vật lý quá trình hình thành băng sương giá trong tự nhiên:
  - **Chiến lược sương mềm (Soft-rime):** Gió nhẹ, ngưng tụ tự do $\to$ Thăm dò toàn cục.
  - **Cơ chế xuyên thấu sương cứng (Hard-rime):** Gió mạnh, đâm xuyên và thay thế tọa độ hạt kém $\to$ Khai thác cục bộ & Crossover.
  - **Chọn lọc tham lam tích cực (Positive-greedy):** Giữ vững nghiệm tối ưu, ngăn chặn thoái hóa.

---

## 📜 Bản quyền & Trích dẫn Khoa học

Dự án phục vụ mục đích nghiên cứu khoa học sinh viên tại Trường Đại học Công Thương TP. Hồ Chí Minh (HUIT).
Mọi thuật toán và bộ dữ liệu viễn thám tuân thủ giấy phép mã nguồn mở và chính sách trích dẫn quốc tế (ECMWF ERA5, Copernicus Marine Service, Natural Earth Data).
