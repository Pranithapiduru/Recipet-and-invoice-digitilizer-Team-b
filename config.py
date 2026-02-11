import os

# =========================================================
# APPLICATION CONFIGURATION
# =========================================================
APP_TITLE = "Receipt Vault & Analyzer"

# =========================================================
# BASE DIRECTORY
# =========================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# =========================================================
# DATABASE CONFIGURATION (SQLite)
# =========================================================
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "receipts.db")
os.makedirs(DATA_DIR, exist_ok=True)

# =========================================================
# OCR CONFIGURATION
# =========================================================
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"C:\Users\p.pranitha\Downloads\Release-25.12.0-0\poppler-25.12.0\Library\bin"

# =========================================================
# FILE UPLOAD CONFIGURATION
# =========================================================
ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg", "pdf"]
MAX_FILE_SIZE_MB = 10

# =========================================================
# IMAGE PROCESSING CONFIGURATION
# =========================================================
IMAGE_DPI = 300
GRAYSCALE = True

# =========================================================
# ANALYTICS CONFIGURATION
# =========================================================
CURRENCY_SYMBOL = "₹"

def is_windows():
    return os.name == "nt"
