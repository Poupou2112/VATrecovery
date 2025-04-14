from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import subprocess
from loguru import logger

def run_reminder_script() -> None:
    """Run the invoice reminder script as a subprocess"""
    logger.info(f"⏰ Starting reminder job: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        subprocess.run(["python", "app/reminder.py"], check=True)
        logger.info("✅ Reminder script executed successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Error executing reminder script: {e}")

def start_scheduler() -> BackgroundScheduler:
    """Initialize and start the background scheduler for reminders"""
    scheduler = BackgroundScheduler(timezone="Europe/Madrid")
    # Run every day at 9:00 AM
    scheduler.add_job(run_reminder_script, 'cron', hour=9, minute=0)
    scheduler.start()
    logger.info("✅ Scheduler started (reminder every day at 9:00 AM)")
    return scheduler
