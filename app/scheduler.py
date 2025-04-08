from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import subprocess

def run_reminder_script():
    print(f"⏰ [Scheduler] Lancement de la relance - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    subprocess.run(["python", "app/reminder.py"])

def start_scheduler():
    scheduler = BackgroundScheduler(timezone="Europe/Madrid")
    scheduler.add_job(run_reminder_script, 'cron', hour=9, minute=0)
    scheduler.start()
    print("✅ Scheduler lancé (relance tous les jours à 9h)")
