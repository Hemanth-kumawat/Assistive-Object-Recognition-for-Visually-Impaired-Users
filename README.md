# 👁️‍🗨️ AI-Powered Assistive Tool for Visually Impaired

## 📌 About the Project
This AI-powered tool helps visually impaired individuals interact with their environment using real-time object detection, text reading, and navigation assistance. The system is voice-activated and provides audio feedback through a simple Streamlit interface.

**Key Features:**
- Real-time object detection using YOLOv8
- Text recognition with EasyOCR and audio output via pyttsx3
- Voice-activated navigation assistance using OpenRouteService API
- Optional AI Assistant for interactive voice queries

---

## 🔍 Features

### Object Detection
- Detects and recognizes surrounding objects using YOLOv8.
- Provides immediate audio feedback (e.g., "I see a chair").

### Text Recognition & Audio Output
- Captures text from documents, signs, or images using EasyOCR.
- Converts recognized text to speech for real-time accessibility.

### Navigation Support
- Provides audio-based step-by-step directions using OpenRouteService.
- Allows users to specify a destination via voice command.

### Voice Activation & Intents
- Wake word: **"Alexa"**
- Voice commands trigger specific modules:
  - Object Detection → "Detect objects"
  - Text Reading → "Read this"
  - Navigation → "Guide me to [destination]"
  - AI Assistant → "Talk to assistant"

---

## 🧠 Technologies Used

| Module                     | Technology Used          |
|-----------------------------|-------------------------|
| Object Detection            | YOLOv8 (Ultralytics)    |
| Text Recognition            | EasyOCR                 |
| Image Processing            | OpenCV                  |
| Text-to-Speech              | pyttsx3                 |
| Navigation                  | OpenRouteService API    |
| User Interface              | Streamlit               |
|  AI Assistant               | Gemini AI               |

---

## ⚙️ System Requirements

**Software:**
- Python 3.12+
- VS Code (or any IDE)
- Libraries: OpenCV, pyttsx3, EasyOCR, Streamlit, SpeechRecognition
- Browser: Chrome or any modern browser

**Hardware:**
- Processor: Intel i5 or equivalent
- RAM: 4GB
- Storage: 256GB SSD
- Webcam & Microphone
- Stable Internet connection (for navigation)

---

## 🚀 How It Works
1. **Initialization:** System listens for wake word "Alexa".
2. **Voice Command Capture:** Speech converted to text via SpeechRecognition.
3. **Intent Detection:**
   - **Describe:** YOLOv8 detects objects and provides audio feedback.
   - **Read:** EasyOCR extracts text and reads aloud.
   - **Navigate:** ORS API gives real-time directions.
4. **Audio Output:** System delivers immediate voice feedback for all commands.

---

## ⚠️ Note
This repository contains a **demo version**. Some modules (AI models, API keys) are not included to protect proprietary logic.  
For access to the full source code, contact: **varshab2k23@gmail.com**

---

## 🌟 Future Enhancements
- Step-by-step turn-by-turn navigation
- Multilingual support for text-to-speech
- Enhanced object context awareness (spatial info)
- Offline functionality for maps and OCR
- Mobile application version for portability
- Improved source detection using GPS + Wi-Fi

