
# **Accessible Computer Control for Disabled Users**

This project is designed to empower individuals with disabilities by providing an intuitive and accessible way to interact with computers using hand gestures and voice commands. It leverages cutting-edge technologies like **hand tracking (MediaPipe)**, **speech recognition**, and **AI-driven conversational models** to enable users to perform everyday tasks such as zooming, panning, opening applications, searching the web, and more.

## **Key Features**
- **Hand Gesture Recognition**: 
  - Zoom in/out using pinch gestures (thumb and index finger).
  - Pan-lock mode activated by touching thumb and pinky for smooth navigation.
- **Voice Command Interface**: 
  - Execute system commands (e.g., open browser, play music, search Google).
  - Perform translations and engage in AI-powered conversations for assistance.
- **Customizable Actions**: 
  - Easily extendable to support additional gestures or voice commands tailored to individual needs.
- **User-Friendly Design**: 
  - Seamlessly integrates with Windows systems to provide a natural and empowering user experience.
- **Speech Logging**: 
  - Logs all recognized speech commands into a `.txt` file for future reference or analysis.

## **How It Works**
1. **Gesture Mode**:
   - Use hand gestures detected via your webcam to control zooming, panning, and other actions on the computer.
2. **Voice Mode**:
   - Activate voice mode by pressing a key (`V`) and issue spoken commands to perform tasks like opening apps, searching the web, or asking questions to an AI assistant.
3. **Switch Between Modes**:
   - Effortlessly toggle between gesture and voice modes to suit the user's preference or task requirements.

## **Technologies Used**
- **OpenCV & MediaPipe**: For real-time hand tracking and gesture recognition.
- **SpeechRecognition & pyttsx3**: For speech-to-text and text-to-speech functionalities.
- **GoogleTranslator**: For language translation support.
- **Ollama**: For AI-driven conversational capabilities.
- **PyAutoGUI & PyWhatKit**: For automating system actions and web-based tasks.

## **Who Is This For?**
This tool is specifically designed for individuals with physical disabilities who may face challenges using traditional input devices like a mouse or keyboard. By combining voice and gesture-based interactions, this project aims to make computer usage more inclusive and accessible.

## **Installation**
1. Clone this repository:
   ```bash
   git clone https://github.com/wasif-exe/AdaptiControl.git
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python final.py
   ```

## **Future Enhancements**
- Add support for additional languages and dialects.
- Introduce eye-tracking for users with limited hand mobility.
- Expand compatibility to other operating systems (Linux, macOS).
- Incorporate feedback from users with disabilities to refine the interface further.

## **Contributing**
We welcome contributions from developers, accessibility advocates, and anyone passionate about making technology more inclusive. Feel free to open issues, suggest features, or submit pull requests.

## **Acknowledgments**
This project was inspired by the need to bridge the accessibility gap in human-computer interaction. Special thanks to the open-source community for providing tools like MediaPipe, SpeechRecognition, and Ollama that made this project possible.

---
