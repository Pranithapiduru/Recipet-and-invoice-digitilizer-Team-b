from database.db import get_db


# ================= SAVE RECEIPT =================
def save_receipt(data):
    """
    Save receipt to database.
    Assumes data = {
        bill_id, vendor, date, amount, tax, subtotal
    }
    """
    db = get_db()
    
    # Ensure subtotal exists
    if "subtotal" not in data:
        data["subtotal"] = 0.0
    
    # Ensure category exists
    if "category" not in data:
        data["category"] = "Uncategorized"

    db.execute(
        """
        INSERT INTO receipts (bill_id, vendor, date, amount, tax, subtotal, category)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["bill_id"],
            data["vendor"],
            data["date"],
            float(data["amount"]),
            float(data["tax"]),
            float(data["subtotal"]),
            data["category"],
        ),
    )
    db.commit()


# ================= DUPLICATE CHECK =================
def receipt_exists(bill_id):
    db = get_db()
    cur = db.execute(
        "SELECT 1 FROM receipts WHERE bill_id = ?",
        (bill_id,)
    )
    return cur.fetchone() is not None


# ================= FETCH ALL RECEIPTS =================
from typing import List, Dict, Any

def fetch_all_receipts() -> List[Dict[str, Any]]:
    """
    Returns list of dicts:
    [
        {bill_id, vendor, date, amount, tax, subtotal},
        ...
    ]
    """
    db = get_db()
    
    # Handle case where subtotal/category might be missing in older schemas (though init_db fixes it)
    try:
        cur = db.execute(
            "SELECT bill_id, vendor, date, amount, tax, subtotal, category FROM receipts ORDER BY date DESC"
        )
    except:
        # Fallback for code running before migration (unlikely but safe)
        cur = db.execute(
            "SELECT bill_id, vendor, date, amount, tax, 0.0 as subtotal, 'Uncategorized' as category FROM receipts ORDER BY date DESC"
        )

    rows = cur.fetchall()

    return [
        {
            "bill_id": r["bill_id"],
            "vendor": r["vendor"],
            "date": r["date"],
            "amount": float(r["amount"]),
            "tax": float(r["tax"]),
            "subtotal": float(r["subtotal"]) if ("subtotal" in r.keys() and r["subtotal"] is not None) else 0.0,
            "category": r["category"] if ("category" in r.keys() and r["category"]) else "Uncategorized",
        }
        for r in rows
    ]


# ================= DELETE ONE RECEIPT =================
def delete_receipt(bill_id):
    db = get_db()
    db.execute(
        "DELETE FROM receipts WHERE bill_id = ?",
        (bill_id,)
    )
    db.commit()


# ================= CLEAR ALL RECEIPTS =================
def clear_all_receipts():
    db = get_db()
    db.execute("DELETE FROM receipts")
    db.commit()
