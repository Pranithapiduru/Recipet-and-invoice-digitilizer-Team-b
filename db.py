import sqlite3
from pathlib import Path

# ================= DATABASE FILE =================
DB_PATH = Path("receipts.db")


# ================= GET DB CONNECTION =================
def get_db():
    """
    Returns a SQLite connection with row_factory enabled
    so rows behave like dictionaries.
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


# ================= INITIALIZE DATABASE =================
def init_db():
    """
    Creates receipts table if it does not exist.
    Call this once at app startup.
    """
    db = get_db()

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS receipts (
            bill_id TEXT PRIMARY KEY,
            vendor TEXT NOT NULL,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            tax REAL NOT NULL,
            subtotal REAL DEFAULT 0.0,
            category TEXT DEFAULT 'Uncategorized'
        )
        """
    )
    
    # Migration: Add subtotal column if it doesn't exist
    try:
        db.execute("ALTER TABLE receipts ADD COLUMN subtotal REAL DEFAULT 0.0")
    except sqlite3.OperationalError:
        pass

    # Migration: Add category column if it doesn't exist
    try:
        db.execute("ALTER TABLE receipts ADD COLUMN category TEXT DEFAULT 'Uncategorized'")
    except sqlite3.OperationalError:
        pass

    db.commit()
