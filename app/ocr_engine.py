import re
from google.cloud import vision

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
        data["vat_number"] = match.group(1).replace(" ", "")

    # SIREN (9-digit French company number)
    match = re.search(r'\b(\d{3}[\s\-]?\d{3}[\s\-]?\d{3})\b', text)
    if match:
        data["siren"] = match.group(1).replace(" ", "").replace("-", "")

    # Address + zipcode
    match = re.search(r'(\d{1,4}\s+\w.+?)[,\n\s]+(\d{5})\b', text)
    if match:
        data["address"] = match.group(1).strip()
        data["zipcode"] = match.group(2)

    # Phone number (French formats)
    match = re.search(r'((?:\+33\s?|0)[1-9](?:[\s.-]?\d{2}){4})', text)
    if match:
        data["phone"] = match.group(1).replace(" ", "").replace(".", "").replace("-", "")

    # Date (format DD/MM/YYYY)
    match = re.search(r'(\d{2}/\d{2}/\d{4})', text)
    if match:
        data["date"] = match.group(1)

    # Price TTC
    match = re.search(r'TTC\s*[:\-]?\s*([\d,\.]+)', text, re.IGNORECASE)
    if match:
        data["price_ttc"] = float(match.group(1).replace(",", "."))

    # Price HT
    match = re.search(r'HT\s*[:\-]?\s*([\d,\.]+)', text, re.IGNORECASE)
    if match:
        data["price_ht"] = float(match.group(1).replace(",", "."))

    # VAT amount
    match = re.search(r'TVA\s*[:\-]?\s*([\d,\.]+)', text, re.IGNORECASE)
    if match:
        data["vat"] = float(match.group(1).replace(",", "."))

    return data


def analyze_ticket(ticket_path: str) -> dict:
    """
    Given the path to an image or PDF receipt, extract structured data.
    """
    client = vision.ImageAnnotatorClient()

    with open(ticket_path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    
    if response.error.message:
        raise Exception(f"Google Vision OCR Error: {response.error.message}")

    full_text = response.full_text_annotation.text
    return extract_info_from_text(full_text)
