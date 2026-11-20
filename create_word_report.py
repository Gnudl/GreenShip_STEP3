import os
from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def create_report():
    doc = Document()

    # --- Page Setup (Margins: 2.0 cm) ---
    for section in doc.sections:
        section.top_margin = Inches(0.79)
        section.bottom_margin = Inches(0.79)
        section.left_margin = Inches(0.79)
        section.right_margin = Inches(0.79)

    # Base Colors
    COLOR_PRIMARY = RGBColor(31, 78, 121)     # Deep Navy #1F4E79
    COLOR_SECONDARY = RGBColor(46, 117, 182) # Blue #2E75B6
    COLOR_TEXT = RGBColor(38, 38, 38)        # Charcoal #262626
    COLOR_MUTED = RGBColor(89, 89, 89)       # Gray #595959
    HEX_PRIMARY = "1F4E79"
    HEX_LIGHT_BG = "F2F5F8"
    HEX_BORDER = "D3DFEE"
    HEX_ALT_ROW = "F9FBFC"

    # Base Normal Style
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Times New Roman'
    style_normal.font.size = Pt(11)
    style_normal.font.color.rgb = COLOR_TEXT
    style_normal.paragraph_format.line_spacing = 1.2
    style_normal.paragraph_format.space_after = Pt(4)

    def set_font_rfonts(run, font_name="Times New Roman"):
        rPr = run._r.get_or_add_rPr()
        rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="{font_name}" w:hAnsi="{font_name}" w:cs="{font_name}"/>')
        rPr.append(rFonts)

    def set_cell_background(cell, fill_hex):
        tcPr = cell._tc.get_or_add_tcPr()
        tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>'))

    def set_cell_margins(cell, top=120, bottom=120, left=160, right=160):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
        tcPr.append(tcMar)

    def set_table_borders(table, color=HEX_BORDER):
        tblPr = table._tbl.tblPr
        borders_xml = f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="6" w:space="0" w:color="{color}"/>
            <w:bottom w:val="single" w:sz="6" w:space="0" w:color="{color}"/>
            <w:left w:val="none"/>
            <w:right w:val="none"/>
            <w:insideH w:val="single" w:sz="4" w:space="0" w:color="{color}"/>
            <w:insideV w:val="none"/>
        </w:tblBorders>
        '''
        tblPr.append(parse_xml(borders_xml))

    def add_title(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(20)
        run.font.color.rgb = COLOR_PRIMARY
        set_font_rfonts(run)
        return p

    def add_subtitle(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(14)
        run = p.add_run(text)
        run.font.size = Pt(12)
        run.font.italic = True
        run.font.color.rgb = COLOR_SECONDARY
        set_font_rfonts(run)
        return p

    def add_heading_1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(15)
        run.font.color.rgb = COLOR_PRIMARY
        set_font_rfonts(run)
        return p

    def add_heading_2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(13)
        run.font.color.rgb = COLOR_SECONDARY
        set_font_rfonts(run)
        return p

    def add_heading_3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(11.5)
        run.font.color.rgb = COLOR_PRIMARY
        set_font_rfonts(run)
        return p

    def add_callout(text, prefix="LƯU Ý: "):
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.cell(0, 0)
        set_cell_background(cell, HEX_LIGHT_BG)
        set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
        
        tcPr = cell._tc.get_or_add_tcPr()
        borders_xml = f'''
        <w:tcBorders {nsdecls("w")}>
            <w:left w:val="single" w:sz="24" w:space="0" w:color="{HEX_PRIMARY}"/>
            <w:top w:val="none"/>
            <w:right w:val="none"/>
            <w:bottom w:val="none"/>
        </w:tcBorders>
        '''
        tcPr.append(parse_xml(borders_xml))
        
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.15
        
        run_prefix = p.add_run(prefix)
        run_prefix.bold = True
        run_prefix.font.color.rgb = COLOR_PRIMARY
        set_font_rfonts(run_prefix)
        
        run_text = p.add_run(text)
        run_text.font.color.rgb = COLOR_TEXT
        set_font_rfonts(run_text)
        
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # ==================== HEADER INFO ====================
    add_title("DỰ ÁN NGHIÊN CỨU KHOA HỌC SINH VIÊN GREENSHIP")
    add_subtitle("BÁO CÁO CHI TIẾT CHỨC NĂNG CÁC HÀM TRONG THƯ MỤC SRC\nVÀ DANH MỤC TIÊU CHÍ NGHIỆM THU STEP 2")

    # Meta Table
    meta_table = doc.add_table(rows=2, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Cơ quan / Đơn vị:", "Đề tài Nghiên cứu Khoa học Sinh viên GreenShip"),
        ("Tên nhóm nghiên cứu:", "Nhóm Hải Thần (Đặng Long Ngũ, Nguyễn Trần Như Nguyệt, Nguyễn Phương Thùy)"),
        ("Mã giai đoạn (Step):", "STEP 2 – Chuẩn bị Dữ liệu thật & Hàm đánh giá độc lập evaluate_route()"),
        ("Tình trạng nghiệm thu:", "100% HOÀN THÀNH (Đạt 16/16 tiêu chí, 36/36 tests PASSED)")
    ]
    meta_table.rows[0].cells[0].paragraphs[0].add_run("Đơn vị đề tài: ").bold = True
    meta_table.rows[0].cells[0].paragraphs[0].add_run("Nghiên cứu Khoa học GreenShip")
    meta_table.rows[0].cells[1].paragraphs[0].add_run("Nhóm thực hiện: ").bold = True
    meta_table.rows[0].cells[1].paragraphs[0].add_run("Nhóm Hải Thần (Ngũ, Nguyệt, Thùy)")
    meta_table.rows[1].cells[0].paragraphs[0].add_run("Giai đoạn: ").bold = True
    meta_table.rows[1].cells[0].paragraphs[0].add_run("STEP 2 (Dữ liệu thật & evaluate_route)")
    meta_table.rows[1].cells[1].paragraphs[0].add_run("Tiến độ: ").bold = True
    meta_table.rows[1].cells[1].paragraphs[0].add_run("100% HOÀN THÀNH (Sẵn sàng sang STEP 3)")
    
    for row in meta_table.rows:
        for cell in row.cells:
            set_cell_background(cell, HEX_LIGHT_BG)
            set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
    set_table_borders(meta_table)

    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_before = Pt(8)
    p_spacer.paragraph_format.space_after = Pt(8)

    # ==================== PHẦN 1 ====================
    add_heading_1("PHẦN 1: TÁC DỤNG VÀ CHỨC NĂNG CHI TIẾT CỦA CÁC HÀM TRONG SRC")
    
    p = doc.add_paragraph(
        "Thư mục src/ là nơi chứa toàn bộ mã nguồn phục vụ việc chuẩn bị dữ liệu, mô hình hóa hình học tuyến tàu, "
        "tra cứu thời tiết hải dương, kiểm định ràng buộc và thực thi hàm đánh giá lộ trình độc lập evaluate_route(). "
        "Tất cả các hàm được xây dựng theo kiến trúc mô-đun hóa cao, phân định trách nhiệm rõ ràng giữa các thành viên."
    )

    # --- Nhóm 1 ---
    add_heading_2("1. Nhóm Đánh giá Tuyến & Chi phí Vận hành – evaluator.py")
    doc.add_paragraph(
        "Tệp evaluator.py là mô-đun trung tâm quan trọng nhất của STEP 2, do Đặng Long Ngũ phụ trách chính. "
        "Mô-đun này xây dựng hàm đánh giá chi phí tuyến độc lập hoàn toàn với thuật toán tối ưu hóa (COA–RIME), "
        "đảm bảo tính tất định (deterministic), không dùng số ngẫu nhiên và phân rã chi tiết kết quả từng chặng."
    )

    eval_funcs = [
        ("evaluate_route(route, departure_utc, ship, weather, land, cfg)",
         "Hàm cốt lõi của STEP 2. Đánh giá toàn diện một tuyến hành trình: nhận vào danh sách waypoint, thời điểm khởi hành UTC, cấu hình tàu, nguồn dữ liệu thời tiết, mặt nạ đất và cấu hình ràng buộc. Hàm chia nhỏ tuyến thành các đoạn mẫu <= 5 NM, tra cứu thời tiết, cộng vector dòng chảy dọc tuyến vào SOG, tính thời gian, nhiên liệu, phát thải CO2 và kiểm tra ràng buộc. Trả về đối tượng kết quả phân rã chi tiết, cờ khả thi (feasible) và giá trị hàm mục tiêu (fitness)."),
        ("lay_gia_tri_tham_so(cau_hinh_tau, ten, don_vi, cho_phep_bang_khong)",
         "Đọc và thẩm định một tham số tàu từ tệp ship.json. Kiểm tra bắt buộc tính hợp lệ của đơn vị (kn, kW, g/kWh, tCO2/t-fuel) và miền giá trị hữu hạn, loại trừ lỗi nhập sai đơn vị vật lý."),
        ("doc_tham_so_tau(cau_hinh_tau)",
         "Đọc và xác thực trọn bộ tham số tàu mẫu (STW = 12 kn, Power = 5000 kW, SFOC = 190 g/kWh, CF = 3.114 tCO2/t-fuel) cho mô hình tiêu thụ nhiên liệu tối thiểu."),
        ("tinh_nhien_lieu_tan(cong_suat_kw, sfoc_g_kwh, thoi_gian_h)",
         "Tính lượng tiêu hao nhiên liệu theo công thức vật lý: Fuel (tấn) = (Công suất kW × SFOC g/kWh × Thời gian h) / 1,000,000. Có kiểm tra giá trị hữu hạn và không âm."),
        ("tinh_co2_tan(nhien_lieu_tan, he_so_phat_thai)",
         "Tính tổng phát thải CO2 ước tính (tank-to-wake) theo công thức: CO2 (tấn) = Nhiên liệu (tấn) × CF."),
        ("tinh_huong_don_vi(diem_dau, diem_cuoi)",
         "Tính vector đơn vị chỉ hướng hành trình của tàu (thành phần Đông và thành phần Bắc) trên mặt cầu tại từng phân đoạn."),
        ("tinh_dong_chay_doc_tuyen_kn(mau_thoi_tiet, diem_dau, diem_cuoi)",
         "Chiếu vector dòng chảy đại dương (uo, vo) lên vector hướng đi của tàu để tính thành phần dòng chảy dọc tuyến (u_along theo knots). Nếu dòng chảy thiếu hoặc không hợp lệ, trả về None."),
        ("goi_tra_cuu_thoi_tiet(nguon_thoi_tiet, vi_do, kinh_do, thoi_gian_utc)",
         "Hàm bao bọc (wrapper) gọi phương thức tra cứu thời tiết linh hoạt từ object KhoDuLieuThoiTiet hoặc hàm callable, tạo thuận lợi tối đa khi viết unit test."),
        ("tao_vi_pham_dau_vao(...) & tao_ket_qua_loi_dau_vao(...)",
         "Khởi tạo cấu trúc dữ liệu chuẩn báo lỗi cấu hình đầu vào (khi tàu thiếu tham số, tọa độ không hợp lệ hoặc dữ liệu cấu hình sai lệch)."),
        ("tao_bao_cao_danh_gia() & main()",
         "Thực thi đánh giá đồng loạt 3 tuyến thủ công (R01, R02, R03) và xuất kết quả phân rã chi tiết ra file outputs/evaluation_results.json.")
    ]

    for fname, fdesc in eval_funcs:
        p = doc.add_paragraph()
        run_name = p.add_run(f"• {fname}: ")
        run_name.bold = True
        run_name.font.color.rgb = COLOR_PRIMARY
        set_font_rfonts(run_name)
        run_desc = p.add_run(fdesc)
        set_font_rfonts(run_desc)

    # --- Nhóm 2 ---
    add_heading_2("2. Nhóm Hình học Tuyến & Kiểm tra Đất liền – route_geometry.py")
    doc.add_paragraph(
        "Tệp route_geometry.py do Đặng Long Ngũ và Nguyễn Phương Thùy phối hợp xây dựng. "
        "Mô-đun chịu trách nhiệm toàn bộ về các phép toán trắc địa ellipsoid WGS84, phân rã lấy mẫu và kiểm tra giao cắt đất liền."
    )

    geom_funcs = [
        ("kiem_tra_diem(kinh_do, vi_do)",
         "Kiểm tra và chuẩn hóa tọa độ điểm WGS84, bảo đảm vĩ độ thuộc [-90, 90] và kinh độ thuộc [-180, 180], giá trị phải là số thực hữu hạn."),
        ("doc_diem_tuyen(gia_tri) & doc_cac_tuyen(duong_dan)",
         "Đọc danh sách các tuyến từ tệp JSON data/routes/manual_routes.json, chuẩn hóa định dạng tọa độ [kinh độ, vĩ độ] và kiểm tra trùng lặp mã route_id."),
        ("tinh_khoang_cach_trac_dia_m(diem_dau, diem_cuoi)",
         "Tính khoảng cách trắc địa chính xác (mét) trên ellipsoid WGS84 bằng thuật toán lặp nghịch đảo Vincenty (nguyên mẫu trắc địa độ chính xác milimet)."),
        ("tinh_khoang_cach_trac_dia_nm(diem_dau, diem_cuoi)",
         "Quy đổi khoảng cách trắc địa WGS84 từ mét sang hải lý (Nautical Miles) theo quy chuẩn quốc tế: 1 NM = 1,852.0 m."),
        ("tinh_khoang_cach_haversine_m(diem_dau, diem_cuoi)",
         "Tính khoảng cách cung lớn trên hình cầu, dùng làm giải pháp dự phòng ổn định trong các tình huống thuật toán Vincenty không hội tụ."),
        ("chia_diem_tren_doan(...) & chia_diem_tren_tuyen(...)",
         "Thuật toán chia nhỏ một đoạn hành trình thành các điểm mẫu nội suy sao cho khoảng cách giữa hai điểm kế tiếp luôn <= 5 NM (theo tham số maximum_spacing_nm trong kịch bản)."),
        ("tinh_khoang_cach_tuyen_nm(cac_diem_tuyen)",
         "Tính tổng chiều dài toàn bộ hành trình bằng cách cộng dồn khoảng cách trắc địa WGS84 giữa các waypoint liên tiếp."),
        ("Lớp MatNaDatLien",
         "Lớp quản lý bộ polygon đất liền Natural Earth Land 5.1.1 (1:10m). Tích hợp các thuật toán: tạo hộp bao (bounding box) lọc nhanh, thuật toán Ray-Casting xác định điểm trong đa giác (diem_o_trong_vong), và thuật toán xác định giao cắt hai đoạn thẳng dựa trên hướng quay tích có hướng CCW (hai_doan_giao_nhau, doan_cat_dat)."),
        ("kiem_tra_tuyen_cat_dat(cac_diem_tuyen, mat_na_dat)",
         "Kiểm tra toàn diện tất cả các phân đoạn nối giữa các điểm mẫu với tập polygon đất liền để phát hiện hành trình vi phạm cắt đất."),
        ("danh_gia_hinh_hoc_tuyen(...) & tao_bao_cao()",
         "Tổng hợp toàn bộ chỉ số hình học của tuyến (tổng khoảng cách, số lượng đoạn, số điểm lấy mẫu, cờ cắt đất, danh sách đoạn vi phạm) và xuất file outputs/route_geometry.json.")
    ]

    for fname, fdesc in geom_funcs:
        p = doc.add_paragraph()
        run_name = p.add_run(f"• {fname}: ")
        run_name.bold = True
        run_name.font.color.rgb = COLOR_PRIMARY
        set_font_rfonts(run_name)
        run_desc = p.add_run(fdesc)
        set_font_rfonts(run_desc)

    # --- Nhóm 3 ---
    add_heading_2("3. Nhóm Tra cứu & Xử lý Dữ liệu Khí tượng Hải dương – weather.py, normalize_data.py, inspect_data.py")
    doc.add_paragraph(
        "Nhóm mô-đun này do Nguyễn Trần Như Nguyệt phụ trách chính, đảm nhận toàn bộ quy trình kiểm toán, "
        "chuẩn hóa và tra cứu dữ liệu thời tiết không gian 3 chiều (kinh độ, vĩ độ, thời gian)."
    )

    weather_funcs = [
        ("Lớp KhoDuLieuThoiTiet (trong weather.py)",
         "Lớp quản lý mở các tệp NetCDF (wind.nc, waves.nc, currents.nc) một lần duy nhất vào bộ nhớ và đóng tệp an toàn thông qua context manager (__enter__, __exit__), tối ưu hóa hiệu năng truy vấn liên tục."),
        ("KhoDuLieuThoiTiet.tra_cuu(...)",
         "Thực hiện truy vấn dữ liệu theo tọa độ và thời gian bằng phương pháp láng giềng gần nhất (nearest grid cell). Kiểm tra nghiêm ngặt phạm vi biên không gian và thời gian. Khi phát hiện ô sóng ven bờ bị NaN, tự động kích hoạt thuật toán tìm ô biển hợp lệ gần nhất trong bán kính <= 30 NM và ghi rõ khoảng cách tìm kiếm vào trường note."),
        ("KhoDuLieuThoiTiet.weather_at(...) & weather_at(...)",
         "Hàm giao diện tra cứu tổng hợp: trả về một từ điển chứa vận tốc gió Đông/Bắc (u10, v10), chiều cao sóng có nghĩa (swh), vận tốc dòng chảy (uo, vo), cờ dữ liệu hợp lệ (valid) và toàn bộ nguồn gốc metadata."),
        ("tinh_khoang_cach_cau_nm(...) & doi_sang_thoi_diem_utc(...)",
         "Các hàm tiện ích tính khoảng cách hình cầu phục vụ tìm kiếm ô biển hợp lệ và chuẩn hóa đối tượng thời gian sang múi giờ UTC chuẩn ISO-8601."),
        ("chuan_hoa_mot_bo(ten, dac_ta) (trong normalize_data.py)",
         "Chuẩn hóa dữ liệu thô NetCDF: đổi tên trục tọa độ về chuẩn thống nhất (time, latitude, longitude), sắp xếp tọa độ đơn điệu, giữ nguyên giá trị NaN (tuyệt đối không thay thế bằng 0), lưu ra thư mục data/processed/."),
        ("kiem_tra_tep(...) & ghi_hinh_kiem_tra(...) (trong inspect_data.py)",
         "Kiểm toán kích thước, số lượng chiều, số bước thời gian, độ phủ không gian và tỷ lệ ô thiếu missing của 4 nguồn dữ liệu; xuất kết quả ra outputs/data_audit.csv và outputs/data_audit_table.png.")
    ]

    for fname, fdesc in weather_funcs:
        p = doc.add_paragraph()
        run_name = p.add_run(f"• {fname}: ")
        run_name.bold = True
        run_name.font.color.rgb = COLOR_PRIMARY
        set_font_rfonts(run_name)
        run_desc = p.add_run(fdesc)
        set_font_rfonts(run_desc)

    # --- Nhóm 4 ---
    add_heading_2("4. Nhóm Phân loại Ràng buộc & Báo cáo Bảng biểu – constraints.py, result_table.py")
    doc.add_paragraph(
        "Mô-đun constraints.py do Nguyễn Phương Thùy phụ trách, định nghĩa hệ thống phân loại ràng buộc cứng/mềm "
        "và tệp result_table.py phụ trách trích xuất số liệu tổng hợp."
    )

    constraint_funcs = [
        ("tao_vi_pham(ma, phan_loai, thong_bao, chi_tiet, muc_do_chuan_hoa)",
         "Khởi tạo bản ghi vi phạm chuẩn hóa với mã vi phạm, phân loại (hard hoặc soft), thông điệp, ngữ cảnh chi tiết và độ nghiêm trọng chuẩn hóa trong đoạn [0.0, 1.0]."),
        ("tim_doan_gan_bang_khong(cac_diem_tuyen, nguong_nm)",
         "Phát hiện các cặp điểm liên tiếp trong lộ trình có khoảng cách gần bằng không (<= 1e-4 NM), cảnh báo điểm waypoint bị lặp."),
        ("kiem_tra_mau_thoi_tiet(cac_mau_thoi_tiet, cau_hinh_song)",
         "Kiểm tra điều kiện dữ liệu thời tiết bắt buộc: sinh vi phạm cứng MANDATORY_WEATHER_INVALID nếu thiếu gió/sóng hoặc ngoài biên; sinh vi phạm mềm/cứng WAVE_HEIGHT_EXCEEDED nếu chiều cao sóng swh vượt ngưỡng an toàn 3.0 m."),
        ("kiem_tra_rang_buoc(...)",
         "Đánh giá tổng hợp toàn bộ ràng buộc: Cắt đất (LAND_CROSSING - Hard), Bước lấy mẫu sai (SAMPLING_SPACING_INVALID - Hard), Lặp điểm (NEAR_ZERO_SEGMENT - Soft), Tuyến vòng quá mức (EXCESSIVE_DETOUR - Soft nếu dài hơn 1.05 lần baseline R01). Tuyến chỉ khả thi (feasible = True) khi không có bất kỳ vi phạm cứng nào."),
        ("tao_bang_ket_qua(...) & ve_bang_ket_qua(...) (trong result_table.py)",
         "Trích xuất số liệu đánh giá 3 tuyến từ evaluation_results.json, tổng hợp thành bảng đối chiếu rõ ràng và vẽ ảnh xuất bản outputs/tables/route_results.png, đồng thời xuất file CSV outputs/tables/route_results.csv.")
    ]

    for fname, fdesc in constraint_funcs:
        p = doc.add_paragraph()
        run_name = p.add_run(f"• {fname}: ")
        run_name.bold = True
        run_name.font.color.rgb = COLOR_PRIMARY
        set_font_rfonts(run_name)
        run_desc = p.add_run(fdesc)
        set_font_rfonts(run_desc)

    # --- Nhóm 5 ---
    add_heading_2("5. Nhóm Trực quan hóa & AI Reviewer Tự động – map_manual_routes.py, ai_agent_reviewer.py")
    doc.add_paragraph(
        "Nhóm mô-đun hỗ trợ trực quan hóa địa lý và hệ thống AI Agent kiểm định tự động chất lượng sản phẩm."
    )

    other_funcs = [
        ("map_domain.py & map_manual_routes.py",
         "Sử dụng matplotlib vẽ trực quan bản đồ miền nghiên cứu [105°E - 111°E, 9°N - 22°N], các điểm tiếp cận cảng và 3 tuyến thủ công R01 (xanh lá), R02 (đỏ - cắt đất), R03 (cam - ngoài khơi) trên nền đa giác bờ biển."),
        ("Lớp GreenShipReviewerAgent (trong ai_agent_reviewer.py)",
         "Agent tự động rà soát toàn bộ dự án: kiểm tra cấu trúc 14 thư mục bắt buộc, kiểm tra vòng lặp hình học tuyến và vòng lặp mô phỏng vật lý, tự động kích hoạt bộ 36 tests và chấm điểm 16 tiêu chí nghiệm thu của STEP 2."),
        ("Lớp GreenShipReporterAgent (trong ai_agent_reporter.py)",
         "Agent tổng hợp tiến độ tự động, trích xuất dữ liệu thực nghiệm và xuất báo cáo markdown chi tiết phục vụ nghiệm thu.")
    ]

    for fname, fdesc in other_funcs:
        p = doc.add_paragraph()
        run_name = p.add_run(f"• {fname}: ")
        run_name.bold = True
        run_name.font.color.rgb = COLOR_PRIMARY
        set_font_rfonts(run_name)
        run_desc = p.add_run(fdesc)
        set_font_rfonts(run_desc)

    # Spacer
    p_spacer2 = doc.add_paragraph()
    p_spacer2.paragraph_format.space_before = Pt(12)

    # ==================== PHẦN 2 ====================
    add_heading_1("PHẦN 2: BẢN CHẤT VÀ DANH MỤC TIÊU CHÍ NGHIỆM THU STEP 2")
    
    doc.add_paragraph(
        "Nghiệm thu STEP 2 là thủ tục đánh giá khoa học và kỹ thuật nhằm xác nhận việc hoàn thành toàn bộ "
        "giai đoạn chuẩn bị dữ liệu và đóng gói thành công hàm đánh giá chi phí tuyến độc lập evaluate_route(). "
        "Giai đoạn này là tiền đề bắt buộc trước khi bước vào STEP 3 (tối ưu hóa lộ trình bằng thuật toán Crayfish–RIME)."
    )

    add_callout(
        "Nguyên tắc cốt lõi của nghiệm thu STEP 2: Tuyệt đối không tuyên bố tuyến thủ công nào là tối ưu và "
        "không suy diễn mức tiết kiệm nhiên liệu hay CO2 khi chưa áp dụng thuật toán tối ưu. Tuyến R01 chỉ đóng vai trò "
        "là tuyến tham chiếu cơ sở (baseline candidate) để so sánh.",
        prefix="NGUYÊN TẮC NGHIỆM THU: "
    )

    add_heading_2("1. Bảng 16 Tiêu chí Nghiệm thu STEP 2 (Checklist Mục K Báo cáo)")
    doc.add_paragraph(
        "Bảng dưới đây liệt kê chi tiết 16 tiêu chí nghiệm thu bắt buộc theo yêu cầu của đề tài, "
        "kèm theo kết quả thẩm định và minh chứng kỹ thuật cụ thể đã đạt được trong dự án:"
    )

    # 16 Criteria Table
    criteria_data = [
        ("01", "Khóa kịch bản và tàu mẫu", "Khóa cặp cảng (Hải Phòng → Cái Mép), departure UTC (2024-10-10T00:00:00Z), phạm vi thời tiết [105-111°E, 9-22°N], tàu mẫu 40k DWT.", "ĐẠT", "config/scenario.yaml, config/ship.json"),
        ("02", "Dữ liệu thời tiết thật & đất liền", "Tải và mở được >= 1 file thời tiết thật và bộ polygon đất liền Natural Earth 5.1.1, có screenshot làm bằng chứng.", "ĐẠT", "data/processed/*.nc, data/land/, screenshots/"),
        ("03", "Danh mục nguồn (Source Register)", "Có source_register.csv đầy đủ metadata, URL, version, ngày giờ, biến, đơn vị, coverage không gian và thời gian.", "ĐẠT", "data/source_register.csv"),
        ("04", "Hàm tra cứu weather_at()", "Xử lý ô thiếu minh bạch (giữ NaN, không gán 0), out-of-range báo lỗi rõ, có fallback tìm ô biển gần nhất <= 30 NM cho sóng ven bờ.", "ĐẠT", "src/weather.py (KhoDuLieuThoiTiet.weather_at)"),
        ("05", "Biểu diễn >= 3 tuyến thủ công", "Biểu diễn ít nhất 03 tuyến thủ công dạng waypoint: R01 ven bờ, R02 cắt đất cố tình, R03 ngoài khơi.", "ĐẠT", "data/routes/manual_routes.json (R01, R02, R03)"),
        ("06", "Tính khoảng cách Geodesic WGS84", "Tính khoảng cách trắc địa theo NM bằng Vincenty, chia đoạn mẫu <= 5 NM, kiểm tra cắt đất theo từng đoạn thay vì chỉ ở waypoint.", "ĐẠT", "src/route_geometry.py (tinh_khoang_cach_trac_dia_nm)"),
        ("07", "Phân loại Hard / Soft Constraints", "Phân loại đúng: Hard (cắt đất, thiếu thời tiết bắt buộc, giãn cách sai) và Soft (vượt sóng, đường vòng, đoạn lặp gần 0).", "ĐẠT", "src/constraints.py (LAND_CROSSING, WAVE_EXCEEDED)"),
        ("08", "Nguồn gốc thông số tàu mẫu", "Thông số vận hành tàu (STW, Power, SFOC, CF) có nguồn trích dẫn hoặc nêu rõ là giả định mô hình (toy model assumption).", "ĐẠT", "config/ship.json (provenance: model_assumption)"),
        ("09", "Tính ổn định của evaluate_route()", "Hàm độc lập, tất định (deterministic), không dùng số ngẫu nhiên, không phụ thuộc COA–RIME, phân rã chi tiết từng segment.", "ĐẠT", "src/evaluator.py (evaluate_route)"),
        ("10", "Tính toán thời gian, nhiên liệu, CO2", "Tính toán thời gian (h), nhiên liệu (tấn), CO2 (tấn) có kiểm tra và bảo đảm đơn vị vật lý chặt chẽ.", "ĐẠT", "src/evaluator.py (tinh_nhien_lieu_tan, tinh_co2_tan)"),
        ("11", "Tính nhất quán của Baseline", "Không gọi đường Rhumb Line là ngắn nhất; mọi route được đánh giá bằng cùng một hàm evaluator thống nhất.", "ĐẠT", "R01 là baseline candidate, đánh giá chung hàm"),
        ("12", "Bộ kiểm thử tự động >= 10 tests", "Có >= 10 tests gồm thiếu dữ liệu và cắt đất; có log lưu kết quả thực thi (đạt 36/36 tests PASSED).", "ĐẠT", "36 tests PASS, lưu outputs/test_results.txt"),
        ("13", "Ví dụ tính tay 100 NM", "Có ví dụ tính tay trên giấy (100 NM, 10 kn, 1000 kW, SFOC 200 g/kWh -> 10 h, 2 t fuel, 6.228 t CO2) và đối chiếu khớp 100% bằng code.", "ĐẠT", "tests/test_evaluator.py::test_vi_du_tinh_tay_100_nm"),
        ("14", "Bản đồ trực quan & Bảng kết quả", "Có bản đồ 3 tuyến và bảng so sánh kết quả rõ ràng, không khẳng định tiết kiệm khi chưa tối ưu hóa.", "ĐẠT", "outputs/maps/manual_routes.png, route_results.csv"),
        ("15", "Tài liệu & Giới hạn mô hình", "Có README, cấu trúc dự án chuẩn, hướng dẫn chạy và tài liệu ghi nhận trung thực các giới hạn mô hình.", "ĐẠT", "README.md, reports/scenario_decisions.md"),
        ("16", "Nắm vững luồng dữ liệu & Báo cáo", "Toàn bộ thành viên giải thích được luồng dữ liệu và một lỗi minh họa cụ thể (R02 cắt đất). Báo cáo hoàn chỉnh.", "ĐẠT", "STEP2_Mau_bao_cao_Nhom_Hai_Than.docx, reports/")
    ]

    crit_table = doc.add_table(rows=len(criteria_data) + 1, cols=5)
    crit_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["STT", "Tiêu chí nghiệm thu", "Nội dung yêu cầu chi tiết", "Kết quả", "Minh chứng kỹ thuật"]
    
    # Format Header
    for col_idx, text in enumerate(headers):
        cell = crit_table.rows[0].cells[col_idx]
        set_cell_background(cell, HEX_PRIMARY)
        set_cell_margins(cell, top=140, bottom=140, left=120, right=120)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        run.bold = True
        run.font.color.rgb = RGBColor(255, 255, 255)
        set_font_rfonts(run)

    # Format Rows
    for row_idx, data in enumerate(criteria_data, start=1):
        row = crit_table.rows[row_idx]
        bg_color = HEX_ALT_ROW if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, text in enumerate(data):
            cell = row.cells[col_idx]
            set_cell_background(cell, bg_color)
            set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
            p = cell.paragraphs[0]
            if col_idx in (0, 3):
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(text)
            if col_idx == 3:
                run.bold = True
                run.font.color.rgb = RGBColor(0, 128, 0)
            elif col_idx == 0:
                run.bold = True
            set_font_rfonts(run)

    set_table_borders(crit_table)

    # Spacer
    p_spacer3 = doc.add_paragraph()
    p_spacer3.paragraph_format.space_before = Pt(12)

    # --- Thực nghiệm 3 tuyến ---
    add_heading_2("2. Kết quả Thực nghiệm Nghiệm thu trên 3 Tuyến Thủ công")
    doc.add_paragraph(
        "Hàm evaluate_route() đã thực hiện đánh giá độc lập 3 tuyến thủ công được thiết lập trong data/routes/manual_routes.json "
        "với cùng một mốc thời gian xuất phát 2024-10-10T00:00:00Z:"
    )

    route_summary_data = [
        ("R01", "Coastal baseline candidate", "779.602", "62.689", "59.555", "185.453", "CÓ", "0", "0", "59.555", "Tuyến thử khả thi; đóng vai trò là baseline tham chiếu."),
        ("R02", "Deliberate land-crossing test", "631.375", "52.372", "49.753", "154.932", "KHÔNG", "91", "0", "—", "Không khả thi; bị loại bỏ do cắt qua đất liền miền Trung và thiếu dữ liệu biển."),
        ("R03", "Offshore alternative candidate", "822.731", "68.036", "64.634", "201.271", "CÓ", "0", "1", "64.634", "Tuyến thử khả thi; ghi nhận 1 vi phạm mềm đường vòng (dài hơn 1.05 lần R01).")
    ]

    route_table = doc.add_table(rows=len(route_summary_data) + 1, cols=11)
    route_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    r_headers = ["Tuyến", "Tên tuyến", "Khoảng cách (NM)", "Thời gian (h)", "Nhiên liệu (tấn)", "CO2 (tấn)", "Khả thi", "Hard", "Soft", "Fitness", "Kết luận"]

    for col_idx, text in enumerate(r_headers):
        cell = route_table.rows[0].cells[col_idx]
        set_cell_background(cell, HEX_PRIMARY)
        set_cell_margins(cell, top=140, bottom=140, left=80, right=80)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor(255, 255, 255)
        set_font_rfonts(run)

    for row_idx, data in enumerate(route_summary_data, start=1):
        row = route_table.rows[row_idx]
        bg_color = HEX_ALT_ROW if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, text in enumerate(data):
            cell = row.cells[col_idx]
            set_cell_background(cell, bg_color)
            set_cell_margins(cell, top=90, bottom=90, left=70, right=70)
            p = cell.paragraphs[0]
            if col_idx in (0, 6, 7, 8):
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            elif col_idx in (2, 3, 4, 5, 9):
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(text)
            run.font.size = Pt(9.5)
            if col_idx == 6:
                run.bold = True
                run.font.color.rgb = RGBColor(0, 128, 0) if text == "CÓ" else RGBColor(192, 0, 0)
            set_font_rfonts(run)

    set_table_borders(route_table)

    # Spacer
    p_spacer4 = doc.add_paragraph()
    p_spacer4.paragraph_format.space_before = Pt(12)

    # --- Hình ảnh minh chứng ---
    add_heading_2("3. Hình ảnh và Minh chứng Trực quan Nghiệm thu")
    
    root_dir = Path(r"c:\Users\Admin\OneDrive\Desktop\GreenShip_STEP2")
    img_routes = root_dir / "outputs" / "maps" / "manual_routes.png"
    img_domain = root_dir / "outputs" / "maps" / "map_domain.png"
    img_table = root_dir / "outputs" / "tables" / "route_results.png"

    if img_routes.exists():
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(2)
        run_img = p_img.add_run()
        run_img.add_picture(str(img_routes), width=Inches(6.0))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(12)
        run_cap = p_cap.add_run("Hình 1: Bản đồ trực quan hóa 3 tuyến thủ công R01, R02 (cắt đất) và R03 trên nền địa hình biển Việt Nam")
        run_cap.font.italic = True
        run_cap.font.size = Pt(9.5)
        run_cap.font.color.rgb = COLOR_MUTED
        set_font_rfonts(run_cap)

    if img_table.exists():
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(2)
        run_img = p_img.add_run()
        run_img.add_picture(str(img_table), width=Inches(6.0))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(12)
        run_cap = p_cap.add_run("Hình 2: Bảng kết quả tổng hợp đánh giá 3 tuyến sinh tự động từ mô-đun result_table.py")
        run_cap.font.italic = True
        run_cap.font.size = Pt(9.5)
        run_cap.font.color.rgb = COLOR_MUTED
        set_font_rfonts(run_cap)

    # --- Kết luận nghiệm thu ---
    add_heading_2("4. Kết luận Nghiệm thu và Đề nghị Chuyển bước (STEP 3)")
    doc.add_paragraph(
        "1. Toàn bộ 16/16 tiêu chí nghiệm thu của giai đoạn STEP 2 đã được hoàn thành trọn vẹn 100%, "
        "đáp ứng đầy đủ các yêu cầu khắt khe về tính khoa học, độ chính xác số học và tính minh bạch của dữ liệu."
    )
    doc.add_paragraph(
        "2. Bộ kiểm thử tự động đạt 36/36 tests PASSED, vượt 360% chỉ tiêu tối thiểu (>= 10 tests), "
        "đảm bảo hàm evaluate_route() vận hành ổn định, sẵn sàng tích hợp trực tiếp vào thuật toán tối ưu hóa bầy đàn Crayfish–RIME ở STEP 3."
    )
    doc.add_paragraph(
        "3. Nhóm Hải Thần chính thức đề nghị Hội đồng Khoa học nghiệm thu hoàn thành giai đoạn STEP 2."
    )

    # Save document
    output_filename = "GreenShip_STEP2_Bao_cao_Chuc_nang_Ham_va_Nghiem_thu.docx"
    output_path = root_dir / output_filename
    doc.save(str(output_path))
    print(f"Report successfully saved to: {output_path}")
    return output_path

if __name__ == "__main__":
    create_report()
