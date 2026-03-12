# 📊 Data Mapping สำหรับ Animal Risk Prediction Model

## ภาพรวม
เอกสารนี้แสดงให้เห็นว่าข้อมูลอะไรบ้างที่ส่งไปยังโมเดล Machine Learning และวิธีการแมพข้อมูล

## โครงสร้างข้อมูลที่ส่งไปโมเดล

### 1. Animal Features (ฟีเจอร์สัตว์)
โมเดลใช้ One-Hot Encoding สำหรับชนิดสัตว์ทั้ง 31 ชนิด:

```
AnimalName_Dog, AnimalName_Cat, AnimalName_Cattle, AnimalName_Poultry,
AnimalName_Sheep, AnimalName_Pig, AnimalName_Elephant, AnimalName_Donkey,
AnimalName_Goat, AnimalName_Monkey, AnimalName_Deer, AnimalName_Wild_cat,
AnimalName_Hamster, AnimalName_Horse, AnimalName_Rabbit, AnimalName_Fox,
AnimalName_Other_birds, AnimalName_Turtle, AnimalName_Mammal, AnimalName_Snake,
AnimalName_Wapiti, AnimalName_Elk, AnimalName_Mule_deer, AnimalName_Black-tailed_deer,
AnimalName_White-tailed_deer, AnimalName_Sika_deer, AnimalName_Reindeer,
AnimalName_Moos, AnimalName_Wolves, AnimalName_Hyaenas, AnimalName_Synthetic_Animal
```

### 2. Symptom Features (ฟีเจอร์อาการ)
อาการต่างๆ ที่พบในข้อมูลการฝึก (One-Hot Encoding):

```
fever, diarrhea, vomiting, weight loss, dehydration, coughing, tiredness,
pains, lethargy, sneezing, seizures, hyperesthesia, sudden death, ulcers,
poor appetite, tarry stool, enlarged lymph nodes, facial swelling, bloody drool,
foul breath, unable to eat, lossened teeth, difficulty breathing, thrist and urination,
swelling on leg, painfull, nasal discharge, broken bones, short term lethargy,
loss of appetite, weekness in the back legs, rapid heart rate, week pulse,
swollen lymph nodes, difficulty walking, back pain, vaginal discharge,
abdominal pain, stiffness, severe weekness and depression, reduce energy,
lameness, swelling of joints, chronic eye inflamation, neurologic abnormalities,
swelling of face or leg, depression, diarrhea with muscus, tensemus,
watery stool, flatulence, strong cough, runny nose, inflammed eye, limping,
eye and skin change, unable to exercise, joint pain, lesions in the nasal cavity,
lesions on nose, nose bleeds, noisy breathing, hair loss, dandruff,
darkened skin, crusting of the skin, ulcerated skin, greenish-yellow nasal discharge,
lack of pigmentation, pain on face, vomitting, jaundice, pneumonia,
lession on the skin, pain, poor coat apperence, watering, no appp,
blindness, muscle pain, muscle stiffness, upset stomach, anaemia,
distended chest, allergic reaction, willnot run to jump, week legs,
pain on leg, eye ulcer, congestion, pink eye, eye disharge, arthritis,
hydrophobia, jaw is dropped, shyness or aggression, bloody urine,
diffculty breathing, loss of eat, dark or black face, blood in faces,
appetite varies, fell unwell, skin issue, sickness, raised growth or bump,
nasal bleeding, diffulty chewing, gasc, blood in stool, stomach growling,
black stool, shaking head, scartching ear, black on ear, bad smell,
red and inflammation ear, attacks, periodic vommiting, blood stool,
inflamed nostrils, lound breathing, polyuria, polydipsa, exessive urination,
change in gait, inability to jump, convulsion, loss of consciousness,
chewing, twitching, salivating, wheezing, rapid breathing, swallowing,
effort to breath, lession on cat skin, dandruff in cat coat, red patches,
excessive grooming, floopy muscle, speech delay, intellectual disability,
walking problem, eye movements, sensitivity to bright light, disharge from affected eye,
inflammation, clouded cornea, rubbing eye, cramps, tenderness, erythema,
scartch, salivation, decrease appetite, scaly patches of skin, sore, scabs,
fatty stool, nausea, firm, distended stomach, swelling in the bite area,
eyeproblem, liver disease, nuerological, mild sneezing, nasal, ocular discharge,
most often none, dyspnea, blood from mouth, shock, discomfort, dry or dull hair,
grinding teeth, rhinitis, abscessess, torticollis, septicemia, enteritis,
stomach cramps, immediate death, blue colored lip, bloody discharge,
pox lession on skin, skin reashes, horny growth, wart-like growth,
red on affected area, lesions on ear, chills, skin ulcer, exhaustion,
swollen and painfull, watering diarrhea, emaciation, ruffled coat,
loss in weight, emaciation, weakness, swollen purple wattle, swollen comb,
egg production decreases, stunted growth, distinctive bumps, thirst,
closed eyes, inability to absorb nutrients, weakened legs, los of the ability to walk,
mammary glads, fluif filled blisters, abortion at the end of gestation,
fatigue, weak calves, join pains, swelling of internal organs, swollen,
red-colored, hot udder, milk getting out more watery, milk getting out more thick,
distress, trembling, staggering, fluif faeces on blood and muscle,
blooody fluid, red diarrhea, faeces are streake with blood, stand with head droping,
abnormal behaviour, slightly swollen, lession on the skin, milky hard,
papules appear on teats anad udder, dull, hind quarted soil, animal stop feed,
decrease in milk production, severe, blood on faces, appetite, milk reduce,
relunctance to move
```

## วิธีการแมพข้อมูลจาก UI

### Input จากผู้ใช้:
```javascript
{
    "animal_type": "Dog",           // ชนิดสัตว์ที่เลือก
    "symptoms": ["fever", "diarrhea"]  // อาการที่เลือก
}
```

### การแปลงข้อมูล:
1. **Animal Type → Animal Feature**
   - "Dog" → ตั้งค่า `AnimalName_Dog = 1`
   - สัตว์อื่นๆ → ตั้งค่าเป็น 0

2. **Symptoms → Symptom Features**
   - แต่ละอาการที่เลือก → ตั้งค่าเป็น 1
   - อาการที่ไม่ได้เลือก → ตั้งค่าเป็น 0

### ตัวอย่างข้อมูลที่ส่งไปโมเดล:

#### กรณีที่ 1: สุนัข + ไข้ + ท้องเสีย
```json
{
    "AnimalName_Dog": 1,
    "AnimalName_Cat": 0,
    "AnimalName_Cattle": 0,
    // ... สัตว์อื่นๆ = 0
    "fever": 1,
    "diarrhea": 1,
    "vomiting": 0,
    // ... อาการอื่นๆ = 0
}
```

#### กรณีที่ 2: แมว + อาเจียน
```json
{
    "AnimalName_Dog": 0,
    "AnimalName_Cat": 1,
    "AnimalName_Cattle": 0,
    // ... สัตว์อื่นๆ = 0
    "fever": 0,
    "diarrhea": 0,
    "vomiting": 1,
    // ... อาการอื่นๆ = 0
}
```

## โมเดลทำนาย

โมเดล Random Forest จะ:
1. รับ input vector ขนาด 31 (สัตว์) + N (อาการ) มิติ
2. คำนวณความน่าจะเป็นของคลาส "Dangerous"
3. คืนค่าเป็นเปอร์เซ็นต์ (0-100%)

## Debug Information

เมื่อส่งข้อมูลไป API `/predict` จะเห็น log แบบนี้:
```
Active features: ['AnimalName_Dog', 'fever', 'diarrhea']
Risk Score: 85.67%
```

---
*เอกสารสร้างเมื่อ: March 12, 2026*
*อัปเดตล่าสุด: March 12, 2026*</content>
<parameter name="filePath">e:\KU\KU3-2\ML\Project\Danger\docs\DATA_MAPPING.md