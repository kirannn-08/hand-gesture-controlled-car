import cv2
import mediapipe as mp

# MediaPipe hands setup
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Finger tip IDs
tip_ids = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky

# Function to detect hand gestures
def detect_gesture(lm_list):
    if not lm_list:
        return "No hand"

    fingers = []

    # Thumb (x-axis comparison)
    if lm_list[tip_ids[0]][0] > lm_list[tip_ids[0]-1][0]:
        fingers.append(1)
    else:
        fingers.append(0)

    # Other fingers (y-axis comparison)
    for id in range(1, 5):
        if lm_list[tip_ids[id]][1] < lm_list[tip_ids[id]-2][1]:
            fingers.append(1)
        else:
            fingers.append(0)

    total_fingers = fingers.count(1)

    # Map finger count to gesture
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
        return "UNKNOWN"

# Start webcam capture
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Flip image for natural interaction
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

        # Draw landmarks on hand
        mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    gesture = detect_gesture(lm_list)
    cv2.putText(frame, gesture, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

    print(gesture)  # Print recognized gesture to console

    cv2.imshow("Hand Gesture Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# cd ~/mediapipe_project
# source venv/bin/activate
# pip install opencv-python mediapipe


# python --version

# pip list | grep mediapipe
#python gesture_control.py