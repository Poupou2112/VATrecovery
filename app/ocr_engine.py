import os
import re
import json
import smtplib
from email.message import EmailMessage
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

    # SIREN
    match = re.search(r'\b(\d{3}[\s\-]?\d{3}[\s\-]?\d{3})\b', text)
    if match:
        data["siren"] = match.group(1).replace(" ", "").replace("-", "")

    # Address + zipcode
    match = re.search(r'(\d{1,4}\s+\w.+?)[,\n\s]+(\d{5})\b', text)
    if match:
        data["address"] = match.group(1).strip()
        data["zipcode"] = match.group(2)

    # Phone
    match = re.search(r'((?:\+33\s?|0)[1-9](?:[\s.-]?\d{2}){4})', text)
    if match:
        data["phone"] = match.group(1).replace(" ", "").replace(".", "").replace("-", "")

    # Date
    match = re.search(r'(\d{2}/\d{2}/\d{4})', text)
    if match:
        data["date"] = match.group(1)

    # TTC
    match = re.search(r'TTC\s*[:\-]?\s*([\d,\.]+)', text, re.IGNORECASE)
    if match:
        data["price_ttc"] = float(match.group(1).replace(",", "."))

    # HT
    match = re.search(r'HT\s*[:\-]?\s*([\d,\.]+)', text, re.IGNORECASE)
    if match:
        data["price_ht"] = float(match.group(1).replace(",", "."))

    # TVA
    match = re.search(r'TVA\s*[:\-]?\s*([\d,\.]+)', text, re.IGNORECASE)
    if match:
        data["vat"] = float(match.group(1).replace(",", "."))

    return data

def analyze_ticket(ticket_path: str) -> dict:
    client = vision.ImageAnnotatorClient()

    with open(ticket_path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)

    if response.error.message:
        raise Exception(f"Google Vision OCR Error: {response.error.message}")

    full_text = response.full_text_annotation.text
    data = extract_info_from_text(full_text)

    # Export JSON (optional)
    json_path = ticket_path.replace(".jpg", ".json").replace(".png", ".json")
    with open(json_path, "w") as f:
        json.dump(data, f, indent=4)

    return data

def send_email(to_email: str, ticket_data: dict, ticket_path: str):
    msg = EmailMessage()
    msg["Subject"] = "Demande de facture pour note de frais"
    msg["From"] = os.getenv("SMTP_FROM")
    msg["To"] = to_email

    body = f"""
Bonjour,

Je vous écris pour vous demander une **facture** correspondant au reçu suivant :

- Date : {ticket_data.get('date', 'non reconnue')}
- Montant TTC : {ticket_data.get('price_ttc', 'non reconnu')} EUR
- Raison sociale détectée : {ticket_data.get('company_name', 'non reconnue')}

Merci de bien vouloir nous faire parvenir une facture conforme à : [ton adresse email].

Bien cordialement,

Reclaimy
"""
    msg.set_content(body)

    with open(ticket_path, "rb") as f:
        file_data = f.read()
        filename = os.path.basename(ticket_path)
        msg.add_attachment(file_data, maintype="image", subtype="jpeg", filename=filename)

    with smtplib.SMTP_SSL(os.getenv("SMTP_HOST"), int(os.getenv("SMTP_PORT"))) as smtp:
        smtp.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASS"))
        smtp.send_message(msg)

# Exemple d'usage (à faire dans un autre script)
if __name__ == "__main__":
    ticket_path = "app/static/test_ticket.jpg"
    to_email = "contact@societe.fr"

    data = analyze_ticket(ticket_path)
    send_email(to_email, data, ticket_path)
    print("✅ Ticket analysé et email envoyé.")
