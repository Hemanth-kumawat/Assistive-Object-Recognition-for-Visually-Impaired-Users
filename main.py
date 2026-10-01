import speech
import ollama


MODEL = "llama3.2:latest"


def ask_ultron(user_text):

    print()
    print("🧠 ULTRON: Thinking...")

    try:

        response = ollama.chat(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are ULTRON, a helpful voice assistant. "
                        "Give concise, natural spoken answers. "
                        "Do not use markdown, emojis, or long explanations "
                        "unless specifically requested."
                    )
                },
                {
                    "role": "user",
                    "content": user_text
                }
            ]
        )

        answer = response["message"]["content"].strip()

        print(f"🤖 ULTRON: {answer}")

        return answer

    except Exception as error:

        print(f"❌ Ollama error: {error}")

        return (
            "I'm having trouble connecting to my AI brain right now."
        )


def main():

    print()
    print("==============================================")
    print("          ULTRON VOICE ASSISTANT")
    print("==============================================")
    print("🧠 AI Brain: Ollama")
    print("🔊 Voice: Daniel")
    print("🎤 Continuous listening: ON")
    print("==============================================")
    print()

    audio = None

    try:

        audio = speech.create_audio_core()

        audio.speak(
            "Hello. I am Ultron. "
            "My AI brain is online. "
            "How can I help you?"
        )

        audio.start_listening(ask_ultron)

    except KeyboardInterrupt:

        print()
        print("🛑 ULTRON interrupted.")

    except Exception as error:

        print()
        print(f"❌ ULTRON ERROR: {error}")

    finally:

        if audio:

            try:
                audio.stop()
            except Exception:
                pass

        print()
        print("==============================================")
        print("             ULTRON OFFLINE")
        print("==============================================")


if __name__ == "__main__":
    main()