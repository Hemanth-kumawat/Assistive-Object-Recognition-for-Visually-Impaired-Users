import cv2
import numpy as np




# ============================================================
# BRIGHTNESS
# ============================================================

def get_brightness():
    """
    Capture an image from the webcam and determine
    the current brightness level.
    """

    print("📷 Checking brightness...")

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():

        print("❌ Could not open camera.")

        return "unknown"

    try:

        ret, frame = camera.read()

    finally:

        camera.release()

    if not ret:

        print("❌ Could not capture camera frame.")

        return "unknown"

    try:

        # Convert to grayscale and compute mean pixel value (0-255)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mean_brightness = float(np.mean(gray))

        if mean_brightness < 50:
            brightness = "dark"
        elif mean_brightness < 100:
            brightness = "dim"
        elif mean_brightness < 180:
            brightness = "normal"
        else:
            brightness = "bright"

        print(
            f"💡 Brightness: {brightness} (mean={mean_brightness:.1f})"
        )

        return brightness

    except Exception as error:

        print(
            f"❌ Brightness analysis error: {error}"
        )

        return "unknown"


# ============================================================
# YOLO RESULT PROCESSING
# ============================================================

def process_results(results, engine):
    """
    Process YOLO detection results.

    The actual description-generation logic will be
    connected when we rebuild the remaining detection
    modules.
    """

    print("🧠 Processing YOLO results...")

    try:

        detected_objects = []

        for result in results:

            if result.boxes is None:
                continue

            for box in result.boxes:

                try:

                    class_id = int(
                        box.cls[0]
                    )

                    confidence = float(
                        box.conf[0]
                    )

                    names = result.names

                    object_name = names.get(
                        class_id,
                        str(class_id)
                    )

                    detected_objects.append(
                        (
                            object_name,
                            confidence
                        )
                    )

                except Exception:

                    continue

        if not detected_objects:

            message = "I couldn't detect any objects."

            print(
                f"🤖 ULTRON: {message}"
            )

            try:
                engine.speak(message)
            except Exception:
                pass

            return

        # Remove duplicate object names
        unique_objects = []

        for object_name, confidence in detected_objects:

            if object_name not in unique_objects:

                unique_objects.append(
                    object_name
                )

        description = (
            "I can see "
            + ", ".join(unique_objects)
            + "."
        )

        print(
            f"🤖 ULTRON: {description}"
        )

        try:

            engine.speak(
                description
            )

        except Exception as error:

            print(
                f"❌ Speech error: {error}"
            )

    except Exception as error:

        print(
            f"❌ YOLO processing error: {error}"
        )

        try:

            engine.speak(
                "I had trouble analyzing the scene."
            )

        except Exception:
            pass


# ============================================================
# OCR
# ============================================================

def extract_text(frame, engine):
    """
    Placeholder for OCR processing.

    The actual OCR system will be connected through
    read.py when we rebuild that module.
    """

    print("🔎 OCR processing requested.")

    try:

        import read

        if hasattr(
            read,
            "process_frame"
        ):

            return read.process_frame(
                frame,
                engine
            )

        elif hasattr(
            read,
            "read_text_from_camera"
        ):

            return read.read_text_from_camera()

        else:

            print(
                "⚠️ OCR function not found in read.py."
            )

            engine.speak(
                "The text reading system is not ready yet."
            )

    except Exception as error:

        print(
            f"❌ OCR error: {error}"
        )

        try:

            engine.speak(
                "I could not read the text."
            )

        except Exception:
            pass


# ============================================================
# NAVIGATION
# ============================================================

def handle_navigation(engine):
    """
    Start the navigation system.

    Navigation will be connected after Navigation.py
    is rebuilt.
    """

    print("🧭 Navigation requested.")

    try:

        import Navigation as navigation_handler

        navigation_handler.start_navigation(
            current_location="unknown",
            destination="destination"
        )

        try:

            engine.speak(
                "Navigation system started."
            )

        except Exception:
            pass

    except ImportError:

        print(
            "⚠️ Navigation.py is not available."
        )

        try:

            engine.speak(
                "The navigation system is not connected yet."
            )

        except Exception:
            pass

    except Exception as error:

        print(
            f"❌ Navigation error: {error}"
        )

        try:

            engine.speak(
                "I could not start navigation."
            )

        except Exception:
            pass


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("======================================")
    print("        ULTRON FUNCTIONS MODULE")
    print("======================================")
    print()
    print("Functions module loaded successfully.")