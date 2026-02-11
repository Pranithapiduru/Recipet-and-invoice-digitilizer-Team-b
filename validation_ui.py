from typing import Any, Dict  # type: ignore
import streamlit as st  # type: ignore
from datetime import datetime  # type: ignore
from database.queries import fetch_all_receipts, receipt_exists  # type: ignore
from config.translations import get_text # type: ignore
import pandas as pd # type: ignore

EXPECTED_TAX_RATE = 0.08   # 8%
TOLERANCE = 0.05           # 5% tolerance


def validate_receipt(data: dict, skip_duplicate: bool = False) -> dict:
    results = []
    passed = True

    # ---------- Required Fields ----------
    required = ["bill_id", "vendor", "date", "amount", "tax"]
    missing = [f for f in required if data.get(f) is None]

    if missing:
        results.append({
            "status": "error",
            "title": "Required Fields",
            "message": f"Missing fields: {', '.join(missing)}"
        })
        passed = False
        return {
            "passed": passed,
            "results": results
        }
    else:
        results.append({
            "status": "success",
            "title": "Required Fields",
            "message": "All required fields present"
        })

    # ---------- Date Format ----------
    date_val = data.get("date")
    try:
        datetime.strptime(str(date_val), "%Y-%m-%d")
        results.append({
            "status": "success",
            "title": "Date Format",
            "message": f"Valid date: {date_val}"
        })
    except Exception:
        results.append({
            "status": "error",
            "title": "Date Format",
            "message": f"Invalid date format: {date_val}"
        })
        passed = False

    # ---------- Amount & Tax Validation ----------
    try:
        amount_val = data.get("amount")
        amount = float(amount_val) if amount_val is not None else 0.0
    except (ValueError, TypeError):
        amount = 0.0
        
    try:
        tax_val = data.get("tax")
        tax = float(tax_val) if tax_val is not None else 0.0
    except (ValueError, TypeError):
        tax = 0.0

    # ---------- Total Validation ----------
    if amount > 0:
        results.append({
            "status": "success",
            "title": "Total Amount",
            "message": f"Amount ₹{amount:.2f} is valid"
        })
    else:
        results.append({
            "status": "error",
            "title": "Total Amount",
            "message": "Invalid amount value"
        })
        passed = False

    # ---------- Tax Rate Validation ----------
    if tax == 0.0:
        results.append({
            "status": "success",
            "title": "Tax Rate",
            "message": "No tax applied"
        })
    else:
        subtotal_option_1 = float(amount - tax)
        subtotal_option_2 = float(amount)

        valid = False
        used_subtotal = 0.0
        actual_rate = 0.0

        for subtotal in [subtotal_option_1, subtotal_option_2]:
            subtotal = float(subtotal)
            if subtotal <= 0:
                continue
            
            try:
                rate = float(tax) / subtotal
            except ZeroDivisionError:
                continue

            if abs(rate - EXPECTED_TAX_RATE) <= TOLERANCE:
                valid = True
                used_subtotal = subtotal
                actual_rate = rate
                break

        if valid:
            results.append({
                "status": "success",
                "title": "Tax Rate",
                "message": (
                    f"Tax rate OK "
                    f"({actual_rate*100:.2f}%, Subtotal ₹{used_subtotal:.2f})"
                )
            })
        else:
            results.append({
                "status": "error",
                "title": "Tax Rate",
                "message": (
                    f"Tax mismatch. Expected ~{EXPECTED_TAX_RATE*100:.1f}% "
                    f"but got ₹{tax:.2f} on amount ₹{amount:.2f}"
                )
            })
            passed = False

    # ---------- Duplicate Detection ----------
    if not skip_duplicate:
        if receipt_exists(data.get("bill_id")):
            results.append({
                "status": "error",
                "title": "Duplicate Detection",
                "message": "Duplicate receipt found in database"
            })
            passed = False
        else:
            results.append({
                "status": "success",
                "title": "Duplicate Detection",
                "message": "No duplicate found"
            })
    else:
        results.append({
            "status": "success",
            "title": "Duplicate Detection",
            "message": "Duplicate check skipped"
        })

    return {
        "passed": passed,
        "results": results
    }



def validation_ui():
    st.header("🧾 Receipt Validation")

    # ================= CURRENT UPLOADED RECEIPT =================
    data = st.session_state.get("LAST_EXTRACTED_RECEIPT")
    report = st.session_state.get("LAST_VALIDATION_REPORT")

    if data and report:
        st.subheader("🎯 Current Uploaded Receipt")

        for r in report["results"]:
            if r["status"] == "success":
                st.success(f"✅ **{r['title']}**\n\n{r['message']}")
            else:
                st.error(f"❌ **{r['title']}**\n\n{r['message']}")

        if report["passed"]:
            st.success("🎉 Receipt passed validation")
        else:
            st.error("❌ Receipt failed validation")
    else:
        st.info("No receipt uploaded yet")

    st.divider()

    # ================= STORED RECEIPT VALIDATION =================
    st.subheader("🔍 Validate Stored Receipt")

    c1, c2, c3, c4 = st.columns(4)
    bill_id = c1.text_input("Bill ID")
    vendor = c2.text_input("Vendor")
    amount_input = c3.text_input("Amount")
    tax_input = c4.text_input("Tax")

    if st.button("Run Validation", use_container_width=True):
        receipts = fetch_all_receipts()
        match: dict[str, Any] | None = None

        for r_raw in receipts:
            r: Dict[str, Any] = r_raw
            r_bill_id = str(r.get("bill_id", ""))
            r_vendor = str(r.get("vendor", ""))
            r_amount = float(r.get("amount", 0.0))
            r_tax = float(r.get("tax", 0.0))

            if bill_id and bill_id not in r_bill_id:
                continue
            if vendor and vendor.lower() not in r_vendor.lower():
                continue
            if amount_input:
                try:
                    if float(amount_input) != r_amount:
                        continue
                except ValueError:
                    pass
            if tax_input:
                try:
                    if float(tax_input) != r_tax:
                        continue
                except ValueError:
                    pass

            match = r
            break

        if match is None:
            st.error("No matching stored receipt found")
            return

        # Explicitly declare match as dict for type checker
        match_data: dict[str, Any] = match # type: ignore
        stored_report = validate_receipt(match_data, skip_duplicate=True)

        st.subheader(f"🧪 Validation for {match_data.get('bill_id', 'Unknown')}")

        for r in stored_report["results"]:
            if r["status"] == "success":
                st.success(f"✅ **{r['title']}**\n\n{r['message']}")
            else:
                st.error(f"❌ **{r['title']}**\n\n{r['message']}")

        if stored_report["passed"]:
            st.success("🎉 Stored receipt passed validation")
        else:
            st.error("❌ Stored receipt failed validation")
