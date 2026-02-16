from fastapi import FastAPI, HTTPException, Depends, Query
from typing import List, Optional
from pydantic import BaseModel
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.queries import fetch_all_receipts, search_receipts, get_receipt_by_id
from datetime import datetime
import uvicorn

app = FastAPI(
    title="Receipt Vault Analyzer API",
    description="REST API for ERP integration and external data access",
    version="1.0.0"
)

# --- Schemas ---
class ReceiptBase(BaseModel):
    bill_id: str
    vendor: str
    date: str
    amount: float
    tax: float
    subtotal: float
    category: str

class ERPExportResponse(BaseModel):
    erp_system: str
    sync_status: str
    sync_time: str
    exported_records: int
    payload_preview: dict

# --- Root ---
@app.get("/")
def read_root():
    return {"message": "Receipt Vault API is online", "docs": "/docs"}

# --- Endpoints ---

@app.get("/api/v1/receipts", response_model=List[ReceiptBase])
def get_receipts(
    vendor: Optional[str] = None,
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Fetch receipts for external systems (ERP)"""
    try:
        if any([vendor, category, start_date, end_date]):
            results = search_receipts(vendor=vendor, category=category, start_date=start_date, end_date=end_date)
        else:
            results = fetch_all_receipts()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/receipts/{bill_id}", response_model=ReceiptBase)
def get_receipt(bill_id: str):
    """Focus on single record for detailed ERP mapping"""
    receipt = get_receipt_by_id(bill_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return receipt

@app.post("/api/v1/erp/sync", response_model=ERPExportResponse)
def sync_to_erp(system: str = "SAP"):
    """
    Simulated ERP Synchronization Endpoint.
    Formats data for common ERP schemas (SAP, Oracle, NetSuite).
    """
    receipts = fetch_all_receipts()
    
    # Simulate mapping to ERP JSON structure
    if system == "ERPNext":
        erp_payload = {
            "doctype": "Purchase Invoice",
            "supplier": receipts[0]["vendor"] if receipts else "N/A",
            "posting_date": receipts[0]["date"] if receipts else "N/A",
            "apply_tds": 0,
            "items": [
                {
                    "item_code": "Generic Expense",
                    "qty": 1,
                    "rate": r["amount"],
                    "amount": r["amount"],
                    "description": f"Receipt {r['bill_id']} from {r['vendor']}"
                } for r in receipts[:5]
            ]
        }
    else:
        erp_payload = {
            "Header": {
                "System": system,
                "TransferID": f"TXN-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "Organization": "ReceiptVault-Client"
            },
            "Invoices": [
                {
                    "ExternalInvID": r["bill_id"],
                    "Supplier": r["vendor"],
                    "PostingDate": r["date"],
                    "GrossAmount": r["amount"],
                    "TaxAmount": r["tax"],
                    "Currency": "INR"
                } for r in receipts[:5] # Sample first 5
            ]
        }
    
    return {
        "erp_system": system,
        "sync_status": "SUCCESS",
        "sync_time": datetime.now().isoformat(),
        "exported_records": len(receipts),
        "payload_preview": erp_payload
    }

@app.post("/api/v1/ocr/process")
async def process_image(file_url: str):
    """
    Experimental: Process image from URL via API.
    In production, this would handle multipart/form-data.
    """
    # Logic to fetch and process image using existing parse_receipt
    return {"status": "WIP", "message": "File upload endpoint designed. Ready for multipart implementation."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
