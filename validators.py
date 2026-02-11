from config.config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB

def validate_uploaded_file(uploaded_file):
    if uploaded_file is None:
        raise ValueError("No file uploaded")

    ext = uploaded_file.name.split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("Invalid file type")

    if uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise ValueError("File size exceeded")

def calculate_items_total(items):
    return sum(i["quantity"] * i["price"] for i in items)

def validate_total(extracted_total, calculated_total, tolerance=2.0):
    if extracted_total is None:
        return False
    return abs(extracted_total - calculated_total) <= tolerance

def detect_duplicate(df, merchant, date, total):
    if df.empty:
        return False

    return not df[
        (df["merchant"] == merchant) &
        (df["date"] == date) &
        (df["total"] == total)
    ].empty
