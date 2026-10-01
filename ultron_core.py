import threading
import time

from speech import AudioCore
from read import read_image
from yolopy import Detector
import navigation_handler


class UltronCore:

    def __init__(self):

        print()
        print("=" * 55)
        print("              ULTRON ASSISTIVE AI")
        print("=" * 55)

        self.audio = AudioCore()
        self.detector = Detector()

        self.voice_running = False
        self.voice_thread = None

        self.navigation_voice_running = False
        self.navigation_voice_thread = None

        print("✅ ULTRON Core initialized")

    # =========================================================
    # AI
    # =========================================================

    def ask_ai(self, prompt):

        try:

            return self.audio.ask_ai(prompt)

        except Exception as error:

            print(
                "❌ AI error:",
                error
            )

            return (
                "I could not process "
                "that request."
            )

    # =========================================================
    # OCR
    # =========================================================

    def read_text(self, image):

        try:

            return read_image(image)

        except Exception as error:

            print(
                "❌ OCR error:",
                error
            )

            return "I could not read the text."

    # =========================================================
    # OBJECT DETECTION
    # =========================================================

    def detect_objects(self, image):

        try:

            return self.detector.detect(image)

        except Exception as error:

            print(
                "❌ Detection error:",
                error
            )

            return []

    # =========================================================
    # SCENE DESCRIPTION
    # =========================================================

    def describe_scene(self, image):

        try:

            return self.detector.describe(image)

        except Exception as error:

            print(
                "❌ Scene description error:",
                error
            )

            return (
                "I could not describe "
                "the scene."
            )

    # =========================================================
    # DESTINATION EXTRACTION
    # =========================================================

    def extract_destination(self, command):

        command = command.lower().strip()

        prefixes = [

            "navigate to ",

            "take me to ",

            "directions to ",

            "go to ",

            "route to ",

            "guide me to ",

            "show me directions to "

        ]

        for prefix in prefixes:

            if command.startswith(prefix):

                destination = command[
                    len(prefix):
                ].strip()

                return destination

        return None

    # =========================================================
    # NAVIGATION
    # =========================================================

    def handle_navigation(self, destination):

        if not destination:

            return "Please provide a destination."

        print(
            f"🧭 Navigation requested: "
            f"{destination}"
        )

        if not navigation_handler.is_navigation_server_online():

            return (
                "The navigation server is "
                "not running. Please start "
                "the navigation service."
            )

        try:

            success = (
                navigation_handler
                .start_navigation(destination)
            )

            if not success:

                return (
                    "I could not start "
                    "navigation."
                )

            self.start_navigation_voice()

            message = (
                f"Navigation started to "
                f"{destination}."
            )

            self.audio.speak_async(message)

            return message

        except Exception as error:

            print(
                "❌ Navigation error:",
                error
            )

            return (
                "Navigation is "
                "currently unavailable."
            )

    # =========================================================
    # NAVIGATION VOICE
    # =========================================================

    def start_navigation_voice(self):

        if self.navigation_voice_running:

            return

        self.navigation_voice_running = True

        def navigation_loop():

            last_instruction = ""

            print(
                "🔊 Continuous navigation "
                "voice started"
            )

            while self.navigation_voice_running:

                try:

                    data = (
                        navigation_handler
                        .get_next_instruction()
                    )

                    if data:

                        instruction = data.get(
                            "instruction",
                            ""
                        )

                        if (
                            instruction
                            and
                            instruction
                            != last_instruction
                        ):

                            self.audio.speak(
                                instruction
                            )

                            last_instruction = (
                                instruction
                            )

                    summary = (
                        navigation_handler
                        .get_last_summary()
                    )

                    if summary:

                        if not summary.get(
                            "active",
                            True
                        ):

                            break

                    time.sleep(3)

                except Exception as error:

                    print(
                        "⚠️ Navigation voice error:",
                        error
                    )

                    time.sleep(3)

            self.navigation_voice_running = False

            print(
                "🔇 Navigation voice stopped"
            )

        self.navigation_voice_thread = (
            threading.Thread(
                target=navigation_loop,
                daemon=True
            )
        )

        self.navigation_voice_thread.start()

    # =========================================================
    # STOP NAVIGATION
    # =========================================================

    def stop_navigation(self):

        try:

            navigation_handler.stop_navigation()

        except Exception:
            pass

        self.navigation_voice_running = False

        return "Navigation stopped."

    # =========================================================
    # NAVIGATION STATUS
    # =========================================================

    def navigation_status(self):

        try:

            status = (
                navigation_handler
                .get_navigation_status()
            )

            if not status:

                return (
                    "Navigation status "
                    "is unavailable."
                )

            if not status.get(
                "active",
                False
            ):

                return (
                    "Navigation is "
                    "currently inactive."
                )

            destination = status.get(
                "destination",
                "unknown destination"
            )

            distance = status.get(
                "distance_meters"
            )

            instruction = status.get(
                "next_instruction"
            )

            message = (
                f"Navigation is active. "
                f"Destination: "
                f"{destination}. "
            )

            if distance is not None:

                message += (
                    f"Distance remaining: "
                    f"{round(distance)} meters. "
                )

            if instruction:

                message += (
                    f"Next instruction: "
                    f"{instruction}"
                )

            return message

        except Exception:

            return (
                "Navigation status "
                "is unavailable."
            )

    # =========================================================
    # COMMAND PROCESSOR
    # =========================================================

    def process_text_command(self, command):

        if not command:

            return ""

        command = command.strip()

        lower = command.lower()

        print()
        print("🎤 COMMAND:")
        print(command)

        # STOP NAVIGATION

        if any(
            phrase in lower
            for phrase in [
                "stop navigation",
                "cancel navigation",
                "end navigation",
                "stop directions"
            ]
        ):

            return self.stop_navigation()

        # NAVIGATION STATUS

        if any(
            phrase in lower
            for phrase in [
                "navigation status",
                "where am i going",
                "how far is the destination",
                "navigation information"
            ]
        ):

            return self.navigation_status()

        # NAVIGATION

        destination = (
            self.extract_destination(lower)
        )

        if destination:

            return self.handle_navigation(
                destination
            )

        # OCR

        if any(
            phrase in lower
            for phrase in [
                "read text",
                "read this",
                "read the text"
            ]
        ):

            return (
                "Please capture an image "
                "so I can read the text."
            )

        # OBJECT DETECTION

        if any(
            phrase in lower
            for phrase in [
                "detect objects",
                "what do you see",
                "identify objects",
                "identify this"
            ]
        ):

            return (
                "Please capture an image "
                "and I will identify "
                "the objects."
            )

        # SCENE

        if any(
            phrase in lower
            for phrase in [
                "describe scene",
                "describe what you see",
                "describe surroundings"
            ]
        ):

            return (
                "Please capture an image "
                "and I will describe "
                "the scene."
            )

        # NORMAL AI

        return self.ask_ai(command)

    # =========================================================
    # VOICE COMMAND
    # =========================================================

    def process_voice_command(self, command):

        response = (
            self.process_text_command(command)
        )

        if response:

            self.audio.speak_async(response)

        return response

    # =========================================================
    # CONTINUOUS VOICE
    # =========================================================

    def start_continuous_voice(self):

        if self.voice_running:

            return

        self.voice_running = True

        def voice_loop():

            print(
                "🎤 ULTRON continuous voice "
                "started"
            )

            try:

                self.audio.continuous_listening(
                    self.process_voice_command
                )

            except Exception as error:

                print(
                    "❌ Voice error:",
                    error
                )

            finally:

                self.voice_running = False

                print(
                    "🔇 ULTRON voice stopped"
                )

        self.voice_thread = (
            threading.Thread(
                target=voice_loop,
                daemon=True
            )
        )

        self.voice_thread.start()

    # =========================================================
    # STOP VOICE
    # =========================================================

    def stop_continuous_voice(self):

        self.voice_running = False

        self.audio.stop()

    # =========================================================
    # STATUS
    # =========================================================

    def get_status(self):

        navigation_online = (
            navigation_handler
            .is_navigation_server_online()
        )

        return {

            "ultron": "online",

            "voice":
                "active"
                if self.voice_running
                else "inactive",

            "navigation":
                "online"
                if navigation_online
                else "offline",

            "navigation_voice":
                "active"
                if self.navigation_voice_running
                else "inactive"
        }

    # =========================================================
    # SHUTDOWN
    # =========================================================

    def shutdown(self):

        print(
            "🛑 Shutting down ULTRON..."
        )

        self.voice_running = False

        self.navigation_voice_running = False

        try:

            self.audio.stop()

        except Exception:
            pass

        print("✅ ULTRON stopped")