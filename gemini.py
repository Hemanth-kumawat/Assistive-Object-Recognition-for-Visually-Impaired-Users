import os
from google import genai


class GeminiCore:

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set. "
                "Set your Gemini API key in the terminal first."
            )

        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.0-flash"
        self.chat = self.client.chats.create(model=self.model_name)

    def ask(self, query):

        """
        Send a message to Gemini and return
        a natural conversational response.
        """

        if not query:
            return "I didn't receive a question."

        try:

            response = self.chat.send_message(query)
            answer = getattr(response, "text", None)

            if answer is None:
                answer = str(response)

            return answer.strip()

        except Exception as error:

            print(f"Gemini error: {error}")

            return (
                "I'm having trouble connecting "
                "to my AI system right now."
            )

    def describe(self, query):

        """
        Generate a short description.
        Useful later for camera/vision.
        """

        prompt = f"""
You are ULTRON, an intelligent voice assistant.

Give a short and clear description of:

{query}

Keep the response concise because it will
be spoken aloud.
"""

        return self.ask(prompt)

    def additional_info(self, query):

        """
        Provide additional information.
        """

        prompt = f"""
You are ULTRON, a helpful AI assistant.

Provide useful additional information about:

{query}

Keep the answer conversational and concise.
"""

        return self.ask(prompt)

    def create_sentence(self, ocr_text):

        """
        Convert OCR text into a natural sentence
        without changing its original meaning.
        """

        if not ocr_text:
            return "I couldn't read any text."

        prompt = f"""
You are ULTRON.

The camera/OCR system detected this text:

{ocr_text}

Convert it into a clear, natural sentence
while preserving the original meaning.

Do not invent information.
Keep it short because it will be spoken aloud.
"""

        return self.ask(prompt)


# ---------------------------------------------------------
# GLOBAL GEMINI INSTANCE
# ---------------------------------------------------------

_gemini = None


def get_gemini():

    global _gemini

    if _gemini is None:
        _gemini = GeminiCore()

    return _gemini


# ---------------------------------------------------------
# FUNCTIONS COMPATIBLE WITH THE OLD PROJECT
# ---------------------------------------------------------

def ask_gemini(query):

    return get_gemini().ask(query)


def fetch_description(query):

    return get_gemini().describe(query)


def fetch_additional_info(query):

    return get_gemini().additional_info(query)


def fetch_sentence(ocr_text):

    return get_gemini().create_sentence(ocr_text)


# ---------------------------------------------------------
# TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    print("===================================")
    print("       ULTRON GEMINI CORE")
    print("===================================")

    try:

        gemini = get_gemini()

        print("\nGemini connected successfully.")
        print("Type 'exit' to stop.\n")

        while True:

            question = input("You: ")

            if question.lower().strip() == "exit":
                break

            answer = gemini.ask(question)

            print(f"\nULTRON: {answer}\n")

    except Exception as error:

        print(f"\nERROR: {error}")