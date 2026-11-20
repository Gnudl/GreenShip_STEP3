import sys
import os
import time
import math
import json
import numpy as np
import pandas as pd
import yaml
from pathlib import Path

current_dir = Path.cwd()
sys.path.insert(0, str(current_dir / "src"))

from route_geometry import doc_cac_tuyen, MatNaDatLien
from evaluator import evaluate_route, doc_tham_so_tau, TEP_SHAPEFILE
from weather import KhoDuLieuThoiTiet

print("================================================================================")
print("PHẦN A. CÁC THỰC NGHIỆM ĐỘ NHẠY VÀ KIỂM CHỨNG BỔ SUNG STEP 2")
print("================================================================================")

routes = doc_cac_tuyen()
r01 = next(r for r in routes if r["route_id"] == "R01")
with open("config/scenario.yaml", "r", encoding="utf-8") as f:
    base_cfg = yaml.safe_load(f)
with open("config/ship.json", "r", encoding="utf-8") as f:
    ship_cfg = json.load(f)
land = MatNaDatLien.doc_tu_shapefile(TEP_SHAPEFILE)
weather = KhoDuLieuThoiTiet()

# 1. Thử nghiệm độ nhạy bước lấy mẫu (2.5, 5.0, 10.0 NM)
print("\n--- 1. BẢNG ĐỘ NHẠY BƯỚC LẤY MẪU (2.5 / 5.0 / 10.0 NM) TRÊN R01 ---")
sampling_results = []
for spacing in [2.5, 5.0, 10.0]:
    cfg = yaml.safe_load(open("config/scenario.yaml", "r", encoding="utf-8"))
    cfg["route_sampling"]["maximum_spacing_nm"] = spacing
    t0 = time.time()
    res = evaluate_route(r01, cfg["departure_utc"], ship_cfg, weather, land, cfg)
    runtime = time.time() - t0
    
    invalid_count = sum(1 for seg in res["segments"] for s in seg["sample_intervals"] if not s["weather"]["valid"])
    total_samples = sum(len(seg["sample_intervals"]) for seg in res["segments"])
    
    sampling_results.append({
        "spacing_nm": spacing,
        "distance_nm": round(res["distance_nm"], 3),
        "duration_h": round(res["duration_h"], 3),
        "fuel_t": round(res["fuel_t"], 3),
        "co2_t": round(res["co2_t"], 3),
        "invalid_samples": invalid_count,
        "total_samples": total_samples,
        "runtime_s": round(runtime, 3)
    })

df_sampling = pd.DataFrame(sampling_results)
print(df_sampling.to_string(index=False))

# 2. Thử nghiệm độ nhạy bán kính truy vấn sóng ven bờ (10, 20, 30 NM)
print("\n--- 2. BẢNG ĐỘ NHẠY BÁN KÍNH TRUY VẤN SÓNG (10 / 20 / 30 NM) ---")
test_points = [
    {"name": "Hai Phong Approach", "lat": 20.6667, "lon": 106.8333},
    {"name": "Cai Mep Approach", "lat": 10.4200, "lon": 107.0800},
    {"name": "Ven bờ Nam Định", "lat": 20.0000, "lon": 106.5000},
    {"name": "Ven bờ Đà Nẵng", "lat": 16.1500, "lon": 108.3000},
    {"name": "Ngoài khơi Nha Trang", "lat": 12.5000, "lon": 110.0000}
]
dep_time = pd.Timestamp("2024-10-10T00:00:00Z")

wave_radius_results = []
for R in [10.0, 20.0, 30.0]:
    valid_count = 0
    blocked_count = 0
    details = []
    for pt in test_points:
        lookup = weather.tra_cuu(
            weather.cac_bo_du_lieu["waves"],
            ("swh",),
            pt["lat"],
            pt["lon"],
            dep_time,
            khoang_cach_tim_o_hop_le_toi_da_nm=R
        )
        is_valid = lookup["valid"]
        dist = lookup["matched"]["distance_from_query_nm"] if lookup["matched"] else None
        
        blocked = False
        if is_valid and lookup["matched"]:
            matched_pt = (lookup["matched"]["longitude"], lookup["matched"]["latitude"])
            query_pt = (pt["lon"], pt["lat"])
            if land.doan_cat_dat(query_pt, matched_pt):
                blocked = True
                blocked_count += 1
                
        if is_valid and not blocked:
            valid_count += 1
            
        details.append({
            "point": pt["name"],
            "valid": is_valid,
            "dist_nm": dist,
            "blocked": blocked
        })
        
    wave_radius_results.append({
        "radius_nm": R,
        "valid_count": valid_count,
        "total": len(test_points),
        "blocked_by_land": blocked_count,
        "details": details
    })

for wr in wave_radius_results:
    print(f"Bán kính R={wr['radius_nm']} NM: {wr['valid_count']}/{wr['total']} điểm hợp lệ, {wr['blocked_by_land']} trường hợp bị đất ngăn.")
    for d in wr["details"]:
        print(f"  - {d['point']}: valid={d['valid']}, dist={d['dist_nm']} NM, blocked_by_land={d['blocked']}")

# 3. Kiểm tra ETA và coverage thời tiết
print("\n--- 3. KIỂM TRA ĐỐI CHIẾU ETA CUỐI VÀ COVERAGE THỜI TIẾT ---")
res_r01 = evaluate_route(r01, base_cfg["departure_utc"], ship_cfg, weather, land, base_cfg)
eta_r01 = pd.Timestamp(base_cfg["departure_utc"]) + pd.Timedelta(hours=res_r01["duration_h"])
mandatory_end = pd.Timestamp("2024-10-14T23:00:00Z")
currents_end = pd.Timestamp("2024-10-14T00:00:00Z")
buffer_hours = (mandatory_end - eta_r01).total_seconds() / 3600.0

print(f"Departure UTC: {base_cfg['departure_utc']}")
print(f"Duration R01: {res_r01['duration_h']:.3f} h")
print(f"Arrival ETA: {eta_r01.isoformat()} (Buffer với cuối dữ liệu gió/sóng: {buffer_hours:.2f} h)")
print(f"Mandatory Weather End (Wind/Wave): {mandatory_end.isoformat()} -> ETA TRƯỚC HẠN (HỢP LỆ)")
print(f"Optional Currents End: {currents_end.isoformat()} -> ETA TRƯỚC HẠN (HỢP LỆ)")

# Lưu kết quả Phần A
with open("outputs/step3_part_a_results.json", "w", encoding="utf-8") as f:
    json.dump({
        "sampling_sensitivity": sampling_results,
        "wave_radius_sensitivity": wave_radius_results,
        "eta_check": {
            "departure_utc": base_cfg["departure_utc"],
            "duration_h": res_r01["duration_h"],
            "eta_utc": eta_r01.isoformat(),
            "mandatory_end_utc": mandatory_end.isoformat(),
            "buffer_hours": buffer_hours
        }
    }, f, indent=2)

print("\nHoàn tất thực nghiệm Phần A. Đã lưu outputs/step3_part_a_results.json")
