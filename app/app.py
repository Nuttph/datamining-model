import customtkinter as ctk
import joblib
import pandas as pd
import json
import os

# --- ตั้งค่าธีมหน้าจอ ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AnimalRiskApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Animal Health Risk AI - Desktop Version")
        self.geometry("600x850")

        # --- จัดการ Path ไฟล์ (อิงจากตำแหน่งไฟล์ app.py) ---
        # BASE_DIR คือโฟลเดอร์ E:\...\Danger\app
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 1. โหลด Model: ถอยหลัง 1 ชั้น (..) ออกไป Danger แล้วเข้า models/
        model_path = os.path.join(self.base_dir, '..', 'models', 'randomforest', 'animal_risk_model.pkl')
        feature_path = os.path.join(self.base_dir, '..', 'models', 'randomforest', 'feature_columns.pkl')
        
        # 2. โหลด JSON: อยู่ในโฟลเดอร์เดียวกับ app.py ( Danger\app )
        animal_json = os.path.join(self.base_dir, 'animal_groups_translation.json')
        symptom_json = os.path.join(self.base_dir, 'symptom_dictionary.json')

        # โหลดข้อมูลเข้าสู่ระบบ
        try:
            self.model = joblib.load(model_path)
            self.features = joblib.load(feature_path)
            
            with open(animal_json, 'r', encoding='utf-8') as f:
                self.animal_data = json.load(f)
            with open(symptom_json, 'r', encoding='utf-8') as f:
                self.symptom_dict = json.load(f)
            
            print("✅ โหลดโมเดลและข้อมูลสำเร็จ!")
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการโหลดไฟล์: {e}")
            # แจ้งเตือนผ่านหน้าต่างโปรแกรม
            self.show_error(f"ไม่พบไฟล์สำคัญในระบบ\n{e}")
            return

        self.setup_ui()

    def show_error(self, message):
        err_label = ctk.CTkLabel(self, text=message, text_color="red", font=("Sarabun", 16))
        err_label.pack(pady=50)

    def setup_ui(self):
        # Header
        self.label_title = ctk.CTkLabel(self, text="🩺 วิเคราะห์ความเสี่ยงสุขภาพสัตว์", font=("Sarabun", 26, "bold"))
        self.label_title.pack(pady=20)

        # 1. ส่วนเลือกกลุ่มสัตว์
        self.label_group = ctk.CTkLabel(self, text="1. เลือกกลุ่มสัตว์:", font=("Sarabun", 16))
        self.label_group.pack(pady=5)
        
        self.group_options = [val['th'] for val in self.animal_data.values()]
        self.group_mapping = {val['th']: key for key, val in self.animal_data.items()}
        
        self.combo_group = ctk.CTkComboBox(self, values=self.group_options, width=400, font=("Sarabun", 14))
        self.combo_group.pack(pady=10)

        # 2. ส่วนเลือกอาการ (Scrollable)
        self.label_sym = ctk.CTkLabel(self, text="2. เลือกอาการที่พบ (ติ๊กได้หลายข้อ):", font=("Sarabun", 16))
        self.label_sym.pack(pady=5)

        self.scroll_frame = ctk.CTkScrollableFrame(self, width=480, height=380)
        self.scroll_frame.pack(pady=10, padx=20)

        self.symptom_vars = {}
        for eng, th in self.symptom_dict.items():
            var = ctk.BooleanVar()
            cb = ctk.CTkCheckBox(self.scroll_frame, text=f"{th} ({eng})", variable=var, font=("Sarabun", 13))
            cb.pack(pady=5, anchor="w", padx=15)
            self.symptom_vars[eng] = var

        # ปุ่มวิเคราะห์
        self.btn_predict = ctk.CTkButton(self, text="ประมวลผลความเสี่ยง", command=self.predict_risk, 
                                         fg_color="#1a73e8", hover_color="#1557b0", font=("Sarabun", 18, "bold"), height=50)
        self.btn_predict.pack(pady=25)

        # ส่วนแสดงผลลัพธ์
        self.result_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.result_frame.pack(pady=10)

        self.result_label = ctk.CTkLabel(self.result_frame, text="รอการระบุข้อมูล...", font=("Sarabun", 20))
        self.result_label.pack()
        
        self.score_label = ctk.CTkLabel(self.result_frame, text="", font=("Sarabun", 48, "bold"))
        self.score_label.pack()

    def predict_risk(self):
        # 1. ดึงค่าจากหน้าจอ
        selected_th = self.combo_group.get()
        selected_group = self.group_mapping.get(selected_th)
        selected_symptoms = [sym for sym, var in self.symptom_vars.items() if var.get()]

        if not selected_group:
            self.result_label.configure(text="กรุณาเลือกกลุ่มสัตว์!", text_color="#e74c3c")
            return

        # 2. เตรียมข้อมูลเข้าโมเดล
        input_df = pd.DataFrame(0, index=[0], columns=self.features)
        
        # ตั้งค่า Group
        if f'Group_{selected_group}' in self.features:
            input_df[f'Group_{selected_group}'] = 1
            
        # ตั้งค่า Symptoms
        for sym in selected_symptoms:
            full_sym = f'sym_{sym}'
            if full_sym in self.features:
                input_df[full_sym] = 1

        # 3. ทำนายผล
        try:
            prob = self.model.predict_proba(input_df)[0][1]
            score = round(prob * 100, 2)

            # กำหนดสีและข้อความตามระดับความเสี่ยง
            if score >= 80:
                color = "#ff4d4d" # แดง
                status = "⚠️ วิกฤต (Critical Risk)"
            elif score >= 50:
                color = "#ffa502" # ส้ม
                status = "🟠 อันตราย (Dangerous)"
            else:
                color = "#2ed573" # เขียว
                status = "✅ ปกติ (Normal/Low Risk)"

            self.result_label.configure(text=status, text_color=color)
            self.score_label.configure(text=f"{score}%", text_color=color)
        except Exception as e:
            self.result_label.configure(text=f"Error: {e}", text_color="white")

if __name__ == "__main__":
    app = AnimalRiskApp()
    app.mainloop()