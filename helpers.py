import re
from datetime import datetime


# -------------------------------------------------
# TEXT NORMALIZATION
# -------------------------------------------------

def normalize_text(text: str) -> str:
    """
    Normalize OCR text by removing extra spaces and line breaks.
    """
    if not text:
        return ""

    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# -------------------------------------------------
# AMOUNT CLEANER
# -------------------------------------------------

def clean_amount(text: str):
    """
    Extract the first valid numeric amount from text.
    Example: 'Total: RM 23.60' -> 23.60
    """
    if not text:
        return None

    match = re.search(r"(\d+[.,]?\d*)", text)
    if match:
        return float(match.group(1).replace(",", ""))
    return None


# -------------------------------------------------
# DATE CLEANER
# -------------------------------------------------

def clean_date(text: str):
    """
    Try to parse a date from OCR text.
    Supports common receipt formats.
    """
    if not text:
        return None

    formats = [
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y-%m-%d",
        "%d %b %Y",
        "%d %B %Y"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(text.strip(), fmt).date()
        except ValueError:
            continue

    return None


# -------------------------------------------------
# ITEM NORMALIZER (CRITICAL)
# -------------------------------------------------

def normalize_items(items):
    """
    Guarantee items are returned as a list of dictionaries.
    Prevents pandas DataFrame crashes.
    """
    if not items:
        return []

    if isinstance(items, dict):
        return [items]

    if isinstance(items, list):
        return [i for i in items if isinstance(i, dict)]

    return []
