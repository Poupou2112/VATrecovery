# app/ocr_engine.py

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

    # Date (format français ou ISO)
    match = re.search(r"(\d{2}/\d{2}/\d{4})", text)
    if match:
        data["date"] = match.group(1)
    else:
        match = re.search(r"(\d{4}-\d{2}-\d{2})", text)
        if match:
            date = datetime.strptime(match.group(1), "%Y-%m-%d")
            data["date"] = date.strftime("%d/%m/%Y")

    # TVA
    match = re.search(r"TVA\s*[:=]?\s*(\d+[.,]\d+)", text, re.IGNORECASE)
    if match:
        data["vat_amount"] = float(match.group(1).replace(",", "."))

    # TTC
    match = re.search(r"TTC\s*[:=]?\s*(\d+[.,]\d+)", text, re.IGNORECASE)
    if match:
        data["price_ttc"] = float(match.group(1).replace(",", "."))

    # HT
    match = re.search(r"HT\s*[:=]?\s*(\d+[.,]\d+)", text, re.IGNORECASE)
    if match:
        data["price_ht"] = float(match.group(1).replace(",", "."))

    return data
