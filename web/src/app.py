import os
import json
import joblib
import pandas as pd
from flask import Flask, render_template, request, jsonify

# Initialization
app = Flask(__name__)

# Base path for the application (e:\KU\KU3-2\ML\Project\Danger\web\src)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Model and Data Paths
MODEL_PATH = os.path.join(BASE_DIR, '..', 'models', 'randomforest', 'animal_risk_model.pkl')
COLUMNS_PATH = os.path.join(BASE_DIR, '..', 'models', 'randomforest', 'feature_columns.pkl')
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
            
        selected_symptoms = data.get('symptoms', [])

        # Create input DataFrame with all zeros
        # Feature columns do not have 'sym_' or 'Group_' prefix based on model inspection
        input_df = pd.DataFrame(0, index=[0], columns=feature_columns)

        # Set 1 for selected symptoms
        if isinstance(selected_symptoms, list):
            for symptom in selected_symptoms:
                if symptom in input_df.columns:
                    input_df.at[0, symptom] = 1

        # Predict probability of the "Dangerous" class
        # predict_proba returns [prob_class_0, prob_class_1]
        probs = model.predict_proba(input_df)
        risk_score = round(float(probs[0][1]) * 100, 2)

        return jsonify({
            'risk_score': risk_score
        })

    except Exception as e:
        print(f"Prediction error: {e}")
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    # Running in debug mode for development
    app.run(debug=True)