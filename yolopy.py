import cv2
import numpy as np
from PIL import Image


class Detector:

    def __init__(self, model_path="yolo11n.pt"):

        self.model = None
        self.model_path = model_path

        print("👁️ Initializing YOLO...")

        try:

            from ultralytics import YOLO

            self.model = YOLO(model_path)

            print(
                f"✅ YOLO model loaded: {model_path}"
            )

        except Exception as error:

            print(
                "❌ YOLO initialization failed:",
                error
            )

    # ---------------------------------------------------------
    # IMAGE CONVERSION
    # ---------------------------------------------------------

    def _convert_image(self, image):

        if image is None:
            return None

        try:

            if isinstance(image, np.ndarray):
                return image

            if isinstance(image, Image.Image):

                return cv2.cvtColor(
                    np.array(image),
                    cv2.COLOR_RGB2BGR
                )

            if hasattr(image, "getvalue"):

                data = image.getvalue()

                array = np.frombuffer(
                    data,
                    dtype=np.uint8
                )

                return cv2.imdecode(
                    array,
                    cv2.IMREAD_COLOR
                )

            if isinstance(image, bytes):

                array = np.frombuffer(
                    image,
                    dtype=np.uint8
                )

                return cv2.imdecode(
                    array,
                    cv2.IMREAD_COLOR
                )

        except Exception as error:

            print(
                "❌ Image conversion error:",
                error
            )

        return None

    # ---------------------------------------------------------
    # DETECTION
    # ---------------------------------------------------------

    def detect(
        self,
        image,
        confidence=0.35
    ):

        if self.model is None:

            print("❌ YOLO model is not loaded")

            return []

        frame = self._convert_image(image)

        if frame is None:

            return []

        try:

            results = self.model.predict(
                source=frame,
                conf=confidence,
                verbose=False
            )

            detections = []

            for result in results:

                boxes = result.boxes

                if boxes is None:
                    continue

                names = result.names

                for box in boxes:

                    class_id = int(
                        box.cls[0].item()
                    )

                    confidence_value = float(
                        box.conf[0].item()
                    )

                    xyxy = box.xyxy[0].tolist()

                    name = names.get(
                        class_id,
                        str(class_id)
                    )

                    detections.append(
                        {
                            "class": name,
                            "name": name,
                            "confidence":
                                confidence_value,
                            "box": xyxy
                        }
                    )

            print(
                f"👁️ Detected {len(detections)} objects"
            )

            return detections

        except Exception as error:

            print(
                "❌ YOLO detection error:",
                error
            )

            return []

    # ---------------------------------------------------------
    # DESCRIPTION
    # ---------------------------------------------------------

    def describe(self, image):

        objects = self.detect(image)

        if not objects:

            return (
                "I could not identify any "
                "recognizable objects."
            )

        counts = {}

        for obj in objects:

            name = obj.get("class", "object")

            counts[name] = (
                counts.get(name, 0) + 1
            )

        descriptions = []

        for name, count in counts.items():

            if count == 1:

                descriptions.append(name)

            else:

                descriptions.append(
                    f"{count} {name}s"
                )

        return (
            "I can see "
            + ", ".join(descriptions)
            + "."
        )