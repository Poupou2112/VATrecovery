from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.reminder import send_reminder
from app.database import SessionLocal
from app.logger_setup import logger
import os

scheduler = BackgroundScheduler()


def run_reminder_script():
    try:
        db = SessionLocal()
        count = send_reminder(db)
        logger.info(f"🔁 Scheduled reminder script sent {count} reminders")
    except Exception as e:
        logger.exception(f"❌ Failed to run scheduled reminder: {e}")
    finally:
        db.close()


def start_scheduler():
    if os.getenv("TESTING", "false").lower() == "true":
        logger.warning("⚠️ Scheduler disabled in test environment")
        return

    if scheduler.running:
        logger.info("ℹ️ Scheduler already running")
        return

    logger.info("🕒 Starting scheduler for daily reminder job")
    scheduler.add_job(
        run_reminder_script,
        CronTrigger(hour=9, minute=0),  # Tous les jours à 9h
        id="daily_reminder_job",
        replace_existing=True
    )
    scheduler.start()
