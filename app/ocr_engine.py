import re
from datetime import datetime

def extract_info_from_text(text: str) -> dict:
    data = {}

    # Company name: first uppercase line
    for line in text.split("\n"):
        line = line.strip()
        if line.isupper() and len(line) > 2:
            data["company_name"] = line
            break

    # VAT number (FR intracom)
    match = re.search(r'(FR\s?\d{2}\s?\d{9})', text)
    if match:
        data["vat_number"] = match.group(1)

    # TTC (Total amount including tax)
    match = re.search(r'TTC\s*[:\-]?\s*(\d+[\.,]\d+)', text, re.IGNORECASE)
    if match:
        data["price_ttc"] = float(match.group(1).replace(",", "."))

    # Date
    match = re.search(r'(\d{2}/\d{2}/\d{4})', text)
    if match:
        try:
            datetime.strptime(match.group(1), "%d/%m/%Y")
            data["date"] = match.group(1)
        except ValueError:
            pass

    return data

