import docx
import pandas as pd
import json

doc = docx.Document('STEP3_Bao_cao_Nhom_Hai_Than_Da_dien.docx')

print('=== KIỂM TRA LẦN 2: ĐỐI CHIẾU SỐ LIỆU BẢNG BƯỚC MẪU (TABLE 3) ===')
t3 = doc.tables[3]
with open('outputs/step3_part_a_results.json', 'r', encoding='utf-8') as f:
    real_a = json.load(f)['sampling_sensitivity']

for i in range(1, 4):
    row_text = [c.text.strip() for c in t3.rows[i].cells]
    expected = real_a[i-1]
    print(f"Hàng {i} (Bước {row_text[0]} NM): Distance={row_text[1]} (Gốc={expected['distance_nm']}), Time={row_text[2]} (Gốc={expected['duration_h']}), Fuel={row_text[3]} (Gốc={expected['fuel_t']})")

print('\n=== ĐỐI CHIẾU SỐ LIỆU BẢNG BENCHMARK (TABLE 12) ===')
t12 = doc.tables[12]
df_bench = pd.read_csv('outputs/benchmark_results_step3.csv')
for i in range(1, 7):
    row_text = [c.text.strip() for c in t12.rows[i].cells]
    row_bench = df_bench.iloc[i-1]
    m_exp = f"{row_bench['Mean']:.6f}"
    s_exp = f"{row_bench['Std']:.6f}"
    print(f"Hàng {i} ({row_text[0]}): Mean={row_text[1]} (Gốc={m_exp}), Std={row_text[2]} (Gốc={s_exp})")
