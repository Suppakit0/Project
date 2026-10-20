import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

# โหลดชุดข้อมูล
df = pd.read_csv('gesture_dataset.csv')

# แยก Features (พิกัด) และ Labels (ชื่อท่าทาง)
X = df.drop('label', axis=1)
y = df['label']

# แบ่งข้อมูลสำหรับ Train และ Test (80% / 20%)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# สร้างและเทรนโมเดล Random Forest
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# ตรวจสอบความแม่นยำ
accuracy = model.score(X_test, y_test)
print(f"Model Accuracy: {accuracy * 100:.2f}%")

# บันทึกโมเดลเก็บไว้ใช้งาน
joblib.dump(model, 'gesture_model.pkl')
print("Model saved as gesture_model.pkl")