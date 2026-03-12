import customtkinter as ctk
import joblib
import pandas as pd
import json
import os

# --- Themes ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AnimalRiskDesktopApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Animal Health Risk AI - Desktop")
        self.geometry("750x950")

        # --- Path Management ---
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Paths based on "run from app/ but load from ../models/"
        model_path = os.path.join(self.base_dir, '..', 'models', 'randomforest', 'animal_risk_model.pkl')
        feature_path = os.path.join(self.base_dir, '..', 'models', 'randomforest', 'feature_columns.pkl')
        
        # Load local JSONs (or from test if not in app/)
        animal_json = os.path.join(self.base_dir, 'animal_groups_translation.json')
        symptom_json = os.path.join(self.base_dir, 'symptom_dictionary.json')
        
        # Fallback to web/src if not found in app/ (during setup)
        if not os.path.exists(animal_json):
            animal_json = os.path.join(self.base_dir, '..', 'web', 'src', 'animal_groups_translation.json')
        if not os.path.exists(symptom_json):
            symptom_json = os.path.join(self.base_dir, '..', 'web', 'src', 'symptom_dictionary.json')

        # Load artifacts
        try:
            self.model = joblib.load(model_path)
            self.features = joblib.load(feature_path)
            
            with open(animal_json, 'r', encoding='utf-8') as f:
                self.animal_data = json.load(f)
            with open(symptom_json, 'r', encoding='utf-8') as f:
                self.symptom_dict = json.load(f)
            
            # Species mapping: { 'Dog': 'Pets', ... }
            self.species_to_group = {}
            self.all_species = []
            for g_key, g_info in self.animal_data.items():
                if 'members_th' in g_info:
                    for species in g_info['members_th']:
                        self.species_to_group[species] = g_key
                        self.all_species.append(species)
            
            print(f"✅ Loaded {len(self.features)} features and {len(self.all_species)} species.")
        except Exception as e:
            self.show_error(f"Error loading system files:\n{e}")
            return

        self.setup_ui()

    def show_error(self, message):
        err_label = ctk.CTkLabel(self, text=message, text_color="#ff4757", font=("Sarabun", 16))
        err_label.pack(pady=100)

    def setup_ui(self):
        # Header
        self.label_title = ctk.CTkLabel(self, text="🩺 AI วิเคราะห์ความเสี่ยงสุขภาพสัตว์", 
                                        font=("Sarabun", 28, "bold"), text_color="#00d2ff")
        self.label_title.pack(pady=20)

        # 1. Species Selection
        group_frame = ctk.CTkFrame(self)
        group_frame.pack(fill="x", pady=10, padx=30)
        
        self.label_group = ctk.CTkLabel(group_frame, text="1. เลือกชนิดสัตว์:", font=("Sarabun", 16, "bold"))
        self.label_group.pack(pady=(10, 5))
        
        self.combo_species = ctk.CTkComboBox(group_frame, values=sorted(self.all_species), width=500, font=("Sarabun", 14))
        self.combo_species.set("--- ค้นหาหรือเลือกชนิดสัตว์ ---")
        self.combo_species.pack(pady=(5, 15))

        # 2. Symptoms + Search
        sym_frame = ctk.CTkFrame(self)
        sym_frame.pack(fill="both", expand=True, pady=10, padx=30)

        self.label_sym = ctk.CTkLabel(sym_frame, text="2. ค้นหาอาการที่พบ:", font=("Sarabun", 16, "bold"))
        self.label_sym.pack(pady=(10, 5))

        # Search Box
        self.search_entry = ctk.CTkEntry(sym_frame, placeholder_text="พิมพ์เพื่อค้นหาอาการ...", width=500, font=("Sarabun", 14))
        self.search_entry.pack(pady=5)
        self.search_entry.bind("<KeyRelease>", self.filter_symptoms)

        self.scroll_frame = ctk.CTkScrollableFrame(sym_frame, height=400)
        self.scroll_frame.pack(fill="both", expand=True, pady=10, padx=10)

        self.symptom_vars = {}
        self.checkboxes = {}
        
        sorted_symptoms = sorted(self.symptom_dict.items(), key=lambda x: x[1])
        for eng, th in sorted_symptoms:
            var = ctk.BooleanVar()
            cb = ctk.CTkCheckBox(self.scroll_frame, text=f"{th} ({eng})", variable=var, font=("Sarabun", 13))
            cb.pack(pady=3, anchor="w", padx=15)
            self.symptom_vars[eng] = var
            self.checkboxes[eng] = cb

        # Buttons
        self.btn_predict = ctk.CTkButton(self, text="วิเคราะห์ระดับความเสี่ยง", command=self.predict_risk, 
                                         fg_color="#1a73e8", hover_color="#1557b0", 
                                         font=("Sarabun", 18, "bold"), height=55)
        self.btn_predict.pack(pady=20, padx=30, fill="x")

        # Results
        self.res_frame = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=15)
        self.res_frame.pack(pady=10, padx=30, fill="x")

        self.result_label = ctk.CTkLabel(self.res_frame, text="กรุณาใส่ข้อมูลเพื่อเริ่มการวิเคราะห์", font=("Sarabun", 18))
        self.result_label.pack(pady=(15, 0))
        
        self.score_label = ctk.CTkLabel(self.res_frame, text="", font=("Sarabun", 56, "bold"))
        self.score_label.pack(pady=(0, 15))

    def filter_symptoms(self, event=None):
        query = self.search_entry.get().lower()
        for eng, cb in self.checkboxes.items():
            th = self.symptom_dict[eng].lower()
            if query in eng.lower() or query in th:
                cb.pack(pady=3, anchor="w", padx=15)
            else:
                cb.pack_forget()

    def predict_risk(self):
        selected_species = self.combo_species.get()
        actual_group = self.species_to_group.get(selected_species)
        selected_symptoms = [sym for sym, var in self.symptom_vars.items() if var.get()]

        if not actual_group:
            self.result_label.configure(text="❌ โปรดเลือกชนิดสัตว์ที่ถูกต้อง!", text_color="#ff4757")
            return

        # Prepare 0-initialized DataFrame
        input_data = {col: [0] for col in self.features}
        input_df = pd.DataFrame(input_data)
        
        # Group mapping
        group_col = f'Group_{actual_group}'
        if group_col in input_df.columns:
            input_df.at[0, group_col] = 1
            
        # Symptoms mapping
        for sym in selected_symptoms:
            if sym in input_df.columns:
                input_df.at[0, sym] = 1

        try:
            input_df = input_df[self.features] # Maintain order
            probs = self.model.predict_proba(input_df)[0][1]
            score = round(probs * 100, 2)

            # Colors
            if score >= 75:
                color = "#ff4d4d"; status = "วิกฤต (Critical Risk)"
            elif score >= 40:
                color = "#ffa502"; status = "อันตราย/เฝ้าระวัง (Warning)"
            else:
                color = "#2ed573"; status = "ระดับปกติ (Normal)"

            self.result_label.configure(text=status, text_color=color)
            self.score_label.configure(text=f"{score}%", text_color=color)
        except Exception as e:
            self.result_label.configure(text=f"Error: {e}", text_color="white")

if __name__ == "__main__":
    app = AnimalRiskDesktopApp()
    app.mainloop()
