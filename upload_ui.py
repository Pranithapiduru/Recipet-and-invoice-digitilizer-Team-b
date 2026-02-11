import streamlit as st  # type: ignore
from PIL import Image  # type: ignore
import pytesseract  # type: ignore
import pandas as pd  # type: ignore

from ocr.text_parser import parse_receipt  # type: ignore
from ui.validation_ui import validate_receipt  # type: ignore
from database.queries import save_receipt, receipt_exists  # type: ignore
from config.translations import get_text  # type: ignore


def render_upload_ui():
    lang = st.session_state.get("language", "en")
    st.header(get_text(lang, "upload_receipt_header"))

    uploaded = st.file_uploader(
        get_text(lang, "upload_label"),
        type=["png", "jpg", "jpeg", "pdf"]
    )

    if not uploaded:
        st.info(get_text(lang, "upload_info"))
        return

    # ================= IMAGE PROCESSING =================
    if uploaded.type == "application/pdf":
        from ocr.pdf_processor import pdf_to_images
        with st.spinner(get_text(lang, "converting_pdf")):
            try:
                pdf_images = pdf_to_images(uploaded.read())
                if not pdf_images:
                    st.error(get_text(lang, "pdf_error"))
                    return
                img = pdf_images[0] # Take first page
            except Exception as e:
                st.error(f"PDF Processing Error: {e}")
                st.info("Ensure Poppler is installed and path is correct in `ocr/pdf_processor.py`.")
                return
    else:
        img = Image.open(uploaded)

    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption=get_text(lang, "original_image"), use_container_width=True)

    with col2:
        gray = img.convert("L")
        st.image(gray, caption=get_text(lang, "processed_image"), use_container_width=True)

    st.divider()

    # ================= OCR + PARSE =================
    if not st.button(get_text(lang, "extract_save_btn"), use_container_width=True):
        return

    data = None
    items = []
    
    api_key = st.session_state.get("GEMINI_API_KEY")
    use_ai = bool(api_key)

    with st.spinner(get_text(lang, "extracting_data")):
        if use_ai:
            from ai.gemini_client import GeminiClient
            try:
                client = GeminiClient(api_key)
                # Gemini takes PIL image directly
                result = client.extract_receipt(img)
                if result:
                    items = result.pop("items", [])
                    data = result
                    st.success(get_text(lang, "ai_success"))
            except Exception as e:
                st.error(f"AI Extraction failed: {e}. Falling back to OCR.")
                use_ai = False

        if not data:
            # Fallback to Tesseract
            import numpy as np
            import cv2
            # Use image_preprocessing if available
            from ocr.image_preprocessing import preprocess_image
            gray_preprocessed = preprocess_image(img)
            text = pytesseract.image_to_string(gray_preprocessed)
            if not text.strip():
                st.error(get_text(lang, "no_text_error"))
                return
            data, items = parse_receipt(text)

    st.session_state["LAST_EXTRACTED_RECEIPT"] = data

    # ================= RECEIPT SUMMARY (HORIZONTAL TABLE) =================
    st.subheader(get_text(lang, "receipt_summary"))

    summary_df = pd.DataFrame([{
        get_text(lang, "bill_id"): data["bill_id"],
        get_text(lang, "vendor"): data["vendor"],
        get_text(lang, "category"): data.get("category", "Uncategorized"),
        get_text(lang, "date"): data["date"],
        get_text(lang, "subtotal_inr"): round(data.get("subtotal", 0.0), 2),
        get_text(lang, "tax_inr"): round(data["tax"], 2),
        get_text(lang, "amount_inr"): round(data["amount"], 2),
    }])

    st.dataframe(summary_df, use_container_width=True)

    # ================= ITEM WISE EXTRACTION =================
    st.subheader(get_text(lang, "item_details"))

    if items and len(items) > 0:
        st.dataframe(items, use_container_width=True)
    else:
        st.info(get_text(lang, "no_item_details"))

    st.divider()

    # ================= DUPLICATE CHECK =================
    if receipt_exists(data["bill_id"]):
        st.error(get_text(lang, "duplicate_error"))
        return
    else:
        st.success(get_text(lang, "no_duplicate_success"))

    # ================= VALIDATION =================
    validation = validate_receipt(data)
    st.session_state["LAST_VALIDATION_REPORT"] = validation

    # ================= SAVE (EVEN IF VALIDATION FAILS) =================
    save_receipt(data)

    if validation["passed"]:
        st.success(get_text(lang, "validation_passed_save"))
    else:
        st.error(get_text(lang, "validation_failed"))
