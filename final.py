# System and OS utilities
import os
import subprocess
import datetime
import time
import math
import threading

# OpenCV and MediaPipe
import cv2
import mediapipe as mp

# Audio / Voice
import pyttsx3
import speech_recognition as sr
import pyautogui

# Web & translation
import pywhatkit
from deep_translator import GoogleTranslator

# Custom
import ollama
from asl_ui import run_asl_ui



# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)
pan_lock_active = False
app_aliases = {
    "google": "chrome",
    "browser": "chrome",
    "file explorer": "explorer",
    "downloads": "explorer Downloads",
    "documents": "explorer Documents",
    "pictures": "explorer Pictures",
    "task manager": "taskmgr",
    "control panel": "control",
    "settings": "start ms-settings:",
    "terminal": "wt",
    "powershell": "powershell",
    "notepad": "notepad",
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt",
    "calculator": "calc",
    "calendar": "start outlookcal:",
    "media player": "wmplayer",
    "spotify": "spotify",
    "photos": "ms-photos:",
    "camera": "microsoft.windows.camera:",
    "vscode": "code",
    "chat": "start chat_script.py"
}




def speak(text):
    print(f"[VOICE] {text}")
    engine.say(text)
    engine.runAndWait()

# System commands for Windows
system_actions = {
    "open browser": "start chrome",
    "shutdown": "shutdown /s /t 1",
    "open folder": "explorer .",
    "play music": "start wmplayer",
    "open notepad": "notepad",
    "open terminal": "start cmd"
}

def recognize_speech(prompt=None):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        if prompt:
            speak(prompt)
        audio_data = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio_data)
            print(f"[INFO] Recognized Speech: {text}")
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open("speech_log.txt", "a") as f:
                f.write(f"{timestamp}: {text}\n")
            command = text.lower()

            # Check if it's a window command and execute
            handled = handle_window_command(command)

            # Log the original speech
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open("speech_log.txt", "a") as f:
                f.write(f"{timestamp}: {text}\n")

            # If it's handled already, no need to do more
            if handled:
                return None

            return command

        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that. Could you please repeat?")
            return recognize_speech(prompt)
        except sr.RequestError:
            speak("There seems to be an issue with the speech recognition service.")
            return None

def detect_and_translate(text, target_lang='en'):
    """Auto-detect and translate text using Deep Translator."""
    try:
        translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
        print(f"[INFO] Translated Text: {translated}")
        return translated.lower()
    except Exception as e:
        print("[ERROR] Translation failed:", e)
        speak("Sorry, I couldn't translate that.")
        return text.lower()


def perform_action(command):
    for action, cmd in system_actions.items():
        if action in command:
            speak(f"Performing {action}")
            os.system(cmd)
            return True
    if "search for" in command or "google" in command:
        query = command.replace("search for", "").replace("google", "").strip()
        speak(f"Searching Google for {query}")
        pywhatkit.search(query)
        return True
    if "play" in command and "youtube" in command:
        query = command.replace("play", "").replace("on youtube", "").strip()
        speak(f"Playing {query} on YouTube")
        pywhatkit.playonyt(query)
        return True
    if "time" in command:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {current_time}")
        return True
    if "date" in command:
        today = datetime.datetime.now().strftime("%A, %B %d, %Y")
        speak(f"Today's date is {today}")
        return True
    return False

def is_finger_touching(lm, id1, id2, w, h, threshold=40):
    """Utility to check if two landmarks are close."""
    x1, y1 = int(lm[id1].x * w), int(lm[id1].y * h)
    x2, y2 = int(lm[id2].x * w), int(lm[id2].y * h)
    distance = math.hypot(x2 - x1, y2 - y1)
    return distance < threshold

def converse_with_ollama(user_input):
    try:
        response = ollama.chat(model='llama2', messages=[
            {'role': 'user', 'content': user_input}
        ])
        reply = response['message']['content']
        speak(reply)
    except Exception as e:
        speak("Sorry, I couldn't get a response from Ollama.")
        print(f"[ERROR] Ollama: {e}")

# Cooldown mechanism for gesture zoom
last_zoom_time = 0
cooldown_seconds = 1.5

def voice_mode():
    speak("Voice mode activated. Please speak your command.")
    while True:
        command = recognize_speech()
        if command:
            translated_command = detect_and_translate(command)
            if perform_action(translated_command):
                continue  # Wait for more commands
            else:
                converse_with_ollama(translated_command)
        speak("Do you want to continue in voice mode? Say 'yes' or 'no'.")
        response = recognize_speech()
        if response and 'no' in response.lower():
            break
    speak("Returning to gesture mode.")

def handle_window_command(command):
    actions = ["open", "close", "minimize", "maximize"]
    for action in actions:
        if command.startswith(action):
            parts = command.split()
            if len(parts) >= 2:
                app_name = " ".join(parts[1:]).strip()

                # Replace with alias if found
                app_cmd = app_aliases.get(app_name, app_name)

                speak(f"{action.capitalize()}ing {app_name}")
                
                if action == "open":
                    os.system(f"start {app_cmd}")
                else:
                    powershell_cmd = ""

                    if action == "close":
                        powershell_cmd = f"Get-Process | Where-Object {{$_.MainWindowTitle -like '*{app_name}*'}} | ForEach-Object {{$_.CloseMainWindow()}}"
                    elif action == "minimize":
                        powershell_cmd = f"$wshell = New-Object -ComObject wscript.shell; $wshell.AppActivate('{app_name}'); Start-Sleep -Milliseconds 300; $sig = '[DllImport(\"user32.dll\")]public static extern bool ShowWindowAsync(IntPtr hWnd, int nCmdShow);'; $type = Add-Type -MemberDefinition $sig -Name ShowWindow -Namespace Win32Functions -PassThru; $hwnd = Get-Process | Where-Object {{$_.MainWindowTitle -like '*{app_name}*'}} | Select-Object -ExpandProperty MainWindowHandle; $type::ShowWindowAsync($hwnd, 2)"
                    elif action == "maximize":
                        powershell_cmd = f"$wshell = New-Object -ComObject wscript.shell; $wshell.AppActivate('{app_name}'); Start-Sleep -Milliseconds 300; $sig = '[DllImport(\"user32.dll\")]public static extern bool ShowWindowAsync(IntPtr hWnd, int nCmdShow);'; $type = Add-Type -MemberDefinition $sig -Name ShowWindow -Namespace Win32Functions -PassThru; $hwnd = Get-Process | Where-Object {{$_.MainWindowTitle -like '*{app_name}*'}} | Select-Object -ExpandProperty MainWindowHandle; $type::ShowWindowAsync($hwnd, 3)"

                    if powershell_cmd:
                        subprocess.run(["powershell", "-Command", powershell_cmd], shell=True)
                        return True
    return False

def main():
    global last_zoom_time, pan_lock_active
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        exit()

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands()
    mp_draw = mp.solutions.drawing_utils

    speak("Welcome! Press 'V' for voice mode or 'G' for gesture mode.")

    while True:
        success, img = cap.read()
        if not success:
            break

        img = cv2.flip(img, 1)
        h, w, _ = img.shape
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('v'):
            threading.Thread(target=voice_mode).start()

        elif key == ord('g'):
            speak("Starting ASL gesture recognition mode.")
            cap.release()
            cv2.destroyAllWindows()
            run_asl_ui()
            cap = cv2.VideoCapture(0)
            cap.set(3, 640)
            cap.set(4, 480)
            speak("Returning to main mode.")
            continue

        if results.multi_hand_landmarks:
            for hand_lms in results.multi_hand_landmarks:
                lm = hand_lms.landmark

                # Landmarks for thumb, index, pinky
                thumb_x, thumb_y = int(lm[4].x * w), int(lm[4].y * h)
                index_x, index_y = int(lm[8].x * w), int(lm[8].y * h)
                pinky_x, pinky_y = int(lm[20].x * w), int(lm[20].y * h)

                # Check for pan lock gesture (thumb + pinky touch)
                pan_lock_active = is_finger_touching(lm, 4, 20, w, h)

                if pan_lock_active:
                    cv2.putText(img, 'Pan Lock ON', (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 100, 255), 2)
                else:
                    # Zoom only if pan lock is not active
                    dist = math.hypot(index_x - thumb_x, index_y - thumb_y)
                    dist_percent = int(((dist - 10) / (130 - 10)) * 100)
                    dist_percent = max(0, min(100, dist_percent))
                    cv2.putText(img, f'Distance: {dist_percent}%', (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                    now = time.time()
                    if now - last_zoom_time > cooldown_seconds:
                        if dist_percent > 70:
                            pyautogui.hotkey('ctrl', 'add')
                            last_zoom_time = now
                        elif dist_percent < 30:
                            pyautogui.hotkey('ctrl', '-')
                            last_zoom_time = now

                # Draw gesture elements
                cv2.circle(img, (thumb_x, thumb_y), 15, (255, 0, 0), cv2.FILLED)
                cv2.circle(img, (index_x, index_y), 15, (0, 255, 0), cv2.FILLED)
                cv2.circle(img, (pinky_x, pinky_y), 15, (0, 0, 255), cv2.FILLED)
                mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS)

        cv2.imshow("Hand Tracking", img)

        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
