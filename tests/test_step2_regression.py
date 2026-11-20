import pytest
import json
import yaml
from pathlib import Path
import pandas as pd
from src.evaluator import doc_tham_so_tau, lay_gia_tri_tham_so, evaluate_route, MatNaDatLien, TEP_SHAPEFILE
from src.weather import KhoDuLieuThoiTiet
from src.route_geometry import doc_cac_tuyen

def test_power_positive_validation():
    # Power = 0 must raise ValueError in engine-driven vessel mode
    ship_zero = {
        "parameters": {
            "speed_through_water_kn": {"value": 12.0, "unit": "kn"},
            "service_power_kw": {"value": 0.0, "unit": "kW"},
            "sfoc_g_per_kwh": {"value": 190.0, "unit": "g/kWh"},
            "co2_emission_factor_t_per_t_fuel": {"value": 3.114, "unit": "tCO2/t-fuel"}
        }
    }
    with pytest.raises(ValueError):
        lay_gia_tri_tham_so(ship_zero, "service_power_kw", "kW", cho_phep_bang_khong=False)

def test_power_negative_validation():
    ship_neg = {
        "parameters": {
            "speed_through_water_kn": {"value": 12.0, "unit": "kn"},
            "service_power_kw": {"value": -1.0, "unit": "kW"},
            "sfoc_g_per_kwh": {"value": 190.0, "unit": "g/kWh"},
            "co2_emission_factor_t_per_t_fuel": {"value": 3.114, "unit": "tCO2/t-fuel"}
        }
    }
    with pytest.raises(ValueError):
        lay_gia_tri_tham_so(ship_neg, "service_power_kw", "kW", cho_phep_bang_khong=False)

def test_eta_coverage_buffer():
    # ETA of R01 must precede mandatory dataset coverage
    routes = doc_cac_tuyen()
    r01 = next(r for r in routes if r["route_id"] == "R01")
    cfg = yaml.safe_load(open("config/scenario.yaml", "r", encoding="utf-8"))
    ship = json.load(open("config/ship.json", "r", encoding="utf-8"))
    land = MatNaDatLien.doc_tu_shapefile(TEP_SHAPEFILE)
    weather = KhoDuLieuThoiTiet()
    
    res = evaluate_route(r01, cfg["departure_utc"], ship, weather, land, cfg)
    eta = pd.Timestamp(cfg["departure_utc"]) + pd.Timedelta(hours=res["duration_h"])
    mandatory_end = pd.Timestamp("2024-10-14T23:00:00Z")
    assert eta < mandatory_end
    # Buffer is >= 50 hours
    assert (mandatory_end - eta).total_seconds() / 3600.0 >= 50.0
