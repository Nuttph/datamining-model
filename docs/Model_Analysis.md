# รายงานสรุปผลการพัฒนาและวิเคราะห์โมเดล (Model Analysis Report)

เอกสารฉบับนี้รวบรวมรายละเอียดของโมเดลที่ใช้ในการทำนายความอันตราย (Dangerous) ของอาการในสัตว์ โดยวิเคราะห์ผ่านโครงสร้างโมเดล ประสิทธิภาพ และกราฟการเรียนรู้ต่างๆ

---

## 1. โมเดลต้นไม้ตัดสินใจ (Decision Tree)
Decision Tree เป็นโมเดลที่เลียนแบบกระบวนการตัดสินใจของมนุษย์ ทำให้เราสามารถตีความ (Interpret) ได้ง่ายว่าปัจจัยใดมีผลต่อความอันตรายของอาการมากที่สุด

### โครงสร้างของต้นไม้ (Model Structure)
เราได้ออกแบบให้โมเดลมีความลึกที่เหมาะสมเพื่อป้องกันการเกิด Overfitting และให้ผลลัพธ์ที่แม่นยำ

![Decision Tree Structure](decision_tree_structure.png)

### ประสิทธิภาพ (Confusion Matrix)
แผนภาพความร้อน (Heatmap) แสดงจำนวนการทำนายที่ถูกต้องและผิดพลาดของโมเดล Decision Tree

![Heatmap Decision Tree](heatmap_dt.png)

---

## 2. โมเดล LightGBM
LightGBM เป็นโมเดลประเภท Gradient Boosting ที่มีประสิทธิภาพสูง รองรับข้อมูลขนาดใหญ่ได้ดี และมีความแม่นยำสูงกว่าโมเดลพื้นฐาน

### ประสิทธิภาพ (Confusion Matrix)
ผลการทำนายบนข้อมูลทดสอบ (Test Set) ของ LightGBM

![Heatmap LightGBM](heatmap_lgb.png)

---

## 3. โมเดลโครงข่ายประสาทเทียม (Sequential Deep Learning)
โมเดลนี้ใช้สถาปัตยกรรม Deep Neural Network เพื่อตรวจจับความสัมพันธ์ที่ซับซ้อนระหว่างชื่อสัตว์และกลุ่มอาการ

### โครงสร้างโมเดล (Model Architecture)
โมเดลประกอบด้วย Dense Layers หลายชั้น พร้อมการทำ Dropout เพื่อความทนทานต่อข้อมูลที่หลากหลาย

```text
Layer (type)                Output Shape              Param #   
=================================================================
dense (Dense)               (None, 64)                2304      
dropout (Dropout)           (None, 64)                0         
dense_1 (Dense)             (None, 32)                2080      
dense_2 (Dense)             (None, 1)                 33        
=================================================================
```

### กราฟการเรียนรู้ (Learning Curves)
แสดงความก้าวหน้าของการเทรนโมเดลผ่านค่า Accuracy และ Loss

| Accuracy Curve | Loss Curve |
| :---: | :---: |
| ![Sequential Accuracy](learning_curve_sequential_acc.png) | ![Sequential Loss](learning_curve_sequential_loss.png) |

### ประสิทธิภาพ (Confusion Matrix)
ผลการทำนายในรูปแบบแผนภาพความร้อนสำหรับโมเดล Sequential

![Heatmap Sequential](heatmap_seq.png)

---

## 4. สรุปผล
จากการเปรียบเทียบทั้ง 3 โมเดล พบว่าแต่ละโมเดลมีจุดเด่นที่ต่างกัน:
- **Decision Tree**: เข้าใจง่าย เห็นเส้นทางการตัดสินใจชัดเจน
- **LightGBM**: ให้ความแม่นยำสูงสุดในข้อมูลประเภทรหัส (Categorical/Tabular data)
- **Sequential**: สามารถเรียนรู้ความสัมพันธ์ที่ซับซ้อนในเชิงลึกได้ดี

---
*จัดทำโดย: Antigravity AI Assistant*
