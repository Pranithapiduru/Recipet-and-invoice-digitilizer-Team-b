from pdf2image import convert_from_bytes
from typing import List
from PIL import Image

from config.config import POPPLER_PATH


def pdf_to_images(pdf_bytes: bytes) -> List[Image.Image]:
    """
    Convert PDF bytes into list of PIL Images using Poppler
    """
    images = convert_from_bytes(
        pdf_bytes,
        poppler_path=POPPLER_PATH
    )
    return images
