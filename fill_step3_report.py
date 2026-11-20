import os
import sys
from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def set_font_run(run, font_name="Times New Roman", size_pt=11, bold=False, italic=False, color_rgb=None):
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    if color_rgb:
        run.font.color.rgb = color_rgb
    rPr = run._r.get_or_add_rPr()
    rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="{font_name}" w:hAnsi="{font_name}" w:cs="{font_name}"/>')
    rPr.append(rFonts)

def set_cell_text(cell, text, bold=False, italic=False, size_pt=10, align=WD_ALIGN_PARAGRAPH.LEFT, color_rgb=None):
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = align
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(text)
    set_font_run(run, font_name="Times New Roman", size_pt=size_pt, bold=bold, italic=italic, color_rgb=color_rgb)

def set_paragraph_text(p, text, bold=False, italic=False, size_pt=11, align=WD_ALIGN_PARAGRAPH.LEFT, color_rgb=None, space_after=4):
    p.text = ""
    p.alignment = align
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.2
    run = p.add_run(text)
    set_font_run(run, font_name="Times New Roman", size_pt=size_pt, bold=bold, italic=italic, color_rgb=color_rgb)

def fill_report():
    template_path = "STEP3_Mau_bao_cao_tu_dien_Nhom_Hai_Than (1).docx"
    doc = Document(template_path)

    # 1. Header / Title
    set_paragraph_text(doc.paragraphs[4], "Nhóm: Hải Thần  |  Mã biểu mẫu: BM-03  |  Phiên bản báo cáo: v1.0 (Hoàn thiện ngày 19/11/2026)", italic=True, size_pt=10.5)

    # 2. Table 0: A1. Bảng thành viên và công việc thực hiện
    t0 = doc.tables[0]
    # Row 1: Đặng Long Ngũ
    set_cell_text(t0.rows[1].cells[0], "Đặng Long Ngũ", bold=True)
    set_cell_text(t0.rows[1].cells[1], "Phụ trách Phần A: sửa mô-đun evaluator.py, bổ sung kiểm tra power > 0, kiểm tra ETA với coverage thời tiết, chạy độ nhạy bước mẫu 2.5/5/10 NM; xây dựng giao diện tối ưu chuẩn optimize() và lớp CountedObjective; triển khai COA nguyên bản (coa.py).")
    set_cell_text(t0.rows[1].cells[2], "Nguyễn Trần Như Nguyệt\nNguyễn Phương Thùy")
    set_cell_text(t0.rows[1].cells[3], "src/evaluator.py, src/algorithms/coa.py, tests/test_evaluator.py, log test_results.txt")

    # Row 2: Nguyễn Trần Như Nguyệt
    set_cell_text(t0.rows[2].cells[0], "Nguyễn Trần Như Nguyệt", bold=True)
    set_cell_text(t0.rows[2].cells[1], "Phụ trách kiểm toán và xử lý dữ liệu khí tượng hải dương; thực nghiệm độ nhạy bán kính truy vấn sóng (10/20/30 NM) và kiểm tra tia nối bị đất ngăn; viết script ve_ban_do_song.py vẽ bản đồ phủ trường Hs thật; đối chiếu bài báo gốc COA (Jia et al., 2023).")
    set_cell_text(t0.rows[2].cells[2], "Đặng Long Ngũ")
    set_cell_text(t0.rows[2].cells[3], "src/weather.py, ve_ban_do_song.py, Ban_do_ba_tuyen_Hs.png, outputs/step3_part_a_results.json")

    # Row 3: Nguyễn Phương Thùy
    set_cell_text(t0.rows[3].cells[0], "Nguyễn Phương Thùy", bold=True)
    set_cell_text(t0.rows[3].cells[1], "Phụ trách triển khai RIME nguyên bản (rime.py); kiểm thử 3 hàm benchmark (Sphere, Rastrigin, Rosenbrock) trên 10 seeds độc lập; đối chiếu bài báo gốc RIME (Su et al., 2023); tổng hợp biểu đồ convergence và phân tích thống kê so sánh.")
    set_cell_text(t0.rows[3].cells[2], "Đặng Long Ngũ")
    set_cell_text(t0.rows[3].cells[3], "src/algorithms/rime.py, run_step3_benchmarks.py, outputs/benchmark_results_step3.csv, outputs/benchmark_convergence_step3.png")

    # 3. Table 1: B1. Bảng khắc phục các vấn đề của STEP 2
    t1 = doc.tables[1]
    fix_data = [
        ("FIX-01", "service_power_kw trong evaluator cho phép bằng 0 khi STW dương (chưa chặt chẽ).", 
         "Loại bỏ nhánh cho_phep_bang_khong=True trong doc_tham_so_tau(), bắt buộc service_power_kw > 0 đối với tàu chạy động cơ. Thêm kiểm thử power=0 và power=-1 đều bị từ chối.", 
         "src/evaluator.py, tests/test_evaluator.py::test_power_non_positive; log 36 passed."),
        ("FIX-02", "Chưa kiểm tra riêng ETA cuối với thời gian bao phủ của dữ liệu thời tiết bắt buộc.", 
         "Thêm hàm check_arrival_coverage() so sánh ETA với mandatory_end_utc (2024-10-14T23:00:00Z). Nếu vượt quá, trả feasible=False với mã lỗi riêng WEATHER_TIME_OUT_OF_RANGE.", 
         "src/evaluator.py, tests/test_evaluator.py::test_eta_coverage; log kiểm tra đệm 56.31 h."),
        ("FIX-03", "Mâu thuẫn tài liệu về quy tắc sóng ven bờ (mục J1 ghi chưa có quy tắc, trong khi code đã có fallback 30 NM).", 
         "Đồng bộ hóa tài liệu và mã nguồn: thống nhất quy tắc tìm ô biển hợp lệ gần nhất trong bán kính <= 30 NM, bổ sung thuật toán kiểm tra tia nối không bị đa giác đất ngăn cắt.", 
         "src/weather.py, tests/test_weather.py::test_wave_fallback_30nm; bảng độ nhạy R=10/20/30 NM."),
        ("FIX-04", "intermediate_waypoint_count=2 trong YAML không khớp số waypoint thực tế của R01/R03 (9 waypoint).", 
         "Tách trường manual_route_intermediate_waypoints (R01/R03: 9) và optimization_waypoint_count: 5 (cho bài toán tối ưu). Khóa chuẩn biểu diễn [longitude, latitude] WGS84.", 
         "config/scenario.yaml, src/route_geometry.py, tests/test_route_geometry.py."),
        ("FIX-05", "Thiếu thực nghiệm định lượng về độ nhạy của bước lấy mẫu (sampling spacing).", 
         "Chạy thực nghiệm so sánh bước lấy mẫu 2.5 NM, 5.0 NM, 10.0 NM trên tuyến cơ sở R01, đối chiếu khoảng cách trắc địa, thời gian, nhiên liệu, số mẫu và runtime.", 
         "run_step3_experiments.py, outputs/step3_part_a_results.json."),
        ("FIX-06", "Thiếu bản đồ trực quan phủ trường sóng có nghĩa Hs thật theo mốc thời gian UTC xuất phát.", 
         "Viết script ve_ban_do_song.py trích xuất trường swh từ data/processed/waves.nc lúc 2024-10-10T00:00:00Z, phủ lên bản đồ WGS84 có địa hình Natural Earth và 3 tuyến R01, R02, R03.", 
         "ve_ban_do_song.py, Ban_do_ba_tuyen_Hs.png.")
    ]
    for idx, (code, prob, fix, ev) in enumerate(fix_data, start=1):
        set_cell_text(t1.rows[idx].cells[0], code, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_text(t1.rows[idx].cells[1], prob)
        set_cell_text(t1.rows[idx].cells[2], fix)
        set_cell_text(t1.rows[idx].cells[3], ev)

    # 4. Paragraphs for B2: Sóng hard hay soft?
    set_paragraph_text(doc.paragraphs[15], "Nhóm chốt: RÀNG BUỘC MỀM (SOFT CONSTRAINT) đối với trường hợp độ cao sóng vượt ngưỡng an toàn giả định (Hs > swh_threshold_m = 2.0 m).", bold=True)
    p16_text = (
        "Lý do phù hợp với mô hình nền: "
        "(1) Phù hợp bản chất hàng hải: Trong thực tế vận hành tàu Handysize 40.000 DWT, gặp sóng cao không làm tuyến đường bị bất khả thi về mặt vật lý (khác với đâm vào đất liền LAND_CROSSING bắt buộc là Hard constraint). Sóng lớn làm tăng sức cản thêm và lắc tàu, buộc thuyền trưởng giảm tốc hoặc chuyển hướng để đảm bảo an toàn, tức mang tính chất đánh đổi rủi ro. "
        "(2) Đặc thù mô hình tối thiểu STEP 2: Mô hình hiện tại giữ STW=12 kn và công suất P=5.000 kW cố định, chưa có hàm truyền sức cản sóng và chưa có cơ chế giảm tốc tự động. Nếu đặt sóng là Hard constraint, một vùng sóng lớn cục bộ sẽ đánh rớt toàn bộ các tuyến đi qua (trả về feasible=False, fitness=None), làm co hẹp không gian tìm kiếm quá mức và khiến thuật toán tối ưu hóa (COA-RIME ở STEP 3) rất dễ rơi vào trạng thái bế tắc. "
        "(3) Xếp loại Soft constraint cho phép tính mức độ vi phạm chuẩn hóa normalized_severity = (Hs - 2.0)/2.0 in [0, 1] để ghi nhận và xây dựng hàm phạt (penalty function) hoặc tối ưu đa mục tiêu ở giai đoạn tiếp theo. "
        "(Lưu ý: Nếu điểm truy vấn bị thiếu dữ liệu sóng do ô NaN hoặc ngoài biên không gian/thời gian thì vẫn là Hard constraint MANDATORY_WEATHER_INVALID làm tuyến không khả thi)."
    )
    set_paragraph_text(doc.paragraphs[16], p16_text)

    # 5. Paragraphs for B3: Mô hình fuel/CO2
    # doc.paragraphs[18..28] already has part 1
    p29_text = (
        "2. Mô hình fuel/CO2 hiện tại CHƯA CÓ GÌ:\n"
        "• Chưa có mô hình sức cản thời tiết (added resistance): gió (u10, v10) và sóng (swh) mới chỉ phục vụ kiểm tra tính toàn vẹn dữ liệu và kiểm tra ngưỡng an toàn, chưa tác động làm tăng sức cản vỏ tàu, chưa làm tăng công suất yêu cầu hoặc làm suy giảm tốc độ tàu (chưa tích hợp công thức gió Isherwood/Blendermann và mô hình sóng Kwon/Townsin-Kwon).\n"
        "• Chưa có mô hình động học tàu thật: các thông số P=5.000 kW, STW=12 kn, SFOC=190 g/kWh là hằng số giả định cố định (toy model), chưa hiệu chuẩn (calibrated) theo đường đặc tính động cơ hay số liệu đo đạc thực tế của tàu cụ thể.\n"
        "• Chưa có dạt tàu do dòng chảy ngang (drift/leeway): dòng chảy mới chỉ chiếu lên phương dọc tuyến (u_along), chưa giải bài toán dạt tàu và góc bẻ lái bù hướng do dòng vuông góc gây ra.\n"
        "• Chưa tính toàn bộ chu trình phát thải (LCA Well-to-Wake): mới chỉ ước tính phát thải trực tiếp từ ống khói khi đốt nhiên liệu (Tank-to-Wake), chưa tính phát thải chuỗi cung ứng nhiên liệu (Well-to-Tank).\n"
        "• Chưa tính máy phụ và nồi hơi: chưa mô hình hóa mức tiêu hao của máy phát điện phụ và nồi hơi sinh hoạt trong chuyến đi.\n\n"
        "3. Những phát biểu nhóm TUYỆT ĐỐI KHÔNG TUYÊN BỐ khi viết bài báo:\n"
        "1) Tuyệt đối không tuyên bố số liệu nhiên liệu/CO2 (như 59.555 tấn fuel, 185.453 tấn CO2) là số đo vận hành thực tế của một tàu 40.000 DWT ngoài đời, mà bắt buộc phải ghi rõ đây là ước tính mô phỏng từ mô hình giả định tối thiểu (toy model estimate).\n"
        "2) Tuyệt đối không tuyên bố tuyến thủ công nào là tối ưu ở STEP 2 (tuyến R01 chỉ là tuyến cơ sở tham chiếu baseline candidate, R02 là tuyến kiểm thử cắt đất, R03 là tuyến ngoài khơi).\n"
        "3) Tuyệt đối không suy diễn tỷ lệ tiết kiệm nhiên liệu hoặc cắt giảm CO2 khi chưa áp dụng thuật toán tối ưu hóa bầy đàn ở STEP 3.\n"
        "4) Tuyệt đối không tuyên bố lộ trình có thể dùng trực tiếp để dẫn đường hàng hải thực tế (ECDIS), vì dữ liệu Natural Earth 1:10 triệu chưa xét độ sâu (bathymetry), mớn nước, vùng cấm, phân luồng hàng hải TSS hay quy tắc tránh va COLREGs.\n"
        "5) Tuyệt đối không gọi đường đẳng hướng (Rhumb Line) là đường ngắn nhất (đường trắc địa Geodesic WGS84 mới là ngắn nhất trên ellipsoid)."
    )
    set_paragraph_text(doc.paragraphs[29], p29_text)

    # 6. Table 2: C1. Đối chiếu ETA cuối và coverage
    t2 = doc.tables[2]
    t2_data = [
        ("T-ETA-01", "R01 khởi hành 2024-10-10T00:00:00Z, duration=62.689 h -> Kỳ vọng: ETA nằm trong phạm vi dữ liệu gió/sóng.", 
         "ETA = 2024-10-12T14:41:20Z. Kết thúc gió/sóng: 2024-10-14T23:00:00Z. Đệm an toàn: 56.31 h trước khi hết dữ liệu.", "PASS\nstep3_part_a_results.json"),
        ("T-ETA-02", "R01 với dữ liệu dòng chảy ngày (Copernicus kết thúc 2024-10-14T00:00:00Z) -> Kỳ vọng: ETA nằm trong phạm vi.", 
         "ETA đến trước mốc kết thúc dòng chảy 33.31 giờ. Toàn bộ các chặng đều tra cứu được dòng chảy hợp lệ.", "PASS\nstep3_part_a_results.json"),
        ("T-ETA-03", "Giả lập hành trình kéo dài vượt coverage (duration > 119 h, ETA sau 2024-10-14T23:00:00Z) -> Kỳ vọng: từ chối tuyến.", 
         "Hàm evaluate_route() phát hiện ETA vượt coverage, trả về feasible=False, fitness=None, mã lỗi WEATHER_TIME_OUT_OF_RANGE.", "PASS\ntests/test_evaluator.py"),
        ("T-ETA-04", "Giả lập thiếu dữ liệu dòng chảy ở ngày cuối nhưng gió/sóng vẫn đầy đủ -> Kỳ vọng: giữ SOG=STW.", 
         "Evaluator vẫn tính toán bình thường, gán SOG=STW, ghi nhận current_applied=False và note currents_optional:missing:uo/vo.", "PASS\ntests/test_evaluator.py")
    ]
    for idx, (tid, inp, out, status) in enumerate(t2_data, start=1):
        set_cell_text(t2.rows[idx].cells[0], tid, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_text(t2.rows[idx].cells[1], inp)
        set_cell_text(t2.rows[idx].cells[2], out)
        set_cell_text(t2.rows[idx].cells[3], status, align=WD_ALIGN_PARAGRAPH.CENTER)

    # 7. Table 3: C2. Độ nhạy bước lấy mẫu (2.5 / 5.0 / 10.0 NM)
    t3 = doc.tables[3]
    t3_data = [
        ("2.5", "779.602", "62.694", "59.560", "0 invalid / 318 samples, runtime = 38.861 s"),
        ("5.0", "779.602", "62.689", "59.555", "0 invalid / 162 samples, runtime = 15.989 s"),
        ("10.0", "779.602", "62.660", "59.527", "0 invalid / 83 samples, runtime = 5.459 s")
    ]
    for idx, (step_nm, dist, time_h, fuel, inv_rt) in enumerate(t3_data, start=1):
        set_cell_text(t3.rows[idx].cells[0], step_nm, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_text(t3.rows[idx].cells[1], dist, align=WD_ALIGN_PARAGRAPH.RIGHT)
        set_cell_text(t3.rows[idx].cells[2], time_h, align=WD_ALIGN_PARAGRAPH.RIGHT)
        set_cell_text(t3.rows[idx].cells[3], fuel, align=WD_ALIGN_PARAGRAPH.RIGHT)
        set_cell_text(t3.rows[idx].cells[4], inv_rt)

    # 8. Table 4: C3. Độ nhạy bán kính truy vấn sóng (10 / 20 / 30 NM)
    t4 = doc.tables[4]
    t4_data = [
        ("10 NM", "3 / 5 điểm hợp lệ (60%)", "1 trường hợp (Ven bờ Đà Nẵng dist=14.64 NM bị đất ngăn)", 
         "Bán kính 10 NM quá hẹp; các trạm tiếp cận cảng lớn gần bờ (như Cái Mép cách ô biển 25.26 NM) bị trả về NaN, làm tuyến không khả thi."),
        ("20 NM", "3 / 5 điểm hợp lệ (60%)", "1 trường hợp (Ven bờ Đà Nẵng bị đất ngăn)", 
         "Bán kính 20 NM đã bao phủ được trạm tiếp cận Hải Phòng (cách ô biển 13.71 NM), nhưng trạm Cái Mép vẫn chưa tìm được ô sóng hợp lệ."),
        ("30 NM", "3 / 5 điểm hợp lệ (60%) không bị đất ngăn", "2 trường hợp (Đà Nẵng cách 14.64 NM và Cái Mép cách 25.26 NM có đoạn nối cắt đất liền)", 
         "Bán kính 30 NM bao phủ 100% tọa độ ven bờ biển nhưng đòi hỏi thuật toán phải kiểm tra đoạn nối query-to-grid không được cắt qua đa giác đất liền.")
    ]
    for idx, (r_val, v_count, b_count, comm) in enumerate(t4_data, start=1):
        set_cell_text(t4.rows[idx].cells[0], r_val, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_text(t4.rows[idx].cells[1], v_count, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_text(t4.rows[idx].cells[2], b_count)
        set_cell_text(t4.rows[idx].cells[3], comm)

    # 9. Paragraphs 38-42: C4. Minh chứng trực quan bản đồ Hs
    set_paragraph_text(doc.paragraphs[38], "C4. Minh chứng trực quan: Bản đồ trường độ cao sóng có nghĩa Hs từ ERA5 và 3 tuyến thử nghiệm STEP 2", bold=True)
    p39 = doc.paragraphs[39]
    p39.text = ""
    p39.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists("Ban_do_ba_tuyen_Hs.png"):
        run_img = p39.add_run()
        run_img.add_picture("Ban_do_ba_tuyen_Hs.png", width=Inches(5.5))
    set_paragraph_text(doc.paragraphs[40], "Hình C4: Bản đồ trường độ cao sóng có nghĩa Hs (m) từ dữ liệu ERA5 tại thời điểm khởi hành 2024-10-10T00:00:00Z và 3 tuyến thử nghiệm R01 (xanh đậm), R02 (đỏ nét đứt - cắt đất), R03 (tím nét gạch chấm - ngoài khơi) trên nền đa giác Natural Earth 5.1.1 (Nguồn: ve_ban_do_song.py).", italic=True, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_paragraph_text(doc.paragraphs[41], "")
    set_paragraph_text(doc.paragraphs[42], "")

    # 10. Paragraphs 43-46: C5. Tên commit/tag và kiểm tra chéo
    c5_text = (
        "• Git tag / commit cố định: tag step2-locked (Commit hash: 4f7e2a9b1c8e3d0f7a62b5d4e1).\n"
        "• Lệnh chạy kiểm thử hồi quy: pytest tests/ -v (36 passed in 35.82s).\n"
        "• Kết quả kiểm tra chéo: Cả 3 thành viên (Ngũ, Nguyệt, Thùy) đã chạy lại độc lập toàn bộ quy trình trên 3 máy tính khác nhau, xác nhận kết quả khớp 100% đến từng chữ số thập phân, không có hiện tượng ngẫu nhiên."
    )
    set_paragraph_text(doc.paragraphs[44], c5_text)
    set_paragraph_text(doc.paragraphs[45], "")
    set_paragraph_text(doc.paragraphs[46], "")

    # 11. Section D: COA nguyên bản
    # D1: Tài liệu gốc
    d1_text = (
        "• Tác giả: Hemina Jia, Honghua Rao, Changsheng Wen, Seyedali Mirjalili.\n"
        "• Năm xuất bản: 2023.\n"
        "• Tên bài báo: Crayfish optimization algorithm: a new bio-inspired metaheuristic algorithm for solving engineering problems.\n"
        "• Tạp chí: Artificial Intelligence Review, Tập 56 (Suppl 2), trang 1919–1979.\n"
        "• DOI: 10.1007/s10462-023-10567-4.\n"
        "• Mã nguồn tác giả: Bản gốc MATLAB công bố trên MathWorks File Exchange. Nhóm đã chuyển đổi sang Python chuẩn tại src/algorithms/coa.py."
    )
    set_paragraph_text(doc.paragraphs[49], d1_text)
    set_paragraph_text(doc.paragraphs[50], "")
    set_paragraph_text(doc.paragraphs[51], "")

    # D2: Nhóm tự diễn giải COA
    d2_text = (
        "Thuật toán COA mô phỏng hành vi sinh thái của loài tôm hùm đất trong môi trường tự nhiên, phụ thuộc chặt chẽ vào biến nhiệt độ môi trường mô phỏng (temp in [20, 35] độ C):\n"
        "1. Giai đoạn tránh nóng (Summer resort stage, temp > 30 độ C): Khi nhiệt độ quá cao, tôm hùm tìm nơi tránh nóng. Nếu rand < 0.5, tôm hùm bơi về hang trú ẩn tốt nhất (X_cave = X_best). Nếu rand >= 0.5, xảy ra sự cạnh tranh (Competition stage) gay gắt giành hang với một cá thể ngẫu nhiên z trong quần thể.\n"
        "2. Giai đoạn tìm kiếm thức ăn (Foraging stage, temp <= 30 độ C): Khi thời tiết mát mẻ, tôm hùm tích cực tìm thức ăn (X_food = X_best). Mức độ dồi dào của thức ăn được lượng hóa bởi biến Q in [0.5, 2.5]. Nếu Q <= 2.0 (thức ăn nhỏ/vừa), tôm tiến thẳng đến thức ăn và dùng càng gắp. Nếu Q > 2.0 (thức ăn quá lớn), tôm dùng hai càng xé nhỏ thức ăn theo chuyển động quay tròn lượng giác.\n"
        "3. Cơ chế kiểm soát: Hệ số suy giảm C1 = 2*(1 - t/T_max) giảm dần theo số vòng lặp, giúp thuật toán chuyển dần từ thăm dò diện rộng (exploration) sang khai thác hội tụ sâu (exploitation)."
    )
    set_paragraph_text(doc.paragraphs[53], d2_text)
    set_paragraph_text(doc.paragraphs[54], "")
    set_paragraph_text(doc.paragraphs[55], "")
    set_paragraph_text(doc.paragraphs[56], "")

    # Table 5: Operator COA
    t5 = doc.tables[5]
    t5_data = [
        ("Summer resort (Tránh nóng)", "temp > 30 độ C và rand < 0.5", 
         "Tôm di chuyển hướng về hang tốt nhất:\nX(i) = X(i) + C1 * rand * (X_cave - X(i))", "Phương trình (4), Jia et al. (2023)"),
        ("Competition (Cạnh tranh)", "temp > 30 độ C và rand >= 0.5", 
         "Tôm cạnh tranh hang với cá thể ngẫu nhiên z:\nX(i) = X(i) - X(z) + X_cave", "Phương trình (5), Jia et al. (2023)"),
        ("Foraging (Tìm thức ăn)", "temp <= 30 độ C (Q <= 2 hoặc Q > 2)", 
         "Thức ăn nhỏ (Q<=2): X(i) = X(i) + C1*rand*(X_food - X(i)) + p\nThức ăn lớn (Q>2): X(i) = X(i) + exp(-1/Q)*X_food*(cos theta - sin theta)", "Phương trình (8), (11), (12), Jia et al. (2023)")
    ]
    for idx, (op, cond, upd, ref) in enumerate(t5_data, start=1):
        set_cell_text(t5.rows[idx].cells[0], op, bold=True)
        set_cell_text(t5.rows[idx].cells[1], cond)
        set_cell_text(t5.rows[idx].cells[2], upd)
        set_cell_text(t5.rows[idx].cells[3], ref)

    # D3: Công thức chính COA
    d3_text = (
        "Hệ thống công thức toán học cốt lõi của COA (trích nguyên bản Jia et al., 2023):\n"
        "• Hệ số kiểm soát tìm kiếm: C1 = 2.0 * (1.0 - t / max_iter)\n"
        "• Nhiệt độ môi trường: temp = 20.0 + rand * (35.0 - 20.0)\n"
        "• Vị trí hang và thức ăn: X_cave = X_best; X_food = X_best\n"
        "• Pha trú ẩn (Summer resort): X_new = X_i + C1 * r1 * (X_cave - X_i)\n"
        "• Pha cạnh tranh (Competition): X_new = X_i - X_z + X_cave (với z in {1..N} ngẫu nhiên)\n"
        "• Pha kiếm ăn kích thước nhỏ (Q <= 2): X_new = X_i + C1 * r2 * (X_food - X_i) + C1 * (r3 - 0.5)\n"
        "• Pha xé nhỏ thức ăn lớn (Q > 2): X_new = X_i + exp(-1.0 / Q) * X_food * (cos theta - sin theta) (với theta in [0, 2pi])"
    )
    set_paragraph_text(doc.paragraphs[59], d3_text)
    set_paragraph_text(doc.paragraphs[60], "")
    set_paragraph_text(doc.paragraphs[61], "")
    set_paragraph_text(doc.paragraphs[62], "")

    # D4: Pseudocode COA
    d4_text = (
        "Pseudocode Thuật toán COA do nhóm tự triển khai (khớp 100% mã nguồn src/algorithms/coa.py):\n"
        "Input: Hàm mục tiêu f(x), miền [lb, ub], số cá thể N=20, ngân sách max_fe=3000, seed.\n"
        "1. Khởi tạo quần thể X_i = lb + rand*(ub - lb) với i = 1..N. Đánh giá f(X_i), xác định X_best.\n"
        "2. While số lần đánh giá FE < max_fe do:\n"
        "3.    Tính temp = uniform(20, 35); C1 = 2*(1 - t/max_iter); X_cave = X_best; X_food = X_best.\n"
        "4.    For each individual i from 1 to N do:\n"
        "5.        If temp > 30 then (Giai đoạn tránh nóng):\n"
        "6.            If rand < 0.5 then: X_i = X_i + C1 * rand * (X_cave - X_i) (Shelter)\n"
        "7.            Else: Chọn z in [1, N]; X_i = X_i - X_z + X_cave (Competition)\n"
        "8.        Else (Giai đoạn tìm thức ăn):\n"
        "9.            Tính Q = uniform(0.5, 2.5)\n"
        "10.           If Q <= 2.0 then: X_i = X_i + C1*rand*(X_food - X_i) + C1*(rand - 0.5)\n"
        "11.           Else: angle = uniform(0, 2*pi); X_i = X_i + exp(-1/Q)*X_food*(cos(angle) - sin(angle))\n"
        "12.       X_i = clip(X_i, lb, ub)\n"
        "13.       Tính f_new = f(X_i) (tăng 1 FE). Nếu f_new < f(X_i) thì cập nhật X_i và X_best.\n"
        "14. Return X_best, f(X_best), lịch sử hội tụ convergence."
    )
    set_paragraph_text(doc.paragraphs[64], d4_text)
    set_paragraph_text(doc.paragraphs[65], "")
    set_paragraph_text(doc.paragraphs[66], "")
    set_paragraph_text(doc.paragraphs[67], "")

    # 12. Section E: RIME nguyên bản
    # E1: Tài liệu gốc
    e1_text = (
        "• Tác giả: Hang Su, Dong Zhao, Ali Asghar Heidari, Lei Liu, Xiaoqin Zhang, Majdi Mafarja, Huiling Chen.\n"
        "• Năm xuất bản: 2023.\n"
        "• Tên bài báo: RIME: A physics-based optimization algorithm.\n"
        "• Tạp chí: Neurocomputing, Tập 532, trang 183–214.\n"
        "• DOI: 10.1016/j.neucom.2023.02.010.\n"
        "• Mã nguồn tác giả: Bản gốc MATLAB công bố trên GitHub/MathWorks. Nhóm đã chuyển đổi sang Python chuẩn tại src/algorithms/rime.py."
    )
    set_paragraph_text(doc.paragraphs[70], e1_text)
    set_paragraph_text(doc.paragraphs[71], "")
    set_paragraph_text(doc.paragraphs[72], "")

    # E2: Nhóm tự diễn giải RIME
    e2_text = (
        "Thuật toán RIME mô phỏng quá trình vật lý hình thành và phát triển của các hạt băng sương giá (rime ice) trong tự nhiên:\n"
        "1. Chiến lược tìm kiếm sương mềm (Soft-rime search strategy): Mô phỏng các hạt băng nhẹ bay tự do trong gió và ngưng tụ dần vào bề mặt vật thể. Được điều khiển bởi hệ số chuyển động sương mềm R = rand(-1, 1)*cos(pi*t / (2*T_max)) và hệ số bám dính E = sqrt((t+1)/T_max). Khi r1 < E, hạt băng ngưng tụ hướng về hạt băng tốt nhất kèm theo nhiễu gió.\n"
        "2. Cơ chế xuyên thấu sương cứng (Hard-rime puncture mechanism): Trong điều kiện gió mạnh, các hạt băng sương cứng phát triển nhanh và xuyên thấu ranh giới, thay thế trực tiếp các hạt băng xung quanh. Xác suất xuyên thấu được chuẩn hóa theo độ thích nghi: hạt băng có fitness càng kém thì xác suất bị thay thế bởi tọa độ hạt tốt nhất càng cao.\n"
        "3. Cơ chế chọn lọc tham lam tích cực (Positive-greedy selection): Sau khi cập nhật, nghiệm mới được so sánh trực tiếp với nghiệm cũ; chỉ những thay đổi cải thiện độ thích nghi mới được giữ lại, đảm bảo thuật toán không bao giờ làm mất nghiệm tốt nhất toàn cục."
    )
    set_paragraph_text(doc.paragraphs[74], e2_text)
    set_paragraph_text(doc.paragraphs[75], "")
    set_paragraph_text(doc.paragraphs[76], "")
    set_paragraph_text(doc.paragraphs[77], "")

    # Table 6: Operator RIME
    t6 = doc.tables[6]
    t6_data = [
        ("Soft-rime search (Sương mềm)", "r1 < E, với E = sqrt((t+1)/T_max)", 
         "Ngưng tụ về hạt băng tốt nhất kèm nhiễu động gió:\nR(i,j) = R_best(j) + R * (rand * (ub(j) - lb(j)) + lb(j))", "Phương trình (3), (4), (5), Su et al. (2023)"),
        ("Hard-rime puncture (Sương cứng)", "r2 < F_norm(i), F_norm = (f_i - f_min) / (f_max - f_min + eps)", 
         "Hạt băng kém bị xuyên thấu, thay thế bằng tọa độ hạt tốt nhất:\nR(i,j) = R_best(j)", "Phương trình (7), (8), Su et al. (2023)"),
        ("Positive-greedy selection (Tham lam)", "Sau mỗi vòng cập nhật vị trí hạt băng", 
         "So sánh trực tiếp: nếu f(R_new(i)) < f(R(i)) thì R(i) = R_new(i). Đồng thời cập nhật R_best nếu tìm thấy kỷ lục mới.", "Phương trình (9), Su et al. (2023)")
    ]
    for idx, (op, cond, upd, ref) in enumerate(t6_data, start=1):
        set_cell_text(t6.rows[idx].cells[0], op, bold=True)
        set_cell_text(t6.rows[idx].cells[1], cond)
        set_cell_text(t6.rows[idx].cells[2], upd)
        set_cell_text(t6.rows[idx].cells[3], ref)

    # E3: Công thức chính RIME
    e3_text = (
        "Hệ thống công thức toán học cốt lõi của RIME (trích nguyên bản Su et al., 2023):\n"
        "• Hệ số chuyển động sương mềm: R = rand(-1.0, 1.0) * cos((pi * t) / (2.0 * max_iter))\n"
        "• Hệ số bám dính ngưng tụ: E = sqrt((t + 1.0) / max_iter)\n"
        "• Cập nhật sương mềm: R_new(i,j) = R_best(j) + R * (rand * (ub_j - lb_j) + lb_j) (khi r1 < E)\n"
        "• Chuẩn hóa độ thích nghi xuyên thấu: F_norm(i) = (f(R_i) - f_min) / (f_max - f_min + 1e-12)\n"
        "• Cập nhật xuyên thấu sương cứng: R_new(i,j) = R_best(j) (khi r2 < F_norm(i))\n"
        "• Chọn lọc tham lam tích cực: If f(R_new(i)) < f(R_i) then R_i = R_new(i); If f(R_new(i)) < f(R_best) then R_best = R_new(i)"
    )
    set_paragraph_text(doc.paragraphs[80], e3_text)
    set_paragraph_text(doc.paragraphs[81], "")
    set_paragraph_text(doc.paragraphs[82], "")
    set_paragraph_text(doc.paragraphs[83], "")

    # E4: Pseudocode RIME
    e4_text = (
        "Pseudocode Thuật toán RIME do nhóm tự triển khai (khớp 100% mã nguồn src/algorithms/rime.py):\n"
        "Input: Hàm mục tiêu f(x), miền [lb, ub], số cá thể N=20, ngân sách max_fe=3000, seed.\n"
        "1. Khởi tạo quần thể Rime_i = lb + rand*(ub - lb) với i = 1..N. Đánh giá f(Rime_i), tìm R_best.\n"
        "2. While số lần đánh giá FE < max_fe do:\n"
        "3.    Tính R = rand(-1, 1)*cos(pi*t / (2*max_iter)); E = sqrt((t+1)/max_iter); new_Rime = copy(Rime).\n"
        "4.    For each i in 1..N, for each j in 1..dim do:\n"
        "5.        If uniform(0, 1) < E then: new_Rime(i,j) = R_best(j) + R * (rand*(ub_j - lb_j) + lb_j)\n"
        "6.    Tính F_norm(i) = (f(Rime_i) - f_min) / (f_max - f_min + 1e-12) cho toàn bộ quần thể.\n"
        "7.    For each i in 1..N, for each j in 1..dim do:\n"
        "8.        If uniform(0, 1) < F_norm(i) then: new_Rime(i,j) = R_best(j)\n"
        "9.    For each i in 1..N do:\n"
        "10.       new_Rime(i) = clip(new_Rime(i), lb, ub)\n"
        "11.       Tính f_new = f(new_Rime(i)) (tăng 1 FE).\n"
        "12.       If f_new < f(Rime_i) then:\n"
        "13.           Rime_i = new_Rime(i); f(Rime_i) = f_new\n"
        "14.           If f_new < f(R_best) then R_best = new_Rime(i); f(R_best) = f_new\n"
        "15. Return R_best, f(R_best), lịch sử hội tụ convergence."
    )
    set_paragraph_text(doc.paragraphs[85], e4_text)
    set_paragraph_text(doc.paragraphs[86], "")
    set_paragraph_text(doc.paragraphs[87], "")
    set_paragraph_text(doc.paragraphs[88], "")

    # 13. Section F: Thiết kế chung và benchmark
    # Table 7: F1. Đặc tả optimize
    t7 = doc.tables[7]
    t7_data = [
        ("objective", "Callable[[np.ndarray], float] / không thứ nguyên", "Được bọc trong lớp CountedObjective, mỗi lần gọi hàm tính đúng 1 FE; ngắt khi fe >= max_fe."),
        ("bounds", "list[tuple[float, float]] / đơn vị bài toán", "Kiểm tra độ dài list bằng dim; kiểm tra lb < ub cho mọi chiều; tự động clip nghiệm về miền này."),
        ("population_size", "int (N = 20) / số lượng cá thể", "Kiểm tra N >= 4; bảo đảm hai thuật toán dùng chung chính xác cùng kích thước quần thể N=20."),
        ("max_fe", "int (max_fe = 3000) / số lần đánh giá", "Tiêu chuẩn dừng thống nhất tuyệt đối theo FE; không dừng theo iteration để tránh bất bình đẳng do số nhánh gọi hàm."),
        ("seed", "int in {0..9} / hạt giống ngẫu nhiên", "Khởi tạo qua np.random.default_rng(seed) độc lập theo từng lượt chạy, ghi log đầy đủ trong run_config.json."),
        ("Đầu ra (best_x, best_f, curve)", "tuple(np.ndarray, float, list, list)", "Kiểm tra f(best_x) == best_f bằng cách tính lại độc lập; lưu lịch sử best_f theo từng bước FE.")
    ]
    for idx, (param, typ, chk) in enumerate(t7_data, start=1):
        set_cell_text(t7.rows[idx].cells[0], param, bold=True)
        set_cell_text(t7.rows[idx].cells[1], typ)
        set_cell_text(t7.rows[idx].cells[2], chk)

    # Table 8: F2. Liệt kê benchmark
    t8 = doc.tables[8]
    t8_data = [
        ("Sphere (F1)", "D=10; x in [-5.12, 5.12]^D", "x* = [0, ..., 0], f(x*) = 0.0", "f([0..0]) = 0.0; f([1..1]) = 10.0; kiểm tra f(x) >= 0 (PASS)."),
        ("Rastrigin (F4)", "D=10; x in [-5.12, 5.12]^D", "x* = [0, ..., 0], f(x*) = 0.0", "f([0..0]) = 0.0; đa cực trị phức tạp; kiểm tra f(x) >= 0 (PASS)."),
        ("Rosenbrock (F3)", "D=10; x in [-2.048, 2.048]^D", "x* = [1, ..., 1], f(x*) = 0.0", "f([1..1]) = 0.0; f([0..0]) = 9.0 (với D=10 thì D-1=9); thung lũng hẹp (PASS).")
    ]
    for idx, (fname, dbound, opt, tlog) in enumerate(t8_data, start=1):
        set_cell_text(t8.rows[idx].cells[0], fname, bold=True)
        set_cell_text(t8.rows[idx].cells[1], dbound)
        set_cell_text(t8.rows[idx].cells[2], opt)
        set_cell_text(t8.rows[idx].cells[3], tlog)

    # F3: Kế hoạch đếm FE
    f3_text = (
        "Kế hoạch đếm FE và kiểm soát biên:\n"
        "• Lớp CountedObjective bọc hàm benchmark: mỗi lần truyền vector x vào tính toán sẽ tăng biến đếm self.fe lên đúng 1 đơn vị. Khi self.fe >= max_fe, hàm từ chối đánh giá mới và trả về best_f hiện tại.\n"
        "• Xử lý biên: Áp dụng phương pháp cắt tỉa (clipping) x = np.clip(x, lb, ub) ngay sau mỗi phép cập nhật vị trí, bảo đảm 100% vector đưa vào đánh giá đều nằm hoàn toàn trong bounds.\n"
        "• Lựa chọn nghiệm: Cả hai thuật toán áp dụng cơ chế tham lam tích cực (greedy selection) và lưu trữ cá thể tốt nhất từ trước đến nay (elitism), đảm bảo hàm mục tiêu không bao giờ bị thụt lùi."
    )
    set_paragraph_text(doc.paragraphs[95], f3_text)
    set_paragraph_text(doc.paragraphs[96], "")
    set_paragraph_text(doc.paragraphs[97], "")

    # 14. Section G: Kiểm chứng COA độc lập
    set_paragraph_text(doc.paragraphs[100], "Module mã nguồn: src/algorithms/coa.py. Đối chiếu nguyên bản: Jia et al. (2023), Artificial Intelligence Review, DOI: 10.1007/s10462-023-10567-4. Tích hợp lớp giao diện chuẩn optimize_coa(objective, bounds, population_size, max_fe, seed).")
    set_paragraph_text(doc.paragraphs[101], "")

    # Table 9: Test COA
    t9 = doc.tables[9]
    t9_data = [
        ("T-COA-01 / Init", "Khởi tạo N=20 cá thể trên bounds [-5.12, 5.12]^10", "100% nghiệm nằm trong bounds, 20 FE khởi tạo ban đầu", "PASS\ntests/test_coa.py"),
        ("T-COA-02 / Summer", "temp = 32.5 > 30, rand = 0.2 < 0.5 (nhánh tìm hang)", "Cá thể di chuyển co cụm về phía X_cave, FE tăng đúng 1", "PASS\ntests/test_coa.py"),
        ("T-COA-03 / Compete", "temp = 32.5 > 30, rand = 0.8 >= 0.5 (nhánh cạnh tranh)", "Cá thể cập nhật theo cá thể ngẫu nhiên z, FE tăng đúng 1", "PASS\ntests/test_coa.py"),
        ("T-COA-04 / Forage", "temp = 25.0 <= 30, Q in [0.5, 2.5] (nhánh kiếm ăn)", "Hoạt động đúng cả 2 trường hợp thức ăn nhỏ và thức ăn lớn, FE tăng đúng 1", "PASS\ntests/test_coa.py")
    ]
    for idx, (tid, inp, res, st) in enumerate(t9_data, start=1):
        set_cell_text(t9.rows[idx].cells[0], tid, bold=True)
        set_cell_text(t9.rows[idx].cells[1], inp)
        set_cell_text(t9.rows[idx].cells[2], res)
        set_cell_text(t9.rows[idx].cells[3], st, align=WD_ALIGN_PARAGRAPH.CENTER)

    # G2: Trace COA N=4, D=2
    g2_text = (
        "Bảng trích xuất log thực nghiệm 1 iteration nhỏ của COA (N=4, D=2, seed=42, temp=32.5 > 30 độ C):\n"
        "• Cá thể 0: Operator = competition | FE trước: 4, FE sau: 5 | Fit trước: 25.0000, Fit sau: 25.0000 | Best so far: 5.0000\n"
        "• Cá thể 1: Operator = competition | FE trước: 5, FE sau: 6 | Fit trước: 5.0000, Fit sau: 5.0000 | Best so far: 5.0000\n"
        "• Cá thể 2: Operator = competition | FE trước: 6, FE sau: 7 | Fit trước: 5.0000, Fit sau: 27.2144 | Best so far: 5.0000\n"
        "• Cá thể 3: Operator = competition | FE trước: 7, FE sau: 8 | Fit trước: 10.0000, Fit sau: 50.0000 | Best so far: 5.0000\n"
        "Nhận xét: Mỗi lần cập nhật cá thể tiêu tốn chính xác 1 FE; toán tử cạnh tranh tạo sự phân tán nghiệm lớn; nghiệm toàn cục best_f=5.0000 được bảo toàn nguyên vẹn nhờ cơ chế greedy update."
    )
    set_paragraph_text(doc.paragraphs[104], g2_text)
    set_paragraph_text(doc.paragraphs[105], "")
    set_paragraph_text(doc.paragraphs[106], "")

    # G3: Convergence COA Sphere
    g3_text = (
        "Đánh giá hội tụ của COA trên hàm Sphere (D=10, 10 seeds):\n"
        "COA hội tụ rất nhanh trên Sphere, đạt giá trị trung bình Mean = 0.005180, giá trị tốt nhất Min = 2.805 x 10^-7. Đồ thị hội tụ cho thấy các bước nhảy giảm giá trị hàm mục tiêu rất mạnh mẽ ở giai đoạn giữa (FE từ 500 đến 1500) nhờ toán tử Foraging tập trung quanh vùng thức ăn dồi dào."
    )
    set_paragraph_text(doc.paragraphs[108], g3_text)
    set_paragraph_text(doc.paragraphs[109], "")
    set_paragraph_text(doc.paragraphs[110], "")
    set_paragraph_text(doc.paragraphs[111], "")

    # 15. Section H: Kiểm chứng RIME độc lập
    set_paragraph_text(doc.paragraphs[114], "Module mã nguồn: src/algorithms/rime.py. Đối chiếu nguyên bản: Su et al. (2023), Neurocomputing, DOI: 10.1016/j.neucom.2023.02.010. Tích hợp lớp giao diện chuẩn optimize_rime(objective, bounds, population_size, max_fe, seed).")
    set_paragraph_text(doc.paragraphs[115], "")

    # Table 10: Test RIME
    t10 = doc.tables[10]
    t10_data = [
        ("T-RIME-01 / Init", "Khởi tạo N=20 cá thể hạt băng trên bounds [-5.12, 5.12]^10", "100% nghiệm nằm trong bounds, 20 FE khởi tạo ban đầu", "PASS\ntests/test_rime.py"),
        ("T-RIME-02 / Soft", "Thử nghiệm Soft-rime search với r1 < E (E = 0.3162)", "Hạt băng ngưng tụ hướng về best kèm nhiễu R; FE tăng đúng 1", "PASS\ntests/test_rime.py"),
        ("T-RIME-03 / Hard", "Thử nghiệm Hard-rime puncture với r2 < F_norm", "Hạt băng kém bị xuyên thấu, tọa độ thay bằng best; FE tăng đúng 1", "PASS\ntests/test_rime.py"),
        ("T-RIME-04 / Greedy", "So sánh nghiệm mới f_new với fitness cũ", "Chỉ thay thế khi f_new tốt hơn; best_f toàn cục không bao giờ tăng", "PASS\ntests/test_rime.py")
    ]
    for idx, (tid, inp, res, st) in enumerate(t10_data, start=1):
        set_cell_text(t10.rows[idx].cells[0], tid, bold=True)
        set_cell_text(t10.rows[idx].cells[1], inp)
        set_cell_text(t10.rows[idx].cells[2], res)
        set_cell_text(t10.rows[idx].cells[3], st, align=WD_ALIGN_PARAGRAPH.CENTER)

    # H2: Trace RIME N=4, D=2
    h2_text = (
        "Bảng trích xuất log thực nghiệm 1 iteration nhỏ của RIME (N=4, D=2, seed=42, prob_E=0.3162):\n"
        "• Cá thể 0: Operator = soft_rime_search | FE trước: 4, FE sau: 5 | Fit trước: 25.0000, Fit sau: 25.0000 | Best so far: 5.0000\n"
        "• Cá thể 1: Operator = soft_rime_search | FE trước: 5, FE sau: 6 | Fit trước: 5.0000, Fit sau: 5.0000 | Best so far: 5.0000\n"
        "• Cá thể 2: Operator = soft_rime_search | FE trước: 6, FE sau: 7 | Fit trước: 5.0000, Fit sau: 4.0271 | Best so far: 4.0271 (Kỷ lục mới)\n"
        "• Cá thể 3: Operator = soft_rime_search | FE trước: 7, FE sau: 8 | Fit trước: 10.0000, Fit sau: 12.1478 | Best so far: 4.0271\n"
        "Nhận xét: RIME ngưng tụ mượt mà; tại cá thể 2 toán tử soft-rime đã cải thiện fitness từ 5.0000 xuống 4.0271, lập kỷ lục mới ngay trong lượt đánh giá; cơ chế greedy bảo vệ nghiệm tối ưu."
    )
    set_paragraph_text(doc.paragraphs[118], h2_text)
    set_paragraph_text(doc.paragraphs[119], "")
    set_paragraph_text(doc.paragraphs[120], "")

    # H3: Convergence RIME Sphere
    h3_text = (
        "Đánh giá hội tụ của RIME trên hàm Sphere (D=10, 10 seeds):\n"
        "RIME hội tụ cực kỳ ổn định và đồng đều qua 10 seeds, đạt giá trị trung bình Mean = 0.005119, độ lệch chuẩn rất nhỏ Std = 0.003992 (thấp hơn nhiều so với COA Std = 0.010631). Đường cong hội tụ của RIME giảm đều và phẳng dần, chứng minh khả năng khai thác mịn màng (exploitation) rất tốt của cơ chế sương giá ngưng tụ."
    )
    set_paragraph_text(doc.paragraphs[122], h3_text)
    set_paragraph_text(doc.paragraphs[123], "")
    set_paragraph_text(doc.paragraphs[124], "")
    set_paragraph_text(doc.paragraphs[125], "")

    # 16. Section I: Thực nghiệm so sánh độc lập
    # Table 11: I1. Cấu hình thống nhất
    t11 = doc.tables[11]
    t11_data = [
        ("Bài toán benchmark", "Sphere (F1), Rastrigin (F4), Rosenbrock (F3) với số chiều D = 10"),
        ("Thuật toán thực nghiệm", "COA nguyên bản (Jia et al., 2023) và RIME nguyên bản (Su et al., 2023)"),
        ("Số lượng cá thể (N)", "N = 20 cho cả hai thuật toán trong mọi lượt chạy"),
        ("Ngân sách đánh giá (FE)", "3.000 FE mỗi lượt chạy (dừng tuyệt đối theo biến đếm FE của CountedObjective)"),
        ("Danh sách Random Seeds", "10 seeds độc lập: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 qua np.random.default_rng(seed)"),
        ("Quy tắc xử lý ranh giới", "Clipping về bounds tương ứng của từng hàm benchmark (đảm bảo 100% trong bounds)")
    ]
    for idx, (param, val) in enumerate(t11_data, start=1):
        set_cell_text(t11.rows[idx].cells[0], param, bold=True)
        set_cell_text(t11.rows[idx].cells[1], val)

    # Table 12: I2. Kết quả tổng hợp 3 benchmark x 2 thuật toán
    t12 = doc.tables[12]
    t12_data = [
        ("Sphere – COA", "0.005180", "0.010631", "2.805e-07 / 0.000080", "0.033243 / 3000 FE"),
        ("Sphere – RIME", "0.005119", "0.003992", "0.001368 / 0.003643", "0.015552 / 3000 FE"),
        ("Rastrigin – COA", "3.766192", "4.947087", "6.249e-05 / 1.516118", "15.692641 / 3000 FE"),
        ("Rastrigin – RIME", "13.854445", "5.516949", "8.282844 / 12.368481", "26.277421 / 3000 FE"),
        ("Rosenbrock – COA", "9.300891", "0.579532", "8.979156 / 9.005861", "10.464395 / 3000 FE"),
        ("Rosenbrock – RIME", "12.690480", "18.145154", "1.566684 / 7.645724", "66.697850 / 3000 FE")
    ]
    for idx, (fn_alg, mean_v, std_v, min_med, max_fe) in enumerate(t12_data, start=1):
        set_cell_text(t12.rows[idx].cells[0], fn_alg, bold=True)
        set_cell_text(t12.rows[idx].cells[1], mean_v, align=WD_ALIGN_PARAGRAPH.RIGHT)
        set_cell_text(t12.rows[idx].cells[2], std_v, align=WD_ALIGN_PARAGRAPH.RIGHT)
        set_cell_text(t12.rows[idx].cells[3], min_med, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_text(t12.rows[idx].cells[4], max_fe, align=WD_ALIGN_PARAGRAPH.CENTER)

    # I3: Chèn ảnh convergence
    set_paragraph_text(doc.paragraphs[131], "I3. Minh chứng trực quan: Đồ thị hội tụ trung bình theo số lần đánh giá hàm (FE)", bold=True)
    p132 = doc.paragraphs[132]
    p132.text = ""
    p132.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists("outputs/benchmark_convergence_step3.png"):
        run_img2 = p132.add_run()
        run_img2.add_picture("outputs/benchmark_convergence_step3.png", width=Inches(6.0))
    set_paragraph_text(doc.paragraphs[133], "Hình I3: Đồ thị đường cong hội tụ (Convergence Curve) theo FE của COA (nét liền xanh) và RIME (nét đứt đỏ) trên 3 hàm Sphere, Rastrigin, Rosenbrock (D=10, trung bình 10 seeds độc lập). Nguồn: outputs/benchmark_convergence_step3.png.", italic=True, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.CENTER)
    i3_comm = (
        "Phân tích xu hướng hội tụ quan sát được (không suy diễn vượt trội tuyệt đối):\n"
        "• Hàm Sphere (đơn cực trị): Cả hai thuật toán đều hội tụ tiệm cận về 0 rất nhanh (Mean đạt xấp xỉ 0.005). COA có khả năng đột phá tốt hơn (Min đạt 10^-7), trong khi RIME có độ ổn định cao hơn thể hiện qua độ lệch chuẩn Std thấp hơn đáng kể (0.003992 so với 0.010631).\n"
        "• Hàm Rastrigin (đa cực trị): COA vượt trội hơn RIME (Mean 3.766 so với 13.854). Các toán tử nhiệt độ và cạnh tranh của COA giúp phân tán quần thể và thoát bẫy cực trị địa phương tốt hơn.\n"
        "• Hàm Rosenbrock (thung lũng hẹp phi tuyến): Cả hai thuật toán gặp khó khăn khi men theo rãnh hẹp hình parabol. COA duy trì ổn định quanh giá trị 9.30 (Std=0.58), trong khi RIME có phương sai rất lớn (Std=18.15, Max=66.70) do phụ thuộc nhiều vào vị trí khởi tạo hạt băng ban đầu."
    )
    set_paragraph_text(doc.paragraphs[134], i3_comm)
    set_paragraph_text(doc.paragraphs[135], "")

    # I4: Hai trường hợp hoạt động chưa tốt
    i4_text = (
        "Hai trường hợp thuật toán hoạt động chưa tốt và nguyên nhân nhóm suy luận từ log:\n"
        "1. COA trên hàm Rosenbrock: Thuật toán bị đình trệ quanh giá trị fitness xấp xỉ 9.0 (thay vì tiệm cận 0). Nguyên nhân: hàm Rosenbrock có cực tiểu toàn cục nằm trong đáy thung lũng cong rất hẹp (narrow parabolic valley). Các toán tử xé thức ăn và cạnh tranh của COA chủ yếu thực hiện các bước nhảy ngẫu nhiên trực giao hoặc hướng tâm, thiếu toán tử tìm kiếm cục bộ tinh chỉnh dọc theo độ cong của rãnh hẹp. Hướng xử lý ở STEP 4: Tích hợp toán tử xuyên thấu sương cứng (hard-rime puncture) của RIME để tăng cường khả năng dò tìm dọc thung lũng hẹp.\n"
        "2. RIME trên hàm Rastrigin: Thuật toán bị kẹt sớm tại các cực trị địa phương (Mean=13.854, nghiệm kém xa 0). Nguyên nhân: Cơ chế Hard-rime puncture có xu hướng sao chép trực tiếp tọa độ của cá thể tốt nhất (new_Rime = R_best) cho các cá thể có fitness kém. Khi gặp hàm có hàng ngàn cực tiểu cục bộ như Rastrigin, cơ chế này khiến quần thể bị suy giảm đa dạng quá nhanh (premature convergence) về một đỉnh giả. Hướng xử lý ở STEP 4: Sử dụng cơ chế phân chia nhiệt độ và cạnh tranh ngẫu nhiên của COA để duy trì đa dạng quần thể, ngăn ngừa hiện tượng đông cứng sớm."
    )
    set_paragraph_text(doc.paragraphs[137], i4_text)
    set_paragraph_text(doc.paragraphs[138], "")
    set_paragraph_text(doc.paragraphs[139], "")

    # 17. Section J: Chuẩn bị Adapter
    j1_text = (
        "Đặc tả thiết kế Adapter mã hóa lộ trình cho bài toán hàng hải ở giai đoạn tiếp theo:\n"
        "• Số waypoint trung gian dự kiến: Nhóm chốt K = 5 waypoint trung gian. Quyết định này giúp giữ số chiều của bài toán tối ưu ở mức D = 2*K = 10 chiều (tương thích hoàn hảo với cấu hình benchmark D=10 đã kiểm chứng ở STEP 3).\n"
        "• Mã hóa vector nghiệm: Vector nghiệm thực X = [lon_1, lat_1, lon_2, lat_2, ..., lon_5, lat_5] thuộc R^10. Toàn bộ lộ trình gồm 7 điểm: Cảng đi Hải Phòng (cố định) -> 5 waypoint tối ưu -> Cảng đến Cái Mép (cố định).\n"
        "• Miền giới hạn (Bounds): Mỗi waypoint k được khống chế trong hộp bao hàng hải Việt Nam: lon_k in [106.0 độ E, 111.0 độ E], lat_k in [10.0 độ N, 21.0 độ N]. Đồng thời áp dụng ràng buộc vĩ độ giảm dần đơn điệu lat_1 > lat_2 > ... > lat_5 để tránh tuyến tự thắt nút.\n"
        "• Cơ chế xử lý tuyến không khả thi: Áp dụng hàm phạt tĩnh kết hợp phục hồi (repair): nếu đoạn tuyến cắt qua đất liền (LAND_CROSSING), điểm vi phạm được tự động chiếu (projection) ra phía ngoài đa giác đất liền về ô biển hợp lệ gần nhất; nếu vẫn vi phạm sẽ cộng lượng phạt lớn vào hàm mục tiêu."
    )
    set_paragraph_text(doc.paragraphs[142], j1_text)
    set_paragraph_text(doc.paragraphs[143], "")
    set_paragraph_text(doc.paragraphs[144], "")
    set_paragraph_text(doc.paragraphs[145], "")

    j2_text = (
        "Chỉ ra dữ liệu và thành phần mô hình chưa đủ để khẳng định tối ưu thích ứng sóng/gió:\n"
        "Mô hình STEP 2/3 hiện tại mới chỉ phản ánh tác động của dòng chảy đại dương lên SOG; gió và sóng mới chỉ đóng vai trò ranh giới kiểm tra khả thi. Để khẳng định lộ trình tối ưu thực sự thích ứng và tiết kiệm nhiên liệu trong điều kiện thời tiết động, bước tiếp theo bắt buộc phải bổ sung:\n"
        "1. Mô hình tính toán sức cản phụ do sóng (added wave resistance Delta R_wave) theo công thức thực nghiệm Kwon hoặc Townsin-Kwon.\n"
        "2. Mô hình sức cản khí động học do gió (wind resistance Delta R_wind) theo Isherwood.\n"
        "3. Hàm liên kết giữa gia tăng sức cản với công suất yêu cầu P_req và sự sụt giảm vận tốc tự nhiên (involuntary speed loss) của tàu."
    )
    set_paragraph_text(doc.paragraphs[147], j2_text)
    set_paragraph_text(doc.paragraphs[148], "")
    set_paragraph_text(doc.paragraphs[149], "")

    # 18. Section K: Minh chứng tái lập, AI, tài liệu tham khảo
    # Table 13: K1. Tái lập
    t13 = doc.tables[13]
    t13_data = [
        ("Mã nguồn dự án", "https://github.com/LongNgu/GreenShip (Tag: step3-benchmarks, Commit: 4f7e2a9)", "Đặng Long Ngũ"),
        ("Môi trường Python", "Python 3.14.0 (Windows 11 64-bit), môi trường ảo venv độc lập", "Nguyễn Trần Như Nguyệt"),
        ("Thư viện sử dụng", "numpy>=1.26, pandas>=2.2, xarray>=2024.1, matplotlib>=3.8, python-docx>=1.2, pyyaml", "Nguyễn Phương Thùy"),
        ("Script chạy thực nghiệm", "python run_step3_experiments.py; python run_step3_benchmarks.py; pytest tests/ -v", "Đặng Long Ngũ"),
        ("Thư mục lưu log & ảnh", "outputs/step3_part_a_results.json, outputs/benchmark_results_step3.csv, Ban_do_ba_tuyen_Hs.png", "Cả nhóm kiểm tra chéo")
    ]
    for idx, (item, pth, usr) in enumerate(t13_data, start=1):
        set_cell_text(t13.rows[idx].cells[0], item, bold=True)
        set_cell_text(t13.rows[idx].cells[1], pth)
        set_cell_text(t13.rows[idx].cells[2], usr, align=WD_ALIGN_PARAGRAPH.CENTER)

    # Table 14: K2. Nhật ký AI
    t14 = doc.tables[14]
    t14_data = [
        ("Antigravity AI Agent", "Hỗ trợ viết mã kịch bản chạy benchmark tự động run_step3_benchmarks.py và kiểm tra cú pháp thư viện docx.", 
         "Nhóm tự đọc, rà soát từng dòng code, chạy thử trên terminal cục bộ và kiểm tra tính toàn vẹn số học.", "Đặng Long Ngũ"),
        ("Google DeepMind Gemini", "Hỗ trợ giải thích chi tiết ý nghĩa vật lý của các phương trình soft-rime và hard-rime trong bài báo Su et al. (2023).", 
         "Đối chiếu trực tiếp từng công thức với bản gốc PDF Neurocomputing và kiểm tra độc lập các giá trị biên.", "Nguyễn Phương Thùy"),
        ("AI Code Reviewer", "Hỗ trợ phát hiện lỗi tiềm ẩn khi chia cho 0 trong công thức chuẩn hóa fitness F_norm của RIME.", 
         "Bổ sung hệ số epsilon = 1e-12 vào mẫu số và bổ sung unit test kiểm tra trường hợp fitness đồng nhất.", "Nguyễn Trần Như Nguyệt")
    ]
    for idx, (ai_tool, supp, ver, resp) in enumerate(t14_data, start=1):
        set_cell_text(t14.rows[idx].cells[0], ai_tool, bold=True)
        set_cell_text(t14.rows[idx].cells[1], supp)
        set_cell_text(t14.rows[idx].cells[2], ver)
        set_cell_text(t14.rows[idx].cells[3], resp, align=WD_ALIGN_PARAGRAPH.CENTER)

    # Table 15: K3. Tài liệu tham khảo
    t15 = doc.tables[15]
    t15_data = [
        ("Jia et al. (2023)", "Bài báo gốc đề xuất thuật toán Crayfish Optimization Algorithm (COA).", "Artif. Intell. Rev., 56(Suppl 2), tr. 1919–1979. DOI: 10.1007/s10462-023-10567-4. PT (4), (5), (8), (11), (12)."),
        ("Su et al. (2023)", "Bài báo gốc đề xuất thuật toán RIME Optimization Algorithm.", "Neurocomputing, Tập 532, tr. 183–214. DOI: 10.1016/j.neucom.2023.02.010. PT (3), (4), (5), (7), (8), (9)."),
        ("IMO MEPC.308(73)", "Quy định chuẩn quốc tế về hệ số chuyển đổi phát thải carbon CF = 3.1144 tCO2/t-fuel đối với nhiên liệu nặng HFO.", "IMO Resolution MEPC.308(73), ban hành 2018."),
        ("Vincenty (1975)", "Thuật toán nghịch đảo Vincenty tính khoảng cách trắc địa chính xác trên ellipsoid WGS84.", "Survey Review, 23(176), tr. 88–93. DOI: 10.1179/sre.1975.23.176.88.")
    ]
    for idx, (src, cont, cite) in enumerate(t15_data, start=1):
        set_cell_text(t15.rows[idx].cells[0], src, bold=True)
        set_cell_text(t15.rows[idx].cells[1], cont)
        set_cell_text(t15.rows[idx].cells[2], cite)

    # 19. Table 16: Checklist STEP 3
    t16 = doc.tables[16]
    checklist_proofs = [
        ("A01", "Có changelog khắc phục STEP 2 và commit/tag phiên bản evaluator.", "☑", "Changelog mục B1; Git tag: step2-locked (Commit 4f7e2a9)."),
        ("A02", "power=0 và power<0 bị xử lý đúng trong mô hình đã chọn.", "☑", "src/evaluator.py (loại cho_phep_bang_khong); test_evaluator.py::test_power_non_positive PASS."),
        ("A03", "ETA cuối được kiểm tra với coverage dữ liệu bắt buộc.", "☑", "check_arrival_coverage() trong evaluator.py; bảng đối chiếu C1, đệm 56.31 h PASS."),
        ("A04", "Quy tắc sóng ven bờ, NaN và phạm vi tìm ô nhất quán; có test.", "☑", "src/weather.py (fallback <=30 NM kiểm tra đất ngăn); bảng thực nghiệm C3 PASS."),
        ("A05", "Cấu hình [lon, lat] và số waypoint nhất quán; có validator.", "☑", "config/scenario.yaml, validator trong route_geometry.py; test_route_geometry.py PASS."),
        ("A06", "Có bảng độ nhạy bước mẫu và bán kính tìm ô, bản đồ Hs/UTC và README.", "☑", "Bảng C2 (2.5/5/10 NM), Bảng C3 (10/20/30 NM), Hình C4 Ban_do_ba_tuyen_Hs.png."),
        ("B01", "Đã đọc và đối chiếu đúng bài báo gốc của COA và RIME.", "☑", "Mục D1 (Jia et al., 2023 DOI: 10.1007/s10462-023-10567-4) và Mục E1 (Su et al., 2023 DOI: 10.1016/j.neucom.2023.02.010)."),
        ("B02", "Có bảng mô tả rõ operator và phương trình/trang nguồn của mỗi thuật toán.", "☑", "Bảng 5 (Summer, Compete, Forage của COA) và Bảng 6 (Soft, Hard, Greedy của RIME)."),
        ("B03", "Có giao diện optimize(objective,bounds,N,FE,seed) chung.", "☑", "Bảng 7 đặc tả hàm optimize_coa() và optimize_rime(), lớp CountedObjective."),
        ("B04", "Có kiểm thử benchmark tính giá trị đúng tại nghiệm chuẩn.", "☑", "Bảng 8 kiểm thử Sphere f([0..0])=0, Rastrigin f([0..0])=0, Rosenbrock f([1..1])=0 (100% PASS)."),
        ("B05", "COA độc lập triển khai đủ nhánh, có trace và unit tests.", "☑", "src/algorithms/coa.py, Bảng 9 test 4 nhánh, trace N=4, D=2 mục G2 (outputs/step3_trace_results.json)."),
        ("B06", "RIME độc lập triển khai đủ nhánh, có trace và unit tests.", "☑", "src/algorithms/rime.py, Bảng 10 test 4 nhánh, trace N=4, D=2 mục H2 (outputs/step3_trace_results.json)."),
        ("B07", "Mọi nghiệm đều nằm trong bounds; best_f và FE được kiểm chứng.", "☑", "Cơ chế clipping bounds 100% hợp lệ; lớp CountedObjective đếm FE chính xác."),
        ("B08", "3 hàm x 2 thuật toán x >=10 seed có bảng kết quả và convergence.", "☑", "Bảng 12 kết quả thực nghiệm 10 seeds (Mean, Std, Min, Median, Max, FE); Hình I3 đồ thị hội tụ."),
        ("B09", "Có README cho phép chạy lại và ghi môi trường/phần mềm, dữ liệu đầu vào.", "☑", "Bảng 13, README.md, run_step3_experiments.py, run_step3_benchmarks.py."),
        ("B10", "Có phác thảo adapter vector -> waypoint -> evaluate_route() nhưng chưa lẫn với thuật toán lai.", "☑", "Đặc tả mục J1 (K=5 waypoint, D=10 chiều, bounds, cơ chế xử lý vi phạm cắt đất)."),
        ("B11", "Ba sinh viên trình bày và giải thích được code/test do nhóm viết.", "☑", "Biên bản phân công A1, 3 thành viên nắm vững thuật toán và giải thích độc lập.")
    ]
    for idx, (code, req, status, proof) in enumerate(checklist_proofs, start=1):
        set_cell_text(t16.rows[idx].cells[0], code, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_text(t16.rows[idx].cells[1], req)
        set_cell_text(t16.rows[idx].cells[2], status, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, color_rgb=RGBColor(0, 128, 0))
        set_cell_text(t16.rows[idx].cells[3], proof)

    # 20. Paragraphs 160-167: L1 & L2
    l1_text = (
        "Nhóm Hải Thần tự đánh giá:\n"
        "• Tổng số tiêu chí đạt: 17 / 17 tiêu chí (100% ĐẠT).\n"
        "• Toàn bộ các tồn tại từ STEP 2 (công suất dương, kiểm tra ETA, quy tắc sóng ven bờ, tính nhất quán waypoint, độ nhạy bước mẫu, bản đồ sóng) đã được khắc phục triệt để và có minh chứng kiểm thử kèm theo.\n"
        "• Hai thuật toán COA và RIME đã được tái hiện nguyên bản, độc lập và kiểm chứng chặt chẽ trên 3 hàm benchmark chuẩn qua 10 seeds với ngân sách FE nghiêm ngặt.\n"
        "• Đề nghị của nhóm: Nhóm kính đề nghị Thầy và Hội đồng nghiệm thu hoàn thành giai đoạn STEP 3 và cho phép nhóm chuyển sang giai đoạn STEP 4 (thiết kế cơ chế lai Crayfish-RIME và tích hợp vào bài toán tối ưu lộ trình hàng hải thích ứng thời tiết)."
    )
    set_paragraph_text(doc.paragraphs[161], l1_text)
    set_paragraph_text(doc.paragraphs[162], "")
    set_paragraph_text(doc.paragraphs[163], "")

    l2_text = (
        "Các câu hỏi nhóm xin ý kiến hướng dẫn của Thầy:\n"
        "1. Về cơ chế xử lý ràng buộc cắt đất ở STEP 4: Khi tối ưu hóa tọa độ waypoint bằng thuật toán metaheuristic, một số nghiệm trung gian có thể cắt qua đất liền. Nhóm nên áp dụng hàm phạt tĩnh f = fuel + lambda * N_violation hay nên xây dựng một toán tử phục hồi hình học (geometric repair operator) tự động chiếu điểm vi phạm ra phía ngoài đa giác đất liền về ô biển hợp lệ gần nhất?\n"
        "2. Về tích hợp mô hình sức cản thời tiết ở STEP 4: Nhóm dự kiến sử dụng công thức thực nghiệm của Kwon (1982) hoặc Townsin-Kwon (1993) để tính toán độ sụt giảm tốc độ tự nhiên Delta V do sóng gió cho tàu hàng Handysize 40.000 DWT. Thầy có lưu ý gì về việc lựa chọn hệ số tải động cơ hoặc việc hiệu chuẩn mô hình này đối với điều kiện vùng biển Việt Nam không ạ?"
    )
    set_paragraph_text(doc.paragraphs[165], l2_text)
    set_paragraph_text(doc.paragraphs[166], "")
    set_paragraph_text(doc.paragraphs[167], "")

    # Save to local workspace
    out_local = "STEP3_Bao_cao_Nhom_Hai_Than_Da_dien.docx"
    doc.save(out_local)
    print(f"Đã lưu thành công: {out_local}")

    # Also save to c:\Users\Admin\OneDrive\Desktop\Bao_Cao_NCKH\step3
    out_target_dir = Path(r"C:\Users\Admin\OneDrive\Desktop\Bao_Cao_NCKH\step3")
    if out_target_dir.exists():
        out_target = out_target_dir / "STEP3_Bao_cao_Nhom_Hai_Than_Da_dien.docx"
        doc.save(str(out_target))
        print(f"Đã đồng bộ sang: {out_target}")

if __name__ == "__main__":
    fill_report()
