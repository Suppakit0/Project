import cv2
import mediapipe as mp
import serial
import time
import joblib
import numpy as np
import warnings
import pandas as pd
import requests # 1. นำเข้าไลบรารีสำหรับยิงเว็บ API

warnings.filterwarnings("ignore", category=UserWarning)

model = joblib.load('gesture_model.pkl')
print("โหลดโมเดล AI สำเร็จ!")

arduino = serial.Serial('COM4', 115200, timeout=1)


time.sleep(2)

# กำหนด URL ของไฟล์ PHP ที่เราสร้างไว้ใน XAMPP
WEB_API_URL = "http://localhost/my_iot_web/update_status.php"

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
print("System Ready. AI Gesture + Web Dashboard Running!")

required_frames = 5
consecutive_frames = 0
current_gesture = None
last_sent_state = None

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    current_prediction = None

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            row = []
            for lm in hand_landmarks.landmark:
                row.extend([lm.x, lm.y, lm.z])
            
            X_input = np.array([row])
            
            if hasattr(model, 'feature_names_in_'):
                X_input_df = pd.DataFrame(X_input, columns=model.feature_names_in_)
                current_prediction = model.predict(X_input_df)[0]
            else:
                current_prediction = model.predict(X_input)[0]

            if current_prediction == 'ON':
                cv2.putText(frame, "Detecting: ON", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            elif current_prediction == 'OFF':
                cv2.putText(frame, "Detecting: OFF", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255, 2))

    if current_prediction == current_gesture:
        consecutive_frames += 1
    else:
        current_gesture = current_prediction
        consecutive_frames = 1

    if consecutive_frames >= required_frames:
        if current_gesture is not None and current_gesture != last_sent_state:
            if current_gesture == 'ON':
                arduino.write(b'0') # สั่งเปิด ESP32
                last_sent_state = 'ON'
                print("Sent to ESP32: 0 (ON)")
                
                # ส่งข้อมูลสถานะ ON ไปยังเว็บแอปผ่าน POST Request
                try:
                    requests.post(WEB_API_URL, data={'plug_status': 'ON'}, timeout=1)
                except:
                    print("Warning: ไม่สามารถเชื่อมต่อเว็บเซิร์ฟเวอร์ได้")

            elif current_gesture == 'OFF':
                arduino.write(b'1') # สั่งปิด ESP32
                last_sent_state = 'OFF'
                print("Sent to ESP32: 1 (OFF)")
                
                # ส่งข้อมูลสถานะ OFF ไปยังเว็บแอปผ่าน POST Request
                try:
                    requests.post(WEB_API_URL, data={'plug_status': 'OFF'}, timeout=1)
                except:
                    print("Warning: ไม่สามารถเชื่อมต่อเว็บเซิร์ฟเวอร์ได้")

    cv2.putText(frame, f"Plug Status: {last_sent_state}", (390, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
    cv2.imshow('AI Gesture Control Smart Plug', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
arduino.close()