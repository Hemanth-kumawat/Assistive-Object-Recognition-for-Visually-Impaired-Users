from paddleocr import PaddleOCR
from transformers import pipeline
import os


class OCRAnalyzer:

    def __init__(self):

        print("🧠 Initializing OCR system...")

        try:

            self.ocr_engine = PaddleOCR(
                lang="en"
            )

            print("✅ PaddleOCR loaded.")

        except Exception as error:

            print(
                f"❌ PaddleOCR initialization failed: {error}"
            )

            self.ocr_engine = None

        self.summarizer = None

    # ========================================================
    # OCR
    # ========================================================

    def extract_text(self, image_path):

        if not image_path:

            return ""

        if not os.path.exists(image_path):

            print(
                "❌ Image not found:"
                f" {image_path}"
            )

            return ""

        if self.ocr_engine is None:

            return ""

        print(
            "🔎 Extracting text..."
        )

        try:

            result = self.ocr_engine.predict(
                image_path
            )

            text_parts = []

            for page in result:

                try:

                    data = page.json

                    if callable(data):

                        data = data()

                    if not data:

                        continue

                    # PaddleOCR versions can return
                    # different JSON structures.
                    if isinstance(data, dict):

                        for key in [
                            "rec_texts",
                            "texts"
                        ]:

                            values = data.get(
                                key,
                                []
                            )

                            if values:

                                text_parts.extend(
                                    values
                                )

                except Exception:

                    continue

            text = " ".join(
                text_parts
            ).strip()

            if text:

                print()
                print("📖 FETCHED TEXT:")
                print("----------------")
                print(text)
                print("----------------")

            else:

                print(
                    "⚠️ No text detected."
                )

            return text

        except Exception as error:

            print(
                f"❌ OCR error: {error}"
            )

            return ""

    # ========================================================
    # SUMMARIZER
    # ========================================================

    def load_summarizer(self):

        if self.summarizer is not None:

            return self.summarizer

        print(
            "🧠 Loading summarization model..."
        )

        try:

            self.summarizer = pipeline(
                "summarization"
            )

            print(
                "✅ Summarizer loaded."
            )

            return self.summarizer

        except Exception as error:

            print(
                f"❌ Summarizer loading failed: {error}"
            )

            return None

    # ========================================================
    # SUMMARIZE
    # ========================================================

    def summarize(
        self,
        content,
        max_length=100
    ):

        if not content:

            return ""

        if len(content.strip()) < 50:

            print(
                "ℹ️ Text is short — "
                "no summary needed."
            )

            return content

        summarizer = self.load_summarizer()

        if summarizer is None:

            return content

        try:

            # Keep input within a reasonable size
            # for the summarization model.
            content = content[:4000]

            result = summarizer(
                content,
                max_length=max_length,
                min_length=30,
                do_sample=False
            )

            if result:

                summary = result[0].get(
                    "summary_text",
                    ""
                )

                return summary.strip()

        except Exception as error:

            print(
                f"❌ Summarization error: {error}"
            )

        return content


# ============================================================
# GLOBAL ANALYZER
# ============================================================

_analyzer = None


def get_analyzer():

    global _analyzer

    if _analyzer is None:

        _analyzer = OCRAnalyzer()

    return _analyzer


# ============================================================
# MAIN FUNCTION
# ============================================================

def analyze_image(path_to_img):

    analyzer = get_analyzer()

    raw_text = analyzer.extract_text(
        path_to_img
    )

    if not raw_text:

        print(
            "\n⚠️ No readable text found."
        )

        return ""

    print(
        "\nFetched Text:\n",
        raw_text
    )

    if len(raw_text.strip()) > 50:

        short_text = analyzer.summarize(
            raw_text
        )

        print(
            "\nCompressed Summary:\n",
            short_text
        )

        return short_text

    else:

        print(
            "\nBrief content — "
            "no summary generated."
        )

        return raw_text


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("======================================")
    print("        ULTRON OCR ANALYZER")
    print("======================================")
    print()

    image_path = "sample.jpg"

    if not os.path.exists(image_path):

        print(
            f"❌ {image_path} was not found."
        )

    else:

        analyze_image(
            image_path
        )