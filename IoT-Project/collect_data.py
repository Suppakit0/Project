import cv2
import mediapipe as mp
import csv
import os

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# เปิดไฟล์ CSV สำหรับเก็บข้อมูลพิกัด
file_path = 'gesture_dataset.csv'
file_exists = os.path.exists(file_path)
f = open(file_path, mode='a', newline='')
writer = csv.writer(f)

if not file_exists:
    # สร้างหัวคอลัมน์: x0, y0, z0, ... x20, y20, z20, label
    header = []
    for i in range(21):
        header += [f'x{i}', f'y{i}', f'z{i}']
    header.append('label')
    writer.writerow(header)

cap = cv2.VideoCapture(0)
print("Press '1' to record Gesture ON, '0' to record Gesture OFF, 'q' to quit.")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    label_to_save = None
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow('Collect Dataset', frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('1') or key == ord('0'):
        if result.multi_hand_landmarks:
            # ดึงค่าพิกัด normalized ของจุดข้อต่อทั้ง 21 จุด
            landmarks = result.multi_hand_landmarks[0].landmark
            row = []
            for lm in landmarks:
                row.extend([lm.x, lm.y, lm.z])
            
            # ระบุป้ายกำกับ (Label)
            label = 'ON' if key == ord('1') else 'OFF'
            row.append(label)
            writer.writerow(row)
            print(f"Saved gesture: {label}")

cap.release()
f.close()
cv2.destroyAllWindows()