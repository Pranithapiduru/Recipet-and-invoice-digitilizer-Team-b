import cv2
import numpy as np
from PIL import Image
from typing import cast

def preprocess_image(pil_image: Image.Image) -> Image.Image:
    """
    SAFE preprocessing for receipts.
    No aggressive thresholding.
    """
    img = np.array(pil_image.convert("L"))

    # Normalize contrast
    img_normalized = cv2.normalize(img, np.zeros_like(img), 0, 255, cv2.NORM_MINMAX)
    if img_normalized is None:
        img_normalized = img

    # Light denoise
    img_final = cv2.GaussianBlur(cast(np.ndarray, img_normalized), (3, 3), 0)

    return Image.fromarray(img)
