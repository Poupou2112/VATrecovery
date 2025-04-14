from fastapi import APIRouter
from apscheduler.schedulers.background import BackgroundScheduler
from app.reminder import send_reminder
from loguru import logger

scheduler = BackgroundScheduler()

def run_reminder_script():
    logger.info("Scheduled job started: sending reminders.")
    try:
        send_reminder()
    except Exception as e:
        logger.error(f"Error during scheduled reminder: {e}")

def start_scheduler():
    scheduler.add_job(run_reminder_script, 'cron', hour=9, minute=0)
    scheduler.start()
    logger.info("Scheduler started")

# Ce router est nécessaire pour que `from app.scheduler import scheduler_router` fonctionne
scheduler_router = APIRouter()

@scheduler_router.get("/schedule/test")
def test_scheduler():
    return {"status": "Scheduler is available"}
