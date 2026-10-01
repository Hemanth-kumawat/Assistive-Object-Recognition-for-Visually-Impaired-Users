import speech_recognition as sr
import ollama
import pyttsx3


MODEL = "llama3.2:latest"


def speak(text):
    engine = pyttsx3.init()

    for voice in engine.getProperty("voices"):
        if "Daniel" in voice.name or "Daniel" in voice.id:
            engine.setProperty("voice", voice.id)
            break

    engine.setProperty("rate", 150)
    engine.setProperty("volume", 1.0)

    print(f"🔊 ULTRON: {text}")

    engine.say(text)
    engine.runAndWait()
    engine.stop()


def ask_ollama(text):

    print("🧠 ULTRON: Thinking...")

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are ULTRON, an assistive AI assistant. "
                    "Give short, natural answers suitable for speech."
                )
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )

    return response["message"]["content"].strip()


def listen():

    recognizer = sr.Recognizer()

    with sr.Microphone() as source:

        print()
        print("🎤 ULTRON: Listening...")

        recognizer.adjust_for_ambient_noise(
            source,
            duration=0.5
        )

        audio = recognizer.listen(
            source,
            timeout=None,
            phrase_time_limit=10
        )

    print("🧠 Converting speech to text...")

    try:
        text = recognizer.recognize_google(audio)

        print(f"👤 YOU: {text}")

        return text

    except sr.UnknownValueError:
        print("⚠️ I couldn't understand you.")
        return None

    except sr.RequestError as error:
        print(f"❌ Speech recognition error: {error}")
        return None


def main():

    print()
    print("==========================================")
    print("       ULTRON VOICE PIPELINE TEST")
    print("==========================================")
    print("🎤 Microphone")
    print("🧠 Ollama")
    print("🔊 Daniel Voice")
    print("==========================================")

    speak(
        "Hello. I am Ultron. "
        "The voice pipeline is ready."
    )

    while True:

        text = listen()

        if not text:
            continue

        if text.lower().strip() in [
            "stop",
            "exit",
            "quit",
            "stop listening"
        ]:
            speak("Voice system shutting down.")
            break

        try:

            response = ask_ollama(text)

            speak(response)

        except Exception as error:

            print(f"❌ Ollama error: {error}")

            speak(
                "I am having trouble connecting "
                "to my AI brain."
            )


if __name__ == "__main__":
    main()