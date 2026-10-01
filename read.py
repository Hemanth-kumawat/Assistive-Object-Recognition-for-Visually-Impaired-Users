import os
import subprocess
import cv2
import numpy as np


def speak(text):

    if not text:
        return

    try:

        subprocess.run(
            ["say", "-v", "Daniel", str(text)],
            check=False
        )

    except Exception as error:

        print("❌ Speech error:", error)


def save_image(
    image,
    filename="captured_image.jpg"
):

    try:

        if image is None:
            return None

        if hasattr(image, "getbuffer"):

            with open(filename, "wb") as file:

                file.write(
                    image.getbuffer()
                )

            return filename

        if isinstance(image, np.ndarray):

            cv2.imwrite(
                filename,
                image
            )

            return filename

    except Exception as error:

        print(
            "❌ Image save error:",
            error
        )

    return None


def read_image(image):

    if image is None:

        return "No image was provided."

    try:

        from PIL import Image

        if hasattr(image, "getvalue"):

            data = image.getvalue()

            array = np.frombuffer(
                data,
                dtype=np.uint8
            )

            frame = cv2.imdecode(
                array,
                cv2.IMREAD_COLOR
            )

        elif isinstance(image, Image.Image):

            frame = cv2.cvtColor(
                np.array(image),
                cv2.COLOR_RGB2BGR
            )

        elif isinstance(image, np.ndarray):

            frame = image

        else:

            return "Unsupported image format."

        if frame is None:

            return "I could not process the image."

        # -----------------------------------------------------
        # OCR
        # -----------------------------------------------------

        try:

            from paddleocr import PaddleOCR

            ocr = PaddleOCR(
                lang="en",
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False
            )

            result = ocr.predict(frame)

            texts = []

            for item in result:

                if isinstance(item, dict):

                    rec_texts = item.get(
                        "rec_texts",
                        []
                    )

                    if rec_texts:

                        texts.extend(
                            rec_texts
                        )

            if texts:

                return " ".join(
                    str(x) for x in texts
                )

        except Exception as error:

            print(
                "⚠️ PaddleOCR unavailable:",
                error
            )

        return (
            "I could see the image, "
            "but I could not find readable text."
        )

    except Exception as error:

        print(
            "❌ OCR error:",
            error
        )

        return "I could not read the text."