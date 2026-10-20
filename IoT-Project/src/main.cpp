#include <Arduino.h>

const int relayPin = 23;   // ขา S ของ Relay ต่อเข้ากับ GPIO 23
const int ledPin = 2;      // ขาสำหรับ LED (บนบอร์ด ESP32 ส่วนใหญ่คือ GPIO 2)

void setup() {
  Serial.begin(115200);
  
  pinMode(relayPin, OUTPUT);
  pinMode(ledPin, OUTPUT);
  
  // ค่าเริ่มต้น: ปิดรีเลย์ (LOW) และปิด LED (LOW)
  digitalWrite(relayPin, LOW); 
  digitalWrite(ledPin, LOW);
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    
    if (command == '0') {
      digitalWrite(relayPin, HIGH); // สั่งเปิดรีเลย์ (Active High)
      digitalWrite(ledPin, HIGH);   // สั่งเปิด LED 
      Serial.println("Plug ON & LED ON");
    } 
    else if (command == '1') {
      digitalWrite(relayPin, LOW);  // สั่งปิดรีเลย์
      digitalWrite(ledPin, LOW);    // สั่งปิด LED
      Serial.println("Plug OFF & LED OFF");
    }
  }
}