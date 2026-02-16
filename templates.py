import re
from dataclasses import dataclass
from typing import List, Optional, Pattern

@dataclass
class ReceiptTemplate:
    """
    Defines a regex-based template for a specific vendor layout.
    """
    name: str
    vendor_pattern: str  # Regex to identify this vendor (e.g. "Walmart")
    date_pattern: Optional[str] = None
    total_pattern: Optional[str] = None
    tax_pattern: Optional[str] = None
    bill_id_pattern: Optional[str] = None
    line_item_pattern: Optional[str] = None

# Define common templates
TEMPLATES: List[ReceiptTemplate] = [
    ReceiptTemplate(
        name="Walmart",
        vendor_pattern=r"(?i)walmart",
        date_pattern=r"(\d{2}/\d{2}/\d{2,4})",  # MM/DD/YY
        total_pattern=r"(?i)\btotal\s+due\s+\$?\s*(\d+\.\d{2})",
        tax_pattern=r"(?i)tax\s+\d+\s*\$?\s*(\d+\.\d{2})",
        bill_id_pattern=r"(?i)tc#\s*(\d+)"
    ),
    ReceiptTemplate(
        name="Target",
        vendor_pattern=r"(?i)target",
        date_pattern=r"(\d{2}/\d{2}/\d{4})",
        total_pattern=r"(?i)\btotal\s+\$?\s*(\d+\.\d{2})",
        bill_id_pattern=r"(?i)receipt#\s*([a-zA-Z0-9-]+)"
    ),
    ReceiptTemplate(
        name="Costco",
        vendor_pattern=r"(?i)costco",
        date_pattern=r"(\d{2}/\d{2}/\d{4})",
        total_pattern=r"(?i)total\s+owned\s+\$?\s*(\d+\.\d{2})",
    ),
    ReceiptTemplate(
        name="Amazon",
        vendor_pattern=r"(?i)amazon",
        date_pattern=r"(?i)shipped on\s+(\w+\s+\d{1,2},\s+\d{4})",
        total_pattern=r"(?i)grand total:\s*\$?\s*(\d+\.\d{2})",
        bill_id_pattern=r"(?i)order #\s*([0-9-]{10,})",
    ),
    # Generic fallback templates if needed
]


def get_matching_template(text: str) -> Optional[ReceiptTemplate]:
    """Finds the first template that matches the vendor pattern in the text."""
    for tmpl in TEMPLATES:
        if re.search(tmpl.vendor_pattern, text):
            return tmpl
    return None
