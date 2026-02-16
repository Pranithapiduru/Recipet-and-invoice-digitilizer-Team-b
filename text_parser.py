import re
from datetime import datetime
import random


# ---------- HELPERS ----------

def _clean_amount(val):
    try:
        # Handle cases where OCR might have read "," as "." or vice versa
        # but usually we just want to strip commas
        clean_val = val.replace(",", "")
        return float(clean_val)
    except Exception:
        return 0.0


def _round2(val):
    """
    Round to 2 decimal places using math to satisfy strict linters.
    """
    return int(val * 100 + 0.5) / 100.0


def _default_bill_id():
    return f"BILL-{random.randint(100000, 999999)}"


def _extract_date(text):
    """
    NLP-style date extraction (multiple formats)
    """
    patterns = [
        r"\b(\d{4}-\d{2}-\d{2})\b",          # 2024-01-27
        r"\b(\d{2}/\d{2}/\d{4})\b",          # 27/01/2024
        r"\b(\d{2}-\d{2}-\d{4})\b",          # 27-01-2024
    ]

    for p in patterns:
        m = re.search(p, text)
        if m:
            raw = m.group(1)
            try:
                if "-" in raw and raw.count("-") == 2:
                    return datetime.strptime(raw, "%Y-%m-%d").strftime("%Y-%m-%d")
                if "/" in raw:
                    return datetime.strptime(raw, "%d/%m/%Y").strftime("%Y-%m-%d")
            except Exception:
                pass

    # fallback → today
    return datetime.today().strftime("%Y-%m-%d")


from ocr.templates import get_matching_template

# ---------- MAIN PARSER ----------

def parse_receipt(text: str):
    """
    Returns structured data and item list from raw OCR text.
    First tries template-based parsing, then falls back to generic rules.
    """
    
    # Try template-based parsing first
    template = get_matching_template(text)
    template_data = {}
    
    if template:
        # Extract fields using template patterns
        if template.bill_id_pattern:
            m = re.search(template.bill_id_pattern, text)
            if m: template_data['bill_id'] = m.group(1)
            
        if template.date_pattern:
            m = re.search(template.date_pattern, text)
            if m: template_data['date'] = m.group(1) # Note: might need normalization
            
        if template.total_pattern:
            m = re.search(template.total_pattern, text)
            if m: template_data['amount'] = _clean_amount(m.group(1))

        if template.tax_pattern:
            m = re.search(template.tax_pattern, text)
            if m: template_data['tax'] = _clean_amount(m.group(1))

        template_data['vendor'] = template.name

    lines = [l.strip() for l in text.splitlines() if l.strip()]

    # ---------- BILL ID ----------
    bill_id = template_data.get('bill_id')
    if not bill_id:
        # Reordered and added word boundaries to prevent partial matches like 'action' from 'Transaction'
        bill_prefixes = r"(?:transaction|invoice|receipt|order|ticket|bill|inv|rec|txn|trans)"
        bill_patterns = [
            rf"(?i)\b{bill_prefixes}\b\s*(?:no|id|number|#)?\s*[:.-]?\s*([a-zA-Z0-9/-]+)",
            r"(?i)#\s*([a-zA-Z0-9/-]+)",
            r"(?i)\b(?:inv|rec|txn)\b\s*[:.-]?\s*([a-zA-Z0-9/-]+)"
        ]
        
        for l in lines:
            for p in bill_patterns:
                m = re.search(p, l)
                if m:
                    candidate = m.group(1)
                    if candidate and len(candidate) > 2 and not any(kw in candidate.lower() for kw in ['total', 'tax', 'date', 'amount', 'item']):
                        bill_id = candidate
                        break
            if bill_id:
                break

    if not bill_id:
        bill_id = _default_bill_id()

    # ---------- VENDOR ----------
    vendor = template_data.get('vendor')
    if not vendor:
        vendor = "Unknown Vendor"
        generic_headers = ["tax invoice", "cash receipt", "bill of supply", "estimate", "original", "trans"]
        
        # Using simple loop to avoid slice indexing lint errors
        for i, line_text in enumerate(lines):
            if i >= 3:
                break
            if line_text.lower().strip() not in generic_headers and len(line_text) > 3:
                vendor = line_text
                break

    # ---------- DATE ----------
    date = template_data.get('date')
    if not date:
        date = _extract_date(text)
    else:
        # Basic normalization for template dates
        try:
            # Try some common formats or just return as is if it looks okay
            if re.match(r"\d{4}-\d{2}-\d{2}", date):
                pass 
            elif "/" in date:
                parts = date.split("/")
                if len(parts) == 3:
                    if len(parts[2]) == 2: parts[2] = "20" + parts[2]
                    # Default: Assume MM/DD/YYYY structure for US templates
                    # parts[0]=MM, parts[1]=DD, parts[2]=YYYY
                    mm, dd, yyyy = parts[0], parts[1], parts[2]
                    
                    # If MM > 12, swap to DD/MM/YYYY
                    if int(mm) > 12:
                         mm, dd = dd, mm
                         
                    date = f"{yyyy}-{mm}-{dd}"
        except:
             date = _extract_date(text)

    # ---------- FINANCIALS ----------
    total = 0.0
    tax = 0.0
    subtotal = 0.0

    for l in lines:
        # TOTAL
        if template_data.get('amount'):
            total = template_data['amount']
        elif re.search(r"(?i)\b(total|tot|due|payable)\b", l):
            nums = re.findall(r"\d+[.,]?\d*", l)
            if nums:
                dotted = [n for n in nums if "." in n or "," in n]
                if dotted:
                    total = _clean_amount(dotted[-1])
                else:
                    if len(nums) >= 2 and len(nums[-1]) == 2:
                        total = _clean_amount(f"{nums[-2]}.{nums[-1]}")
                    else:
                        total = _clean_amount(nums[-1])
        
        # TAX
        if template_data.get('tax'):
             tax = template_data['tax']
        elif re.search(r"(?i)\b(tax|gst|vat|cgst|sgst)\b", l):
            if "invoice" not in l.lower():
                 nums = re.findall(r"\d+[.,]?\d*", l)
                 if nums:
                     current_tax = 0.0
                     dotted = [n for n in nums if "." in n or "," in n]
                     if dotted:
                         current_tax = _clean_amount(dotted[-1])
                     elif len(nums) >= 2 and len(nums[-1]) == 2:
                         current_tax = _clean_amount(f"{nums[-2]}.{nums[-1]}")
                     else:
                         current_tax = _clean_amount(nums[-1])
                     tax += current_tax

        # SUBTOTAL
        if re.search(r"(?i)\b(sub\s*total|sub\s*ttl|sub\s*tot|stot|net\s*amount|net\s*amt|taxable|sub)\b", l):
            nums = re.findall(r"\d+[.,]?\d*", l)
            if nums:
                dotted = [n for n in nums if "." in n or "," in n]
                if dotted:
                    subtotal = _clean_amount(dotted[-1])
                elif len(nums) >= 2 and len(nums[-1]) == 2:
                    subtotal = _clean_amount(f"{nums[-2]}.{nums[-1]}")
                else:
                    subtotal = _clean_amount(nums[-1])

    # Validation & Fallbacks
    if tax > total and total > 0:
        tax = 0.0

    if total == 0.0:
        nums = re.findall(r"\d+[.,]?\d*", text)
        if nums:
             dotted = [n for n in nums if "." in n]
             if dotted:
                 total = max(_clean_amount(n) for n in dotted)
             else:
                 total = max(_clean_amount(n) for n in nums)
            
    if subtotal == 0.0 and total > 0:
        subtotal = total - tax

    # ---------- ITEMS ----------
    items = []
    for l in lines:
        if re.search(r"\d+\s*x\s*\d+", l):
            continue
        if re.search(r"(?i)(total|subtotal|subttl|tax|vat|gst|change|cash|card|due)", l):
            continue

        m = re.match(r"(.+?)\s+(\d+[.,]?\d*)$", l)
        if m:
            name = m.group(1).strip()
            price = _clean_amount(m.group(2))
            if 0 < price < total and len(name) > 2:
                items.append({
                    "Item": name,
                    "Price": price
                })

    # ---------- CATEGORY DETECTION (Rule-based) ----------
    def _extract_category(text, vendor):
        text_lower = text.lower()
        vendor_lower = vendor.lower()
        
        keywords = {
            "Utility": ["power", "electricity", "water", "gas", "bescom", "tata power", "bill", "supply", "electric"],
            "Food": ["restaurant", "cafe", "kitchen", "hotel", "dining", "burger", "pizza", "swiggy", "zomato", "coffee", "tea", "bistro", "foods"],
            "Grocery": ["mart", "super market", "fresh", "store", "vegetable", "fruit", "market", "grocer", "kirana", "basket"],
            "Medical": ["pharmacy", "hospital", "clinic", "doctor", "dr.", "medplus", "apollo", "pharma", "health", "medical"],
            "Travel": ["fuel", "petrol", "diesel", "station", "pump", "uber", "ola", "rapido", "ride", "trip", "travel"],
            "Shopping": ["retail", "fashion", "clothing", "trends", "zudio", "apparel", "garment", "mall", "shoe", "footwear"],
            "Entertainment": ["movie", "cinema", "theatre", "show", "entertainment", "game", "fun"]
        }
        
        # Check vendor name first (higher priority)
        for cat, kw_list in keywords.items():
            if any(k in vendor_lower for k in kw_list):
                return cat
                
        # Check entire text
        for cat, kw_list in keywords.items():
            if any(k in text_lower for k in kw_list):
                return cat
                
        return "Uncategorized"

    category = _extract_category(text, vendor)

    # ---------- FINAL DATA ----------
    data = {
        "bill_id": bill_id,
        "vendor": vendor,
        "date": date,
        "amount": _round2(total),
        "tax": _round2(tax),
        "subtotal": _round2(subtotal),
        "category": category
    }

    return data, items