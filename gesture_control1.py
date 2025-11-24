import cv2
import mediapipe as mp
import serial
import time

# Replace with your USB Serial port
ESP_PORT = "/dev/cu.usbserial-5A7B0631771"  # your port
ESP_BAUD = 115200

# Connect to ESP32
esp = serial.Serial(ESP_PORT, ESP_BAUD, timeout=1)
time.sleep(2)  # wait for ESP32 to initialize

# MediaPipe setup
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
tip_ids = [4, 8, 12, 16, 20]

def detect_gesture(lm_list):
    if not lm_list:
        return "BRAKE"
    
    fingers = []
    if lm_list[tip_ids[0]][0] > lm_list[tip_ids[0]-1][0]:
        fingers.append(1)
    else:
        fingers.append(0)
    for id in range(1, 5):
        if lm_list[tip_ids[id]][1] < lm_list[tip_ids[id]-2][1]:
            fingers.append(1)
        else:
            fingers.append(0)
    total_fingers = fingers.count(1)
    
    if total_fingers == 0:
        return "BRAKE"
    elif total_fingers == 5:
        return "FORWARD"
    elif total_fingers == 4:
        return "RIGHT"
    elif total_fingers == 3:
        return "LEFT"
    elif total_fingers == 2:
        return "REVERSE"
    else:
        return "BRAKE"

# Webcam capture
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    lm_list = []
    if result.multi_hand_landmarks:
        hand_landmarks = result.multi_hand_landmarks[0]
        for id, lm in enumerate(hand_landmarks.landmark):
            h, w, c = frame.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            lm_list.append((cx, cy))
        mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    gesture = detect_gesture(lm_list)
    cv2.putText(frame, gesture, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
    print(gesture)

    # Send gesture to ESP32
    esp.write((gesture + "\n").encode())

    cv2.imshow("Hand Gesture Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
esp.close()



## needed to be run in the terminal ##

# cd ~/mediapipe_project     (this is the folder name which im using )
# source venv/bin/activate   (setting up a virtual enviornment to run the code )
# pip install opencv-python mediapipe ( double crossing to check the installed packages )


# python --version  (to check the python version )

# pip list | grep mediapipe     
#python gesture_control1.py   (executing thefile )
