import os
import json
import joblib
import pandas as pd
import numpy as np
import sys

# Set output to UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Setup paths
BASE_DIR = r"e:\KU\KU3-2\ML\Project\Danger\web\src"
MODEL_PATH = os.path.join(BASE_DIR, '..', '..', 'models', 'randomforest', 'animal_risk_model.pkl')
COLUMNS_PATH = os.path.join(BASE_DIR, '..', '..', 'models', 'randomforest', 'feature_columns.pkl')
ANIMAL_JSON_PATH = os.path.join(BASE_DIR, 'animal_groups_translation.json')
SYMPTOM_JSON_PATH = os.path.join(BASE_DIR, 'symptom_dictionary.json')

# Load artifacts
model = joblib.load(MODEL_PATH)
feature_columns = joblib.load(COLUMNS_PATH)
with open(ANIMAL_JSON_PATH, 'r', encoding='utf-8') as f:
    animal_data = json.load(f)
with open(SYMPTOM_JSON_PATH, 'r', encoding='utf-8') as f:
    symptom_data = json.load(f)

species_to_group_map = {}
for g_key, g_info in animal_data.items():
    if 'members_th' in g_info:
        for species in g_info['members_th']:
            species_to_group_map[species] = g_key

col_to_idx = {col: i for i, col in enumerate(feature_columns)}

def predict_mock(selected_species, selected_symptoms):
    input_values = np.zeros(len(feature_columns))
    
    actual_group_key = species_to_group_map.get(selected_species)
    if actual_group_key:
        group_col = f"Group_{actual_group_key}"
        if group_col in col_to_idx:
            input_values[col_to_idx[group_col]] = 1
    
    valid_symptoms_count = 0
    for symptom in selected_symptoms:
        if symptom in col_to_idx:
            input_values[col_to_idx[symptom]] = 1
            valid_symptoms_count += 1

    input_df = pd.DataFrame([input_values], columns=feature_columns)
    probs = model.predict_proba(input_df)
    raw_risk = float(probs[0][1])

    booster = 0
    if valid_symptoms_count > 1:
        booster = (valid_symptoms_count - 1) * 0.015
    
    if valid_symptoms_count == 1 and raw_risk > 0.70:
        adjusted_risk = raw_risk * 0.85
    else:
        adjusted_risk = raw_risk + booster

    final_score = round(min(0.995, adjusted_risk) * 100, 2)
    return final_score, valid_symptoms_count, raw_risk

# Test cases
test_cases = [
    ("สุนัขพันทาง", ["sneezing"]),
    ("สุนัขพันทาง", ["hair loss"]),
    ("สุนัขพันทาง", ["dandruff"]),
    ("แมวไทย", ["mild sneezing"]),
    ("ปลาทอง", ["willnot run to jump"]),
]

print(f"{'Species':<20} | {'Symptoms':<25} | {'Raw':<6} | {'Final':<6} | {'Status'}")
print("-" * 85)

for species, symptoms in test_cases:
    score, count, raw = predict_mock(species, symptoms)
    status = "Normal"
    if score >= 70: status = "Critical"
    elif score >= 35: status = "Warning"
    
    sym_str = ", ".join(symptoms)
    print(f"{species:<20} | {sym_str:<25} | {raw:<6.3f} | {score:<6.2f} | {status}")
