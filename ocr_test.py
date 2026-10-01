import cv2
import pytesseract


image = cv2.imread(
    "sample.jpg"
)

if image is None:

    print(
        "❌ sample.jpg not found"
    )

    exit()


gray = cv2.cvtColor(
    image,
    cv2.COLOR_BGR2GRAY
)

gray = cv2.resize(
    gray,
    None,
    fx=3,
    fy=3
)

text = pytesseract.image_to_string(
    gray,
    config="--psm 6"
)

print()
print(
    "=============================="
)

print(
    "OCR RESULT"
)

print(
    "=============================="
)

print(text)