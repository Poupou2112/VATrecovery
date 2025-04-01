
import requests

def get_receipts(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    url = "https://example.com/api/receipts"
    r = requests.get(url, headers=headers)
    return r.json()

def download_receipt(receipt_id, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://example.com/api/receipts/{receipt_id}/file"
    r = requests.get(url, headers=headers)
    with open(f"static/ticket_{receipt_id}.pdf", "wb") as f:
        f.write(r.content)
