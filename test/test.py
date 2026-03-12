import joblib
import pandas as pd
import numpy as np
import os

# 1. กำหนด Path (ปรับตามตำแหน่งที่คุณอยู่)
BASE_DIR = os.getcwd() # หรือกำหนดเอง เช่น 'E:/KU/KU3-2/ML/Project/Danger'
model_path = os.path.abspath(os.path.join(BASE_DIR, '..', 'models', 'randomforest', 'animal_risk_model.pkl'))
feature_path = os.path.abspath(os.path.join(BASE_DIR, '..', 'models', 'randomforest', 'feature_columns.pkl'))
# 2. โหลดโมเดลและคอลัมน์
model = joblib.load(model_path)
feature_columns = joblib.load(feature_path)

def predict_real_case(animal_group, symptoms_list):
    # สร้าง DataFrame เปล่า
    input_data = pd.DataFrame(0, index=[0], columns=feature_columns)
    
    # 1. จัดการกลุ่มสัตว์ (ต้องพิมพ์ให้ตรงกับที่ทำ One-Hot ไว้)
    group_col = f'Group_{animal_group}'
    if group_col in feature_columns:
        input_data[group_col] = 1
    else:
        print(f"❌ ไม่พบกลุ่มสัตว์: {group_col}")

    # 2. จัดการอาการ (ปรับให้ยืดหยุ่นขึ้น)
    for sym in symptoms_list:
        # ลองเดารูปแบบชื่อที่อาจจะเป็นไปได้
        possible_names = [f'sym_{sym}', sym, sym.replace(' ', '_'), f'sym_{sym.replace(" ", "_")}']
        
        found = False
        for name in possible_names:
            if name in feature_columns:
                input_data[name] = 1
                print(f"✅ จับคู่สำเร็จ: {sym} -> {name}")
                found = True
                break
        
        if not found:
            print(f"⚠️ ไม่พบอาการ '{sym}' ใน Feature Columns ของโมเดล")

    # 3. ทำนาย
    prob = model.predict_proba(input_data)[0]
    return prob[1] * 100
# ---------------------------------------------------------
# 🧪 ทดสอบจริง: เปรียบเทียบจุดอ่อน (Weakness Test)
# ---------------------------------------------------------

# เคสที่ 1: สัตว์ปศุสัตว์ (Livestock) มีอาการท้องเสีย
risk_livestock = predict_real_case('Livestock', ['fever'])

# เคสที่ 2: สัตว์ป่าขนาดใหญ่ (Wild_Large) มีอาการท้องเสีย
risk_wild = predict_real_case('Wild_Large', ['fever'])

print("🔍 --- ผลการทดสอบการทำนายจริง ---")
print(f"🐄 กลุ่ม Livestock  (อาการ: fever): ความเสี่ยง {risk_livestock:.2f}%")
print(f"🐘 กลุ่ม Wild_Large (อาการ: fever): ความเสี่ยง {risk_wild:.2f}%")

# วิเคราะห์ผล
diff = abs(risk_livestock - risk_wild)
if diff > 0:
    winner = "Livestock" if risk_livestock > risk_wild else "Wild_Large"
    print(f"\n💡 วิเคราะห์: โมเดลมองว่ากลุ่ม {winner} มีความเปราะบางต่ออาการนี้มากกว่า ({diff:.2f}%)")
else:
    print("\n💡 วิเคราะห์: โมเดลมองว่าอาการนี้อันตรายเท่ากันในทั้งสองกลุ่ม")