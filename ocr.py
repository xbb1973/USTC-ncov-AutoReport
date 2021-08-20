import cv2
import numpy as np
import pytesseract
import requests
from PIL import Image


def ocr(img):
    img = np.array(img)
    img = img[:, :, ::-1].copy()
    img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(img, (45, 100, 40), (90, 255, 255))
    imask = mask > 0
    green = np.zeros_like(img, np.uint8)
    green[imask] = np.array([0, 0, 255])

    green = cv2.cvtColor(green, cv2.COLOR_HSV2RGB)
    img = Image.fromarray(green)

    r = pytesseract.image_to_string(img).strip()
    return r


if __name__ == "__main__":
    raw = requests.get(
        "https://passport.ustc.edu.cn/validatecode.jsp?type=login", stream=True
    ).raw
    img = Image.open(raw)
    img.show()
    r = ocr(img)
    print(r)
