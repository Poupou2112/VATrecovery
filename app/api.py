from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from app.models import Receipt
from app.schemas import SendInvoiceRequest
from app.init_db import get_db_session
from app.email_sender import send_email
from app.queue.redis_queue import RedisQueue
from datetime import datetime
import csv
import io
import os

router = APIRouter()

@router.get("/receipts/filter")
def filter_receipts(
    client_id: int = Query(...),
    invoice_received: bool = Query(None),
    email_sent: bool = Query(None),
    db: Session = Depends(get_db_session)
):
    query = db.query(Receipt).filter(Receipt.client_id == client_id)
    
    if invoice_received is not None:
        query = query.filter(Receipt.invoice_received == invoice_received)
    if email_sent is not None:
        query = query.filter(Receipt.email_sent == email_sent)
        
    results = query.all()
    return results


@router.post("/send-invoice-request")
def send_invoice_request(request_data: SendInvoiceRequest, db: Session = Depends(get_db_session)):
    receipt = db.query(Receipt).filter_by(id=request_data.ticket_id).first()
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    
    subject = "Request for Invoice"
    body = f"Bonjour, pourriez-vous nous envoyer une facture pour le reçu suivant : {receipt.file} ? Merci."
    
    try:
        send_email(to=request_data.email, subject=subject, body=body)
        receipt.email_sent = True
        db.commit()
        return {"message": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/csv")
def export_csv(
    client_id: int = Query(...),
    db: Session = Depends(get_db_session)
):
    receipts = db.query(Receipt).filter(Receipt.client_id == client_id).all()

    if not receipts:
        raise HTTPException(status_code=404, detail="No receipts found.")

    def generate():
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["ID", "File", "Company Name", "Date", "TTC", "Invoice Received", "Email Sent"])
        for r in receipts:
            writer.writerow([
                r.id,
                r.file,
                r.company_name or "",
                r.date or "",
                r.price_ttc or "",
                r.invoice_received,
                r.email_sent
            ])
        buffer.seek(0)
        yield buffer.read()

    return StreamingResponse(generate(), media_type="text/csv")


@router.post("/api/webhooks/task-status")
def handle_task_status(request: Request):
    payload = request.json()
    # Tu pourrais persister cette info en base ou logger
    return {"received": True, "payload": payload}
