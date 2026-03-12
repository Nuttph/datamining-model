import joblib
import json
import os

# 1. Path ของไฟล์
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
feature_path = os.path.join(BASE_DIR, '..', 'models', 'randomforest', 'feature_columns.pkl')

try:
    feature_columns = joblib.load(feature_path)
    
    # 2. คัดออกเฉพาะคอลัมน์ที่ขึ้นต้นด้วย 'Group_' 
    # อะไรที่ไม่ใช่ Group_ เราจะตีว่าเป็น "อาการ" (Symptoms) ทั้งหมด
    symptom_list = [col for col in feature_columns if not col.startswith('Group_')]
    
    # 3. สร้าง Dictionary
    symptom_dict = {}
    for sym in symptom_list:
        # เก็บชื่อต้นฉบับไว้เป็น Key (ห้ามแก้) และ Value (รอแปลไทย)
        symptom_dict[sym] = sym 

    # 4. บันทึกไฟล์
    output_path = os.path.join(BASE_DIR, 'symptom_dictionary.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(symptom_dict, f, indent=4, ensure_ascii=False)

    print(f"✅ แก้ไขสำเร็จ! สร้างไฟล์ที่: {output_path}")
    print(f"📊 พบอาการทั้งหมด {len(symptom_dict)} รายการ")
    
    # ลอง Print ดู 5 อันแรกเพื่อเช็คหน้าตาชื่อ
    print(f"ตัวอย่างชื่ออาการที่พบ: {symptom_list[:5]}")

except Exception as e:
    print(f"❌ Error: {e}")