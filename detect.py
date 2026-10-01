import cv2
import functions


# ============================================================
# INTENT DETECTION
# ============================================================

def detect_intent_texts(project_id, session_id, texts, language_code):
    """
    Simple local intent detection.

    Kept for compatibility with the older project.
    """

    text = texts[0].lower().strip() if texts else ""

    if "time" in text:
        return "Time", "Time query"

    elif "describe" in text or "what do you see" in text:
        return "Describe", "Scene description"

    elif "brightness" in text or "light" in text:
        return "Brightness", "Light analysis"

    elif "read" in text or "text" in text:
        return "Read", "Text recognition"

    elif "navigate" in text or "directions" in text:
        return "Navigate", "Navigation request"

    else:
        return "GeneralQuery", text


# ============================================================
# CAMERA
# ============================================================

def capture_camera():

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():

        print("❌ Camera could not be opened.")

        return None

    ret, frame = camera.read()

    camera.release()

    if not ret:

        print("❌ Could not capture camera frame.")

        return None

    return frame


# ============================================================
# SCENE DESCRIPTION
# ============================================================

def describe_scene(model, engine):

    """
    Capture an image from the camera,
    run YOLO object detection,
    and send the results to functions.py.
    """

    print("📷 Capturing scene...")

    frame = capture_camera()

    if frame is None:

        try:
            engine.speak(
                "Camera access is unavailable."
            )
        except Exception:
            pass

        return

    print("🧠 Analyzing scene...")

    try:

        results = model(frame)

        functions.process_results(
            results,
            engine
        )

    except Exception as error:

        print(
            f"❌ Scene detection error: {error}"
        )

        try:

            engine.speak(
                "I could not analyze the scene."
            )

        except Exception:
            pass


# ============================================================
# TEXT DETECTION
# ============================================================

def detect_text(engine):

    """
    Capture an image and process text recognition.
    """

    print("📷 Capturing image for OCR...")

    frame = capture_camera()

    if frame is None:

        try:

            engine.speak(
                "Camera access is unavailable."
            )

        except Exception:
            pass

        return

    print("🔎 Processing text...")

    try:

        functions.extract_text(
            frame,
            engine
        )

    except Exception as error:

        print(
            f"❌ Text detection error: {error}"
        )

        try:

            engine.speak(
                "I could not read the text."
            )

        except Exception:
            pass


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("======================================")
    print("       ULTRON DETECTION MODULE")
    print("======================================")
    print()
    print("Detection module loaded successfully.")