import os
import shutil
import subprocess
from pathlib import Path

step2_dir = Path(r"C:\Users\Admin\OneDrive\Desktop\GreenShip_STEP2")
step3_dir = Path(r"C:\Users\Admin\OneDrive\Desktop\Bao_Cao_NCKH\step3")

print(f"Creating STEP 3 structure in: {step3_dir}")

# 1. Directories to create
dirs = [
    "config",
    "data/processed",
    "data/land",
    "data/routes",
    "src/optimizers",
    "benchmarks",
    "scripts",
    "tests",
    "outputs/maps",
    "outputs/tables",
    "reports"
]

for d in dirs:
    (step3_dir / d).mkdir(parents=True, exist_ok=True)
    print(f"  + Created: {d}")

# 2. Copy config
shutil.copy2(step2_dir / "config" / "scenario.yaml", step3_dir / "config" / "scenario.yaml")
shutil.copy2(step2_dir / "config" / "ship.json", step3_dir / "config" / "ship.json")
print("  + Copied config files.")

# 3. Copy data
if (step2_dir / "data" / "source_register.csv").exists():
    shutil.copy2(step2_dir / "data" / "source_register.csv", step3_dir / "data" / "source_register.csv")

# Copy processed netcdf
for f in (step2_dir / "data" / "processed").glob("*.nc"):
    shutil.copy2(f, step3_dir / "data" / "processed" / f.name)

# Copy land shapefiles
land_src = step2_dir / "data" / "land" / "ne_10m_land"
land_dst = step3_dir / "data" / "land" / "ne_10m_land"
if land_src.exists():
    shutil.copytree(land_src, land_dst, dirs_exist_ok=True)

# Copy routes
for f in (step2_dir / "data" / "routes").glob("*.json"):
    shutil.copy2(f, step3_dir / "data" / "routes" / f.name)

print("  + Copied data files (processed NC, land polygons, routes).")

# 4. Copy STEP 2 locked source files into src/
src_files = ["weather.py", "route_geometry.py", "constraints.py", "evaluator.py", "map_domain.py", "map_manual_routes.py", "result_table.py"]
for sf in src_files:
    if (step2_dir / "src" / sf).exists():
        shutil.copy2(step2_dir / "src" / sf, step3_dir / "src" / sf)
print("  + Copied base modules into src/.")

# 5. Move/Copy Word reports into reports/
for doc_file in step3_dir.glob("*.docx"):
    shutil.copy2(doc_file, step3_dir / "reports" / doc_file.name)
print("  + Synchronized Word reports into reports/.")

# 6. Copy output results
output_files = [
    "benchmark_results_step3.csv",
    "benchmark_convergence_step3.png",
    "Ban_do_ba_tuyen_Hs.png",
    "step3_part_a_results.json",
    "step3_trace_results.json"
]
for of in output_files:
    if (step2_dir / "outputs" / of).exists():
        shutil.copy2(step2_dir / "outputs" / of, step3_dir / "outputs" / of)
    elif (step2_dir / of).exists():
        shutil.copy2(step2_dir / of, step3_dir / "outputs" / of)
print("  + Copied benchmark and sensitivity outputs.")

print("STEP 3 basic directory structure initialized successfully.")
