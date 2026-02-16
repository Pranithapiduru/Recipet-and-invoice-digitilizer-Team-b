from database.db import get_db
from typing import List, Dict, Any, Optional

# ================= SAVE RECEIPT =================
def save_receipt(data):
    """
    Save receipt to database.
    Assumes data = {
        bill_id, vendor, date, amount, tax, subtotal
    }
    """
    db = get_db()
    
    # Ensure subtotal/category exist
    if "subtotal" not in data:
        data["subtotal"] = 0.0
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


# ================= DUPLICATE CHECK (ROBUST) =================
def check_receipt_duplicate(bill_id, vendor, date, amount):
    """
    Check for duplicates with high reliability (>=95%).
    Checks:
    1. Exact Bill ID match (if valid)
    2. Combination of Vendor + Date + Amount (fallback)
    """
    db = get_db()
    
    # 1. Check Bill ID if it exists and looks valid (not temp/default)
    if bill_id and len(bill_id) > 2 and "REC-" not in bill_id:
        cur = db.execute("SELECT 1 FROM receipts WHERE bill_id = ?", (bill_id,))
        if cur.fetchone():
            return True

    # 2. Check Logic Fingerprint (Vendor + Date + Amount)
    # This catches duplicates where OCR missed the specific Bill ID char but data is same
    try:
        cur = db.execute(
            "SELECT 1 FROM receipts WHERE vendor = ? AND date = ? AND abs(amount - ?) < 0.01",
            (vendor, date, float(amount))
        )
        if cur.fetchone():
            return True
    except:
        pass
        
    return False


def receipt_exists(bill_id):
    """Legacy wrapper for backward compatibility"""
    db = get_db()
    cur = db.execute("SELECT 1 FROM receipts WHERE bill_id = ?", (bill_id,))
    return cur.fetchone() is not None


# ================= FETCH ALL RECEIPTS =================
def fetch_all_receipts() -> List[Dict[str, Any]]:
    """
    Returns list of dicts ordered by date DESC
    """
    db = get_db()
    
    try:
        cur = db.execute(
            "SELECT bill_id, vendor, date, amount, tax, subtotal, category FROM receipts ORDER BY date DESC"
        )
    except:
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


# ================= GET ONE RECEIPT =================
def get_receipt_by_id(bill_id: str) -> Optional[Dict[str, Any]]:
    """Returns a single receipt as a dict or None"""
    db = get_db()
    cur = db.execute(
        "SELECT * FROM receipts WHERE bill_id = ?",
        (bill_id,)
    )
    row = cur.fetchone()
    if row:
        return {
            "bill_id": row["bill_id"],
            "vendor": row["vendor"],
            "date": row["date"],
            "amount": float(row["amount"]),
            "tax": float(row["tax"]),
            "subtotal": float(row["subtotal"]) if ("subtotal" in row.keys() and row["subtotal"] is not None) else 0.0,
            "category": row["category"] if ("category" in row.keys() and row["category"]) else "Uncategorized",
        }
    return None


# ================= UPDATE RECEIPT =================
def update_receipt(bill_id: str, update_data: Dict[str, Any]) -> bool:
    """Updates specific fields for a receipt"""
    db = get_db()
    
    fields = []
    values = []
    
    for key, value in update_data.items():
        if value is not None:
            fields.append(f"{key} = ?")
            values.append(value)
    
    if not fields:
        return False
    
    values.append(bill_id)
    query = f"UPDATE receipts SET {', '.join(fields)} WHERE bill_id = ?"
    
    db.execute(query, values)
    db.commit()
    return True


# ================= SEARCH RECEIPTS (OPTIMIZED) =================
def search_receipts(
    vendor: Optional[str] = None,
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None
) -> List[Dict[str, Any]]:
    """
    Search receipts with dynamic SQL filtering (Server-side optimization).
    Uses indexed columns for better performance.
    """
    db = get_db()
    
    query = "SELECT * FROM receipts WHERE 1=1"
    params: List[Any] = []
    
    if vendor:
        query += " AND vendor LIKE ?"
        params.append(f"%{vendor}%")
    
    if category and category != "All":
        query += " AND category = ?"
        params.append(category)
    
    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)
    
    if min_amount is not None:
        query += " AND amount >= ?"
        params.append(min_amount)
    
    if max_amount is not None:
        query += " AND amount <= ?"
        params.append(max_amount)
    
    query += " ORDER BY date DESC"
    
    cur = db.execute(query, params)
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
    db.execute("DELETE FROM sqlite_sequence WHERE name='receipts'")
    db.commit()