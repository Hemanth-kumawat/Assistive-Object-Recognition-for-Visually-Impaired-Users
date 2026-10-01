import speech_recognition as sr
import pyttsx3
import subprocess
import threading
import queue
import time


class AudioCore:

    def __init__(self):
        self.running = False
        self.speaking = False
        self.speech_queue = queue.Queue()

        # Speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = None

        try:
            self.microphone = sr.Microphone()
            with self.microphone as source:
                print("🎤 Calibrating microphone...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
        except Exception as error:
            print("⚠️ Microphone initialization failed:", error)

        print("🔊 AudioCore initialized")

    # ---------------------------------------------------------
    # TEXT TO SPEECH
    # ---------------------------------------------------------

    def speak(self, text):
        if not text:
            return

        text = str(text).strip()

        if not text:
            return

        print(f"🔊 ULTRON: {text}")

        self.speaking = True

        try:
            # macOS native speech is extremely reliable
            subprocess.run(
                ["say", "-v", "Daniel", text],
                check=False
            )
        except Exception as error:
            print("❌ Speech error:", error)

        self.speaking = False

    def speak_async(self, text):
        if not text:
            return

        thread = threading.Thread(
            target=self.speak,
            args=(text,),
            daemon=True
        )

        thread.start()

    # ---------------------------------------------------------
    # SPEECH RECOGNITION
    # ---------------------------------------------------------

    def listen_once(self):
        if self.microphone is None:
            return None

        try:
            with self.microphone as source:

                print("🎤 Listening...")

                audio = self.recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=10
                )

            print("🧠 Processing speech...")

            command = self.recognizer.recognize_google(
                audio,
                language="en-IN"
            )

            command = command.strip()

            print("🎤 Heard:", command)

            return command

        except sr.WaitTimeoutError:
            return None

        except sr.UnknownValueError:
            print("⚠️ Could not understand speech")
            return None

        except sr.RequestError as error:
            print("❌ Speech recognition service error:", error)
            return None

        except Exception as error:
            print("❌ Microphone error:", error)
            return None

    # ---------------------------------------------------------
    # CONTINUOUS LISTENING
    # ---------------------------------------------------------

    def continuous_listening(self, callback):

        self.running = True

        print("🎤 Continuous voice recognition started")

        while self.running:

            try:

                command = self.listen_once()

                if command:

                    try:
                        callback(command)
                    except Exception as error:
                        print(
                            "❌ Voice callback error:",
                            error
                        )

            except Exception as error:

                print(
                    "❌ Continuous listening error:",
                    error
                )

                time.sleep(1)

        print("🔇 Continuous listening stopped")

    # ---------------------------------------------------------
    # STOP
    # ---------------------------------------------------------

    def stop(self):

        self.running = False

        print("🔇 AudioCore stopped")

    # ---------------------------------------------------------
    # BASIC AI FALLBACK
    # ---------------------------------------------------------

    def ask_ai(self, prompt):

        prompt = prompt.lower().strip()

        if prompt in ["hello", "hi", "hey"]:
            return (
                "Hello Hemanth. "
                "I am ULTRON. "
                "How can I help you?"
            )

        if "who are you" in prompt:
            return (
                "I am ULTRON, "
                "your assistive artificial intelligence."
            )

        if "your name" in prompt:
            return "My name is ULTRON."

        if "how are you" in prompt:
            return (
                "I am online and ready to assist you."
            )

        if "time" in prompt:
            import datetime

            current_time = datetime.datetime.now().strftime(
                "%I:%M %p"
            )

            return f"The current time is {current_time}."

        if "date" in prompt:

            import datetime

            current_date = datetime.datetime.now().strftime(
                "%d %B %Y"
            )

            return f"Today's date is {current_date}."

        if "thank" in prompt:
            return "You're welcome."

        if "help" in prompt:
            return (
                "I can help you with object detection, "
                "text reading, voice commands, "
                "scene understanding and navigation."
            )

        return (
            "I received your command. "
            "I am ready to assist you."
        )


class Speech:
    def __init__(self):
        self.enabled = True
        self._lock = threading.Lock()

    def speak(self, text):
        if not text:
            return

        text = str(text).strip()

        if not text:
            return

        print("🔊 ULTRON:", text)

        def run():
            with self._lock:
                try:
                    subprocess.run(
                        ["say", text],
                        check=False
                    )
                except Exception as error:
                    print("❌ Speech error:", error)

        threading.Thread(
            target=run,
            daemon=True
        ).start()

    def stop(self):
        pass


_speaker = Speech()


def speak(text):
    _speaker.speak(text)


def say(text):
    _speaker.speak(text)


def speak_text(text):
    _speaker.speak(text)