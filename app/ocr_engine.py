import re

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

    # Date (française ou ISO)
    match = re.search(r'(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})', text)
    if match:
        data["date"] = match.group(1)

    # TTC
    match = re.search(r'TTC\s?:?\s?(\d+,\d{2})', text)
    if match:
        data["price_ttc"] = float(match.group(1).replace(",", "."))

    # HT
    match = re.search(r'HT\s?:?\s?(\d+,\d{2})', text)
    if match:
        data["price_ht"] = float(match.group(1).replace(",", "."))

    # TVA
    match = re.search(r'TVA\s?:?\s?(\d+,\d{2})', text)
    if match:
        data["vat"] = float(match.group(1).replace(",", "."))

    return data
