
import os
import json
import joblib
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Load Symptom Dictionary
def load_symptoms():
    dict_path = os.path.join(os.path.dirname(__file__), 'symptom_dictionary.json')
    if not os.path.exists(dict_path):
        # Fallback to data dir if not in src
        dict_path = os.path.join(DATA_DIR, 'symptom_dictionary.json')
    
    with open(dict_path, 'r', encoding='utf-8') as f:
        sym_dict = json.load(f)
    
    # Flip the dictionary: Thai -> English
    thai_to_eng = {v: k for k, v in sym_dict.items()}
    return sym_dict, thai_to_eng

SYMPTOM_DICT, THAI_TO_ENG = load_symptoms()

# Model Cache
MODELS = {}
FEATURES = {}

def get_model(model_name):
    if model_name in MODELS:
        return MODELS[model_name], FEATURES[model_name]
    
    model_path = os.path.join(MODELS_DIR, model_name)
    if not os.path.exists(model_path):
        return None, None
    
    try:
        # Search for any .pkl file that might be the model
        model_files = [f for f in os.listdir(model_path) if f.endswith('.pkl') and 'feature' not in f]
        if not model_files:
            return None, None
            
        model = joblib.load(os.path.join(model_path, model_files[0]))
        features = joblib.load(os.path.join(model_path, 'feature_columns.pkl'))
        MODELS[model_name] = model
        FEATURES[model_name] = features
        return model, features
    except Exception as e:
        print(f"Error loading model {model_name}: {e}")
        return None, None

@app.route('/')
def home():
    # Sort symptoms for dropdown
    thai_symptoms = sorted(THAI_TO_ENG.keys())
    return render_template('index.html', symptoms=thai_symptoms)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    selected_thai_symptoms = data.get('symptoms', [])
    model_name = data.get('model', 'randomforest')
    
    model, feature_columns = get_model(model_name)
    if model is None:
        return jsonify({'error': f'Model {model_name} not found'}), 404
    
    # Map selected Thai symptoms to English keys
    selected_eng_symptoms = [THAI_TO_ENG[s] for s in selected_thai_symptoms if s in THAI_TO_ENG]
    
    # Create input vector
    input_df = pd.DataFrame(np.zeros((1, len(feature_columns))), columns=feature_columns)
    for sym in selected_eng_symptoms:
        if sym in input_df.columns:
            input_df[sym] = 1
            
    # Predict
    prediction = model.predict(input_df)[0]
    probabilities = []
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(input_df)[0].tolist()

    result = {
        'prediction': int(prediction),
        'prediction_label': 'Dangerous' if prediction == 1 else 'Normal',
        'confidence': max(probabilities) if probabilities else None,
        'all_probs': probabilities
    }
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
