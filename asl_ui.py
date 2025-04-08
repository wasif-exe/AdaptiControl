def run_asl_ui():
    import cv2
    import mediapipe as mp
    import numpy as np
    from tensorflow.keras.models import load_model
    import string
    from collections import deque

    model = load_model('asl_model.h5')
    labels = list(string.ascii_uppercase) + ['space', 'del', 'nothing']

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1)
    mp_draw = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    prev_letter = ""
    letter_buffer = deque(maxlen=10)
    current_letter = ""
    confidence = 0.0

    while True:
        success, img = cap.read()
        if not success:
            break

        img = cv2.flip(img, 1)
        h, w, _ = img.shape
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                x_min = int(min([lm.x for lm in hand_landmarks.landmark]) * w)
                x_max = int(max([lm.x for lm in hand_landmarks.landmark]) * w)
                y_min = int(min([lm.y for lm in hand_landmarks.landmark]) * h)
                y_max = int(max([lm.y for lm in hand_landmarks.landmark]) * h)

                margin = 20
                x_min = max(0, x_min - margin)
                y_min = max(0, y_min - margin)
                x_max = min(w, x_max + margin)
                y_max = min(h, y_max + margin)

                hand_img = img[y_min:y_max, x_min:x_max]
                if hand_img.size == 0:
                    continue

                try:
                    resized_img = cv2.resize(hand_img, (64, 64))
                    norm_img = resized_img / 255.0
                    input_img = np.expand_dims(norm_img, axis=0)

                    prediction = model.predict(input_img)
                    if prediction.shape[1] != len(labels):
                        continue

                    predicted_class = np.argmax(prediction)
                    predicted_letter = labels[predicted_class]
                    pred_confidence = float(np.max(prediction))

                    letter_buffer.append(predicted_letter)

                    if letter_buffer.count(predicted_letter) > 7 and predicted_letter != prev_letter:
                        if predicted_letter not in ['nothing', 'space', 'del']:
                            current_letter = predicted_letter
                            confidence = pred_confidence
                        prev_letter = predicted_letter
                except Exception as e:
                    print("Prediction error:", e)

        panel = np.zeros((480, 300, 3), dtype=np.uint8)
        cv2.putText(panel, "Current Letter:", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        cv2.putText(panel, current_letter, (90, 100), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 5)

        bar_x, bar_y = 30, 160
        bar_width, bar_height = 200, 30
        filled_width = int(confidence * bar_width)
        cv2.rectangle(panel, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (255, 255, 255), 2)
        cv2.rectangle(panel, (bar_x, bar_y), (bar_x + filled_width, bar_y + bar_height), (0, 255, 0), -1)
        cv2.putText(panel, f"{int(confidence * 100)}%", (bar_x + 70, bar_y + 23), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        full_frame = np.hstack((img, panel))
        cv2.imshow("ASL Recognition with UI", full_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
