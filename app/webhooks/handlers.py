from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/webhooks/task-status")
async def task_status_webhook(request: Request):
    data = await request.json()
    # Ajoute ici du traitement personnalisé ou journalisation
    return {"status": "received"}
