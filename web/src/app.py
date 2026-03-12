import os
import json
import joblib
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, jsonify

# Initialization
app = Flask(__name__)

# Base path for the application (e:\KU\KU3-2\ML\Project\Danger\web\src)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Model and Data Paths
MODEL_PATH = os.path.join(BASE_DIR, '..', '..', 'models', 'randomforest', 'animal_risk_model.pkl')
COLUMNS_PATH = os.path.join(BASE_DIR, '..', '..', 'models', 'randomforest', 'feature_columns.pkl')
ANIMAL_JSON_PATH = os.path.join(BASE_DIR, 'animal_groups_translation.json')
SYMPTOM_JSON_PATH = os.path.join(BASE_DIR, 'symptom_dictionary.json')

# Helper functions for data loading
def load_model_artifacts():
    try:
        model = joblib.load(MODEL_PATH)
        feature_columns = joblib.load(COLUMNS_PATH)
        return model, feature_columns
    except Exception as e:
        print(f"Error loading model: {e}")
        return None, None

def load_json_file(path):
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return {}

# Preload data
model, feature_columns = load_model_artifacts()
animal_data = load_json_file(ANIMAL_JSON_PATH)
symptom_data = load_json_file(SYMPTOM_JSON_PATH)

# Create lookup map: { 'หมา': 'Pets', 'วัว/โค': 'Livestock', ... }
species_to_group_map = {}
for g_key, g_info in animal_data.items():
    if 'members_th' in g_info:
        for species in g_info['members_th']:
            species_to_group_map[species] = g_key

@app.route('/')
def index():
    return render_template('index.html', 
                         animal_data=animal_data, 
                         symptom_data=symptom_data)

@app.route('/predict', methods=['POST'])
def predict():
    if model is None or feature_columns is None:
        return jsonify({'error': 'Machine learning model is not loaded correctly.'}), 500
        
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        selected_species = data.get('group') 
        selected_symptoms = data.get('symptoms', [])

        # --- ส่วนที่ 1: เตรียมข้อมูลแบบรวดเร็ว (Using Numpy for speed) ---
        # สร้าง array 0 ทั้งหมดตามจำนวน feature_columns
        input_values = np.zeros(len(feature_columns))
        
        # ค้นหา index ของ feature_columns เพื่อประหยัดเวลา
        col_to_idx = {col: i for i, col in enumerate(feature_columns)}

        # 1.1 Species to Group Mapping
        actual_group_key = species_to_group_map.get(selected_species)
        if actual_group_key:
            group_col = f"Group_{actual_group_key}"
            if group_col in col_to_idx:
                input_values[col_to_idx[group_col]] = 1
        
        # 1.2 Symptom Mapping
        valid_symptoms_count = 0
        if isinstance(selected_symptoms, list):
            for symptom in selected_symptoms:
                if symptom in col_to_idx:
                    input_values[col_to_idx[symptom]] = 1
                    valid_symptoms_count += 1

        # แปลงเป็น DataFrame แถวเดียว
        input_df = pd.DataFrame([input_values], columns=feature_columns)

        # --- ส่วนที่ 2: การทำนายและการปรับจูน (The Magic Sauce) ---
        probs = model.predict_proba(input_df)
        raw_risk = float(probs[0][1]) # ค่า 0.0 - 1.0

        # >> เทคนิค A: Symptom Booster (ยิ่งเยอะ ยิ่งเสี่ยงเพิ่ม)
        # บวกเพิ่มอาการละ 1.5% ถ้ามีหลายอาการ (แต่ไม่เกิน 1.0)
        booster = 0
        if valid_symptoms_count > 1:
            booster = (valid_symptoms_count - 1) * 0.015
        
        # >> เทคนิค B: Calibration (ดัดกราฟให้ดูสมจริง)
        # ถ้าความเสี่ยงสูงเกิน 70% แต่มีอาการเดียว ให้ลดลงมานิดหน่อยเพื่อไม่ให้ User ช็อก
        if valid_symptoms_count == 1 and raw_risk > 0.70:
            adjusted_risk = raw_risk * 0.85 # ลดความตระหนกลง 15%
        else:
            adjusted_risk = raw_risk + booster

        # คุมสเกลสุดท้ายให้อยู่ในช่วง 0 - 100
        final_score = round(min(0.995, adjusted_risk) * 100, 2)

        return jsonify({
            'risk_score': final_score,
            'symptoms_analyzed': valid_symptoms_count,
            'base_model_score': round(raw_risk * 100, 2) # ส่งค่าจริงไปเก็บ Log (Optional)
        })

    except Exception as e:
        print(f"Prediction error: {e}")
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)