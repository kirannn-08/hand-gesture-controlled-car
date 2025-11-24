import cv2
import mediapipe as mp
import socket
import time

# Replace with your ESP32 IP and port
ESP_IP = "10.101.171.79"  # Replace with IP printed in Serial Monitor
ESP_PORT = 4210

# Connect to ESP32 via TCP
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Connecting to ESP32...")
while True:
    try:
        client.connect((ESP_IP, ESP_PORT))
        print("Connected to ESP32!")
        break
    except Exception as e:
        print("Connection failed, retrying...")
        time.sleep(2)

# MediaPipe setup
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
tip_ids = [4, 8, 12, 16, 20]

def detect_gesture(lm_list):
    if not lm_list:
        return "BRAKE"
    
    fingers = []
    # Thumb
    if lm_list[tip_ids[0]][0] > lm_list[tip_ids[0]-1][0]:
        fingers.append(1)
    else:
        fingers.append(0)
    # Other fingers
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

    # Send gesture to ESP32 over Wi-Fi
    try:
        client.send((gesture + "\n").encode())
    except Exception as e:
        print("Lost connection to ESP32!")
        break

    cv2.imshow("Hand Gesture Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
client.close()



## needed to be run in the terminal ##

# cd ~/mediapipe_project     (this is the folder name which im using )
# source venv/bin/activate   (setting up a virtual enviornment to run the code )
# pip install opencv-python mediapipe ( double crossing to check the installed packages )


# python --version  (to check the python version )

# pip list | grep mediapipe     
#python gesture_controlwifi.py   (executing thefile )
