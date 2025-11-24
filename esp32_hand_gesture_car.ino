#include <WiFi.h>

// =====================
// CONFIGURATION ZONE
// =====================
const char* ssid = "sleepyhorse";
const char* password = "12345678";

WiFiServer server(4210);  // TCP server on port 4210

// --- L298N Motor Pins ---
const int IN1 = 26;   // Left motor direction 1
const int IN2 = 25;   // Left motor direction 2
const int ENA = 27;   // Left motor enable (PWM)

const int IN3 = 33;   // Right motor direction 1
const int IN4 = 32;   // Right motor direction 2
const int ENB = 14;   // Right motor enable (PWM)

// --- PWM Settings ---
const int freq = 1000;
const int resolution = 8; // 8-bit (0-255)
const int baseSpeed = 70; // Default base speed

// --- Steering Balance ---
// Adjust these to fine-tune left/right turning behavior
float leftMotorFactor = 1.0;   // 1.0 = full speed, <1 reduces left power
float rightMotorFactor = 0.9;  // Reduce right power slightly (for oversteering fix)

void setup() {
  Serial.begin(115200);

  // Motor pins setup
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  // Attach PWM channels automatically
  ledcAttach(ENA, freq, resolution);
  ledcAttach(ENB, freq, resolution);

  stopMotors();

  // Wi-Fi connection
  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\n✅ WiFi Connected!");
  Serial.print("📶 ESP32 IP Address: ");
  Serial.println(WiFi.localIP());

  server.begin();
  Serial.println("🚗 Server started, waiting for client...");
}

void loop() {
  WiFiClient client = server.available();
  if (client) {
    Serial.println("🟢 Client connected!");
    while (client.connected()) {
      if (client.available()) {
        String command = client.readStringUntil('\n');
        command.trim();
        Serial.println("📥 Received: " + command);

        if (command == "FORWARD") moveForward(baseSpeed);
        else if (command == "REVERSE") moveBackward(baseSpeed);
        else if (command == "LEFT") turnLeft(baseSpeed);
        else if (command == "RIGHT") turnRight(baseSpeed);
        else if (command == "BRAKE" || command == "STOP") stopMotors();
      }
    }
    client.stop();
    stopMotors();
    Serial.println("🔴 Client disconnected.");
  }
}

// ======================
// 🧩 MOTOR CONTROL LOGIC
// ======================

void moveForward(int speedVal) {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  ledcWrite(ENA, speedVal * leftMotorFactor);
  ledcWrite(ENB, speedVal * rightMotorFactor);
}

void moveBackward(int speedVal) {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  ledcWrite(ENA, speedVal * leftMotorFactor);
  ledcWrite(ENB, speedVal * rightMotorFactor);
}

void turnLeft(int speedVal) {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  ledcWrite(ENA, speedVal * 0.4 * leftMotorFactor); // Left slower
  ledcWrite(ENB, speedVal * 1.0 * rightMotorFactor); // Right full
}

void turnRight(int speedVal) {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  ledcWrite(ENA, speedVal * 1.0 * leftMotorFactor);  // Left full
  ledcWrite(ENB, speedVal * 0.4 * rightMotorFactor); // Right slower
}

void stopMotors() {
  ledcWrite(ENA, 0);
  ledcWrite(ENB, 0);
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}




### this is the audrino code for the esp 32 module in developers mode ###
